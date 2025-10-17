"""
Publishing Background Tasks

Celery tasks for scheduled post publishing and maintenance.
"""
from datetime import datetime, timedelta
from typing import Optional
from celery import Task
from sqlalchemy.orm import Session
import logging

from app.celery_app import celery_app
from app.db.database import SessionLocal
from app.models.scheduled_post import ScheduledPost
from app.models.social_account import SocialAccount
from app.models.published_post import PublishedPost
from app.core.encryption import decrypt_token
from app.services.publishing import (
    linkedin_publisher,
    twitter_publisher,
    meta_publisher
)

logger = logging.getLogger(__name__)


def get_publisher(platform: str):
    """Get the appropriate publisher for the platform."""
    publishers = {
        "linkedin": linkedin_publisher,
        "twitter": twitter_publisher,
        "meta": meta_publisher
    }
    return publishers.get(platform.lower())


class DatabaseTask(Task):
    """Base task with database session management."""
    _db: Optional[Session] = None
    
    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        """Close database connection after task completes."""
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(base=DatabaseTask, bind=True, max_retries=3, default_retry_delay=60)
async def publish_scheduled_post(self, scheduled_post_id: int) -> dict:
    """
    Publish a scheduled post at its scheduled time.
    
    Args:
        scheduled_post_id: ID of the scheduled post to publish
        
    Returns:
        Dict with success status and details
    """
    db = self.db
    
    try:
        # Get scheduled post
        scheduled_post = db.query(ScheduledPost).filter(
            ScheduledPost.id == scheduled_post_id
        ).first()
        
        if not scheduled_post:
            logger.error(f"Scheduled post {scheduled_post_id} not found")
            return {
                "success": False,
                "error": "Scheduled post not found",
                "scheduled_post_id": scheduled_post_id
            }
        
        # Check if already published or cancelled
        if scheduled_post.status in ["published", "cancelled"]:
            logger.warning(f"Scheduled post {scheduled_post_id} already {scheduled_post.status}")
            return {
                "success": False,
                "error": f"Post already {scheduled_post.status}",
                "scheduled_post_id": scheduled_post_id,
                "status": scheduled_post.status
            }
        
        # Update status to publishing
        scheduled_post.status = "publishing"
        db.commit()
        
        logger.info(
            f"Publishing scheduled post {scheduled_post_id}",
            extra={
                "event_type": "scheduled_post_publishing",
                "scheduled_post_id": scheduled_post_id,
                "platform": scheduled_post.platform
            }
        )
        
        # Get social account
        social_account = db.query(SocialAccount).filter(
            SocialAccount.id == scheduled_post.social_account_id
        ).first()
        
        if not social_account:
            raise ValueError(f"Social account {scheduled_post.social_account_id} not found")
        
        # Decrypt access token
        access_token = decrypt_token(social_account.access_token)
        
        # Get publisher
        publisher = get_publisher(scheduled_post.platform)
        if not publisher:
            raise ValueError(f"Unsupported platform: {scheduled_post.platform}")
        
        # Prepare platform parameters
        platform_params = scheduled_post.platform_params or {}
        
        # Add Meta-specific parameters
        if scheduled_post.platform.lower() == "meta":
            if not platform_params.get("platform_type"):
                platform_params["platform_type"] = "facebook"
            
            if platform_params["platform_type"] == "facebook" and social_account.page_id:
                platform_params["page_id"] = social_account.page_id
            elif platform_params["platform_type"] == "instagram" and social_account.instagram_account_id:
                platform_params["instagram_account_id"] = social_account.instagram_account_id
        
        # Publish!
        result = await publisher.publish(
            content=scheduled_post.content_text,
            access_token=access_token,
            **platform_params
        )
        
        if result.success:
            # Create published post record
            published_post = PublishedPost(
                business_id=scheduled_post.business_id,
                social_account_id=scheduled_post.social_account_id,
                content_text=scheduled_post.content_text,
                platform=scheduled_post.platform,
                platform_post_id=result.post_id,
                platform_post_url=result.url,
                status="published",
                published_at=result.published_at or datetime.utcnow()
            )
            db.add(published_post)
            db.flush()
            
            # Update scheduled post
            scheduled_post.status = "published"
            scheduled_post.published_post_id = published_post.id
            scheduled_post.platform_post_id = result.post_id
            scheduled_post.platform_post_url = result.url
            scheduled_post.published_at = datetime.utcnow()
            scheduled_post.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(
                f"Successfully published scheduled post {scheduled_post_id}",
                extra={
                    "event_type": "scheduled_post_published",
                    "scheduled_post_id": scheduled_post_id,
                    "platform": scheduled_post.platform,
                    "post_id": result.post_id,
                    "post_url": result.url
                }
            )
            
            return {
                "success": True,
                "scheduled_post_id": scheduled_post_id,
                "published_post_id": published_post.id,
                "platform": scheduled_post.platform,
                "post_id": result.post_id,
                "post_url": result.url
            }
        else:
            # Publishing failed
            scheduled_post.status = "failed"
            scheduled_post.error_message = result.error
            scheduled_post.retry_count = (scheduled_post.retry_count or 0) + 1
            scheduled_post.last_retry_at = datetime.utcnow()
            scheduled_post.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.error(
                f"Failed to publish scheduled post {scheduled_post_id}: {result.error}",
                extra={
                    "event_type": "scheduled_post_failed",
                    "scheduled_post_id": scheduled_post_id,
                    "platform": scheduled_post.platform,
                    "error": result.error,
                    "retry_count": scheduled_post.retry_count
                }
            )
            
            # Retry if not exceeded max retries
            if scheduled_post.retry_count < 3:
                logger.info(f"Retrying scheduled post {scheduled_post_id} (attempt {scheduled_post.retry_count + 1}/3)")
                raise self.retry(exc=Exception(result.error))
            
            return {
                "success": False,
                "scheduled_post_id": scheduled_post_id,
                "error": result.error,
                "retry_count": scheduled_post.retry_count
            }
    
    except Exception as e:
        logger.error(
            f"Error publishing scheduled post {scheduled_post_id}: {str(e)}",
            exc_info=True,
            extra={
                "event_type": "scheduled_post_error",
                "scheduled_post_id": scheduled_post_id
            }
        )
        
        # Update scheduled post with error
        try:
            scheduled_post = db.query(ScheduledPost).filter(
                ScheduledPost.id == scheduled_post_id
            ).first()
            
            if scheduled_post:
                scheduled_post.status = "failed"
                scheduled_post.error_message = str(e)
                scheduled_post.retry_count = (scheduled_post.retry_count or 0) + 1
                scheduled_post.last_retry_at = datetime.utcnow()
                scheduled_post.updated_at = datetime.utcnow()
                db.commit()
        except Exception as db_error:
            logger.error(f"Failed to update scheduled post error status: {db_error}")
        
        # Retry if not exceeded max retries
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        
        return {
            "success": False,
            "scheduled_post_id": scheduled_post_id,
            "error": str(e)
        }


