"""
Publishing API v2 Endpoints

Clean API routes using the new publishing service architecture.
Handles immediate publishing, multi-platform publishing, and scheduling.
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import logging

from app.db.database import get_db
from app.core.auth import get_current_user_id
from app.core.encryption import decrypt_token

logger = logging.getLogger(__name__)

# Import rate limiting (gracefully handle if not installed)
try:
    from app.core.rate_limit import limiter, RateLimits
    RATE_LIMITING_ENABLED = True
except ImportError:
    RATE_LIMITING_ENABLED = False
    # Create dummy decorator if rate limiting not available
    class DummyLimiter:
        def limit(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    limiter = DummyLimiter()
    class RateLimits:
        PUBLISH_NOW = "20/hour"
        PUBLISH_MULTI = "10/hour"
        SCHEDULE_POST = "50/hour"

from app.models.business import Business
from app.models.social_account import SocialAccount
from app.models.published_post import PublishedPost
from app.models.scheduled_post import ScheduledPost
from app.schemas.publishing_v2 import (
    PublishRequest,
    PublishResponse,
    MultiPlatformPublishRequest,
    MultiPlatformPublishResponse,
    SchedulePublishRequest,
    ScheduledPostResponse,
    ScheduledPostListResponse,
    CancelScheduledPostResponse,
    UpdateScheduledPostRequest
)
from app.services.publishing import (
    linkedin_publisher,
    twitter_publisher,
    meta_publisher
)

router = APIRouter()


def get_publisher(platform: str):
    """Get the appropriate publisher for the platform."""
    publishers = {
        "linkedin": linkedin_publisher,
        "twitter": twitter_publisher,
        "meta": meta_publisher
    }
    
    publisher = publishers.get(platform.lower())
    if not publisher:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
    
    return publisher


@router.post("/v2/publish", response_model=PublishResponse)
@limiter.limit(RateLimits.PUBLISH_NOW)
async def publish_now(
    request: Request,
    publish_request: PublishRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Publish content immediately to a single platform.
    
    **Rate Limit:** 20 requests per hour per user
    
    Supports: LinkedIn, Twitter, Meta (Facebook/Instagram)
    
    Platform-specific parameters:
    - LinkedIn: visibility ('PUBLIC' or 'CONNECTIONS'), organization_id
    - Twitter: allow_threads (bool)
    - Meta: platform_type ('facebook' or 'instagram'), page_id, instagram_account_id, image_url, link
    """
    try:
        # Get social account
        social_account = db.query(SocialAccount).filter(
            SocialAccount.id == publish_request.social_account_id
        ).first()
        
        if not social_account:
            raise HTTPException(status_code=404, detail="Social account not found")
        
        # Verify user owns this social account through business
        business = db.query(Business).filter(
            Business.id == social_account.business_id,
            Business.user_id == user_id
        ).first()
        
        if not business:
            raise HTTPException(status_code=403, detail="Access denied to this social account")
        
        # Check platform matches
        if social_account.platform.lower() != publish_request.platform.lower():
            raise HTTPException(
                status_code=400,
                detail=f"Social account platform ({social_account.platform}) doesn't match requested platform ({publish_request.platform})"
            )
        
        # Validate content length for Twitter
        if publish_request.platform.lower() == "twitter":
            if len(publish_request.content) > 280:
                raise HTTPException(
                    status_code=400,
                    detail=f"Twitter posts cannot exceed 280 characters. Your post is {len(publish_request.content)} characters."
                )
        
        # Decrypt access token
        access_token = decrypt_token(social_account.access_token)
        
        # Get publisher
        publisher = get_publisher(publish_request.platform)
        
        # Prepare platform parameters
        platform_params = publish_request.platform_params or {}
        
        # Add Meta-specific parameters from social account
        if publish_request.platform.lower() == "meta":
            if not platform_params.get("platform_type"):
                platform_params["platform_type"] = "facebook"  # Default
            
            if platform_params["platform_type"] == "facebook" and social_account.page_id:
                platform_params["page_id"] = social_account.page_id
            elif platform_params["platform_type"] == "instagram" and social_account.instagram_account_id:
                platform_params["instagram_account_id"] = social_account.instagram_account_id
        
        # Publish!
        result = await publisher.publish(
            content=publish_request.content,
            access_token=access_token,
            **platform_params
        )
        
        # Save to database
        if result.success:
            published_post = PublishedPost(
                business_id=business.id,
                social_account_id=social_account.id,
                content_text=publish_request.content,
                platform=publish_request.platform,
                platform_post_id=result.post_id,
                platform_post_url=result.url,
                status="published",
                published_at=result.published_at or datetime.utcnow()
            )
            db.add(published_post)
            db.commit()
            db.refresh(published_post)
        else:
            # Save failed post
            published_post = PublishedPost(
                business_id=business.id,
                social_account_id=social_account.id,
                content_text=publish_request.content,
                platform=publish_request.platform,
                status="failed",
                error_message=result.error
            )
            db.add(published_post)
            db.commit()
        
        return PublishResponse(
            success=result.success,
            platform=result.platform,
            post_id=result.post_id,
            post_url=result.url,
            error=result.error,
            metadata=result.metadata,
            published_at=result.published_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Publishing failed: {str(e)}")


@router.post("/v2/publish/multi", response_model=MultiPlatformPublishResponse)
@limiter.limit(RateLimits.PUBLISH_MULTI)
async def publish_multi_platform(
    request: Request,
    publish_request: MultiPlatformPublishRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Publish content to multiple platforms simultaneously.
    
    **Rate Limit:** 10 requests per hour per user
    
    Each platform config should include:
    - platform: 'linkedin', 'twitter', or 'meta'
    - social_account_id: The account ID to publish from
    - platform_params: Platform-specific parameters (optional)
    """
    results = []
    
    for platform_config in publish_request.platforms:
        try:
            # Create publish request for this platform
            publish_req = PublishRequest(
                content=publish_request.content,
                platform=platform_config["platform"],
                social_account_id=platform_config["social_account_id"],
                platform_params=platform_config.get("platform_params")
            )
            
            # Publish to this platform (bypass rate limit for internal call)
            result = await publish_now(request, publish_req, db, user_id)
            results.append(result)
        
        except HTTPException as e:
            # Add failed result
            results.append(PublishResponse(
                success=False,
                platform=platform_config.get("platform", "unknown"),
                error=e.detail
            ))
        except Exception as e:
            results.append(PublishResponse(
                success=False,
                platform=platform_config.get("platform", "unknown"),
                error=str(e)
            ))
    
    # Calculate success/failure counts
    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful
    
    return MultiPlatformPublishResponse(
        results=results,
        total_platforms=len(results),
        successful_publishes=successful,
        failed_publishes=failed
    )


@router.post("/v2/schedule", response_model=ScheduledPostResponse)
@limiter.limit(RateLimits.SCHEDULE_POST)
async def schedule_post(
    request: Request,
    schedule_request: SchedulePublishRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Schedule a post for future publishing.
    
    **Rate Limit:** 50 requests per hour per user
    
    Note: Requires Celery worker to be running for scheduled posts to be published.
    """
    try:
        # Get social account
        social_account = db.query(SocialAccount).filter(
            SocialAccount.id == schedule_request.social_account_id
        ).first()
        
        if not social_account:
            raise HTTPException(status_code=404, detail="Social account not found")
        
        # Verify ownership
        business = db.query(Business).filter(
            Business.id == social_account.business_id,
            Business.user_id == user_id
        ).first()
        
        if not business:
            raise HTTPException(status_code=403, detail="Access denied to this social account")
        
        # Check scheduled time is in future
        if schedule_request.scheduled_for <= datetime.utcnow():
            raise HTTPException(status_code=400, detail="Scheduled time must be in the future")
        
        # Create scheduled post
        scheduled_post = ScheduledPost(
            business_id=business.id,
            social_account_id=social_account.id,
            content_text=schedule_request.content,
            platform=schedule_request.platform,
            platform_params=schedule_request.platform_params or {},
            scheduled_for=schedule_request.scheduled_for,
            status="pending"
        )
        
        db.add(scheduled_post)
        db.commit()
        db.refresh(scheduled_post)
        
        # Create Celery task for publishing at scheduled time
        try:
            from app.tasks.publishing_tasks import publish_scheduled_post
            
            # Calculate ETA (when to execute the task)
            task = publish_scheduled_post.apply_async(
                args=[scheduled_post.id],
                eta=schedule_request.scheduled_for
            )
            
            # Store Celery task ID for potential cancellation
            scheduled_post.celery_task_id = task.id
            db.commit()
            
            logger.info(
                f"Scheduled post {scheduled_post.id} queued for Celery execution",
                extra={
                    "event_type": "celery_task_scheduled",
                    "scheduled_post_id": scheduled_post.id,
                    "task_id": task.id,
                    "eta": schedule_request.scheduled_for.isoformat()
                }
            )
        except ImportError:
            logger.warning("Celery not available - scheduled post created but won't auto-publish")
        except Exception as e:
            logger.error(f"Failed to create Celery task: {e}", exc_info=True)
        
        return ScheduledPostResponse(
            id=scheduled_post.id,
            content_text=scheduled_post.content_text,
            platform=scheduled_post.platform,
            social_account_id=scheduled_post.social_account_id,
            scheduled_for=scheduled_post.scheduled_for,
            status=scheduled_post.status,
            celery_task_id=scheduled_post.celery_task_id,
            created_at=scheduled_post.created_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scheduling failed: {str(e)}")


@router.get("/v2/scheduled", response_model=ScheduledPostListResponse)
async def get_scheduled_posts(
    business_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get all scheduled posts for a business.
    
    Returns only pending and publishing posts (excludes published, failed, cancelled).
    """
    # Verify business ownership
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Query scheduled posts
    scheduled_posts = db.query(ScheduledPost).filter(
        ScheduledPost.business_id == business_id,
        ScheduledPost.status.in_(["pending", "publishing"])
    ).order_by(ScheduledPost.scheduled_for).all()
    
    return ScheduledPostListResponse(
        scheduled_posts=[
            ScheduledPostResponse(
                id=post.id,
                content_text=post.content_text,
                platform=post.platform,
                social_account_id=post.social_account_id,
                scheduled_for=post.scheduled_for,
                status=post.status,
                celery_task_id=post.celery_task_id,
                created_at=post.created_at
            )
            for post in scheduled_posts
        ],
        total=len(scheduled_posts)
    )


@router.patch("/v2/scheduled/{scheduled_post_id}", response_model=ScheduledPostResponse)
async def update_scheduled_post(
    scheduled_post_id: int,
    update_request: UpdateScheduledPostRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Update a scheduled post's time and/or content.
    
    Reschedules the Celery task with the new time.
    """
    # Get scheduled post
    scheduled_post = db.query(ScheduledPost).filter(
        ScheduledPost.id == scheduled_post_id
    ).first()
    
    if not scheduled_post:
        raise HTTPException(status_code=404, detail="Scheduled post not found")
    
    # Verify ownership
    business = db.query(Business).filter(
        Business.id == scheduled_post.business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if post can be updated (only pending posts)
    if scheduled_post.status != "pending":
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot update post with status: {scheduled_post.status}. Only pending posts can be updated."
        )
    
    # Validate future date
    if update_request.scheduled_for <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Scheduled time must be in the future")
    
    # Update content if provided
    if update_request.content_text is not None:
        scheduled_post.content_text = update_request.content_text
    
    # Update schedule time
    old_scheduled_for = scheduled_post.scheduled_for
    scheduled_post.scheduled_for = update_request.scheduled_for
    scheduled_post.updated_at = datetime.utcnow()
    
    # Reschedule Celery task if exists
    if scheduled_post.celery_task_id:
        try:
            from app.celery_app import celery_app
            from app.tasks.publishing_tasks import publish_scheduled_post
            
            # Revoke old task
            celery_app.control.revoke(scheduled_post.celery_task_id, terminate=True)
            logger.info(
                f"Revoked old Celery task {scheduled_post.celery_task_id} for scheduled post {scheduled_post_id}",
                extra={
                    "event_type": "celery_task_revoked",
                    "scheduled_post_id": scheduled_post_id,
                    "old_task_id": scheduled_post.celery_task_id
                }
            )
            
            # Schedule new task
            result = publish_scheduled_post.apply_async(
                args=[scheduled_post_id],
                eta=update_request.scheduled_for
            )
            scheduled_post.celery_task_id = result.id
            
            logger.info(
                f"Rescheduled post {scheduled_post_id} from {old_scheduled_for} to {update_request.scheduled_for}",
                extra={
                    "event_type": "post_rescheduled",
                    "scheduled_post_id": scheduled_post_id,
                    "old_time": old_scheduled_for.isoformat(),
                    "new_time": update_request.scheduled_for.isoformat(),
                    "new_task_id": result.id
                }
            )
        except ImportError:
            logger.warning("Celery not available - cannot reschedule task")
        except Exception as e:
            logger.error(f"Failed to reschedule Celery task: {e}", exc_info=True)
            # Don't fail the update if Celery fails
    
    db.commit()
    db.refresh(scheduled_post)
    
    return ScheduledPostResponse(
        id=scheduled_post.id,
        content_text=scheduled_post.content_text,
        platform=scheduled_post.platform,
        social_account_id=scheduled_post.social_account_id,
        scheduled_for=scheduled_post.scheduled_for,
        status=scheduled_post.status,
        celery_task_id=scheduled_post.celery_task_id,
        created_at=scheduled_post.created_at
    )


@router.delete("/v2/schedule/{scheduled_post_id}", response_model=CancelScheduledPostResponse)
async def cancel_scheduled_post(
    scheduled_post_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Cancel a scheduled post.
    
    Also revokes the Celery task if it exists.
    """
    # Get scheduled post
    scheduled_post = db.query(ScheduledPost).filter(
        ScheduledPost.id == scheduled_post_id
    ).first()
    
    if not scheduled_post:
        raise HTTPException(status_code=404, detail="Scheduled post not found")
    
    # Verify ownership
    business = db.query(Business).filter(
        Business.id == scheduled_post.business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if already published
    if scheduled_post.status in ["published", "cancelled"]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel post with status: {scheduled_post.status}")
    
    # Revoke Celery task if exists
    if scheduled_post.celery_task_id:
        try:
            from app.celery_app import celery_app
            celery_app.control.revoke(scheduled_post.celery_task_id, terminate=True)
            logger.info(
                f"Revoked Celery task {scheduled_post.celery_task_id} for scheduled post {scheduled_post_id}",
                extra={
                    "event_type": "celery_task_revoked",
                    "scheduled_post_id": scheduled_post_id,
                    "task_id": scheduled_post.celery_task_id
                }
            )
        except ImportError:
            logger.warning("Celery not available - cannot revoke task")
        except Exception as e:
            logger.error(f"Failed to revoke Celery task: {e}", exc_info=True)
    
    # Update status
    scheduled_post.status = "cancelled"
    scheduled_post.updated_at = datetime.utcnow()
    db.commit()
    
    return CancelScheduledPostResponse(
        success=True,
        message="Scheduled post cancelled successfully",
        scheduled_post_id=scheduled_post_id
    )