@celery_app.task(base=DatabaseTask)
def check_and_publish_scheduled_posts():
    """
    Periodic task to check for posts scheduled within the next minute and publish them.
    
    Runs every minute via Celery Beat.
    """
    db = SessionLocal()
    
    try:
        # Find posts scheduled for the next minute
        now = datetime.utcnow()
        next_minute = now + timedelta(minutes=1)
        
        scheduled_posts = db.query(ScheduledPost).filter(
            ScheduledPost.status == "pending",
            ScheduledPost.scheduled_for <= next_minute,
            ScheduledPost.scheduled_for > now - timedelta(minutes=5)  # Don't process posts more than 5 min old
        ).all()
        
        logger.info(
            f"Checking scheduled posts: {len(scheduled_posts)} posts ready to publish",
            extra={
                "event_type": "scheduled_posts_check",
                "count": len(scheduled_posts),
                "time_range": f"{now} to {next_minute}"
            }
        )
        
        for post in scheduled_posts:
            # Calculate delay (publish exactly at scheduled time)
            delay_seconds = max(0, (post.scheduled_for - now).total_seconds())
            
            # Queue the publish task with ETA
            task = publish_scheduled_post.apply_async(
                args=[post.id],
                eta=post.scheduled_for
            )
            
            # Store Celery task ID
            post.celery_task_id = task.id
            post.status = "queued"
            post.updated_at = datetime.utcnow()
            
            logger.info(
                f"Queued scheduled post {post.id} for publishing at {post.scheduled_for}",
                extra={
                    "event_type": "scheduled_post_queued",
                    "scheduled_post_id": post.id,
                    "platform": post.platform,
                    "scheduled_for": post.scheduled_for.isoformat(),
                    "celery_task_id": task.id
                }
            )
        
        db.commit()
        
        return {
            "success": True,
            "checked_at": now.isoformat(),
            "posts_queued": len(scheduled_posts)
        }
    
    except Exception as e:
        logger.error(f"Error checking scheduled posts: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(base=DatabaseTask)
def cleanup_old_scheduled_posts():
    """
    Periodic task to clean up old scheduled posts.
    
    Marks posts older than 7 days as "expired" if still pending.
    Runs every 6 hours via Celery Beat.
    """
    db = SessionLocal()
    
    try:
        # Find posts older than 7 days that are still pending
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        old_posts = db.query(ScheduledPost).filter(
            ScheduledPost.status.in_(["pending", "queued"]),
            ScheduledPost.scheduled_for < cutoff_date
        ).all()
        
        logger.info(
            f"Cleaning up old scheduled posts: {len(old_posts)} posts expired",
            extra={
                "event_type": "scheduled_posts_cleanup",
                "count": len(old_posts),
                "cutoff_date": cutoff_date.isoformat()
            }
        )
        
        for post in old_posts:
            post.status = "expired"
            post.error_message = "Post expired - scheduled time was more than 7 days ago"
            post.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "cleaned_up": len(old_posts),
            "cutoff_date": cutoff_date.isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error cleaning up scheduled posts: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()
