"""
Background Scheduler for Analytics Sync

Configures and manages scheduled jobs for automatic analytics synchronization.
Uses APScheduler to run periodic tasks without blocking the main application.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
from typing import Optional

from app.db.database import SessionLocal
from app.models.business import Business
from app.services.platform_fetchers.analytics_sync_service import AnalyticsSyncService

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: Optional[BackgroundScheduler] = None


def sync_all_businesses_job():
    """
    Background job to sync analytics for all businesses.
    
    Runs periodically to fetch latest analytics data from all platforms
    for all active businesses in the system.
    """
    job_start = datetime.utcnow()
    logger.info("Starting scheduled analytics sync for all businesses")
    
    db = SessionLocal()
    try:
        # Get all active businesses
        businesses = db.query(Business).all()
        
        if not businesses:
            logger.info("No businesses found to sync")
            return
        
        total_synced = 0
        total_failed = 0
        total_posts = 0
        
        # Sync each business
        for business in businesses:
            try:
                logger.info(f"Syncing analytics for business {business.id} ({business.name})")
                
                sync_service = AnalyticsSyncService(db)
                result = sync_service.sync_business_analytics(
                    business_id=business.id,
                    limit=100  # Limit per platform to avoid overwhelming APIs
                )
                
                total_synced += result["synced"]
                total_failed += result["failed"]
                total_posts += result["total_posts"]
                
                logger.info(
                    f"Business {business.id} sync complete: "
                    f"{result['synced']}/{result['total_posts']} posts synced"
                )
                
            except Exception as e:
                logger.error(f"Failed to sync business {business.id}: {e}", exc_info=True)
                total_failed += 1
        
        # Log summary
        duration = (datetime.utcnow() - job_start).total_seconds()
        logger.info(
            f"Scheduled analytics sync complete: "
            f"{total_synced}/{total_posts} posts synced, "
            f"{total_failed} failures, "
            f"{len(businesses)} businesses processed "
            f"in {duration:.2f}s"
        )
        
    except Exception as e:
        logger.error(f"Analytics sync job failed: {e}", exc_info=True)
        
    finally:
        db.close()


def sync_business_job(business_id: int):
    """
    Background job to sync analytics for a specific business.
    
    Args:
        business_id: ID of the business to sync
    """
    logger.info(f"Starting scheduled analytics sync for business {business_id}")
    
    db = SessionLocal()
    try:
        sync_service = AnalyticsSyncService(db)
        result = sync_service.sync_business_analytics(business_id=business_id)
        
        logger.info(
            f"Business {business_id} sync complete: "
            f"{result['synced']}/{result['total_posts']} posts synced, "
            f"{result['failed']} failures"
        )
        
    except Exception as e:
        logger.error(f"Failed to sync business {business_id}: {e}", exc_info=True)
        
    finally:
        db.close()


def start_scheduler():
    """
    Start the background scheduler with configured jobs.
    
    Scheduled Jobs:
    - Hourly analytics sync for all businesses (every hour at :00)
    - Cleanup job for old analytics data (daily at 2 AM)
    """
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler already running")
        return
    
    logger.info("Initializing background scheduler")
    
    # Create scheduler
    scheduler = BackgroundScheduler(
        timezone="UTC",
        job_defaults={
            'coalesce': True,  # Combine multiple missed runs into one
            'max_instances': 1,  # Only one instance of each job at a time
            'misfire_grace_time': 300  # 5 minutes grace time for missed jobs
        }
    )
    
    # Add jobs
    
    # 1. Sync all businesses every hour
    scheduler.add_job(
        func=sync_all_businesses_job,
        trigger=CronTrigger(minute=0),  # Every hour at :00
        id='sync_all_businesses',
        name='Sync Analytics for All Businesses',
        replace_existing=True
    )
    logger.info("Added job: Sync all businesses (hourly at :00)")
    
    # 2. Optional: Sync during peak hours more frequently (9 AM - 5 PM every 30 minutes)
    # Uncomment if you want more frequent syncs during business hours
    # scheduler.add_job(
    #     func=sync_all_businesses_job,
    #     trigger=CronTrigger(hour='9-17', minute='0,30'),
    #     id='sync_all_businesses_peak',
    #     name='Sync Analytics (Peak Hours)',
    #     replace_existing=True
    # )
    
    # Start scheduler
    scheduler.start()
    logger.info("Background scheduler started successfully")
    
    # Log scheduled jobs
    jobs = scheduler.get_jobs()
    logger.info(f"Active scheduled jobs: {len(jobs)}")
    for job in jobs:
        logger.info(f"  - {job.id}: {job.name} (next run: {job.next_run_time})")


def shutdown_scheduler():
    """
    Gracefully shutdown the background scheduler.
    
    Waits for currently running jobs to complete before shutting down.
    """
    global scheduler
    
    if scheduler is None:
        logger.warning("Scheduler not running")
        return
    
    logger.info("Shutting down background scheduler")
    
    try:
        # Shutdown and wait for jobs to complete (max 30 seconds)
        scheduler.shutdown(wait=True)
        scheduler = None
        logger.info("Background scheduler shut down successfully")
        
    except Exception as e:
        logger.error(f"Error shutting down scheduler: {e}", exc_info=True)


def get_scheduler_status():
    """
    Get the current status of the scheduler.
    
    Returns:
        Dictionary with scheduler status and active jobs
    """
    global scheduler
    
    if scheduler is None:
        return {
            "running": False,
            "jobs": []
        }
    
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger)
        })
    
    return {
        "running": scheduler.running,
        "jobs": jobs,
        "state": str(scheduler.state)
    }


def add_business_sync_job(business_id: int, interval_hours: int = 24):
    """
    Add a recurring sync job for a specific business.
    
    Args:
        business_id: ID of the business to sync
        interval_hours: How often to sync (in hours)
    """
    global scheduler
    
    if scheduler is None:
        logger.error("Cannot add job: scheduler not running")
        return False
    
    job_id = f"sync_business_{business_id}"
    
    try:
        scheduler.add_job(
            func=sync_business_job,
            trigger=IntervalTrigger(hours=interval_hours),
            args=[business_id],
            id=job_id,
            name=f"Sync Business {business_id}",
            replace_existing=True
        )
        
        logger.info(f"Added sync job for business {business_id} (every {interval_hours}h)")
        return True
        
    except Exception as e:
        logger.error(f"Failed to add sync job for business {business_id}: {e}")
        return False


def remove_business_sync_job(business_id: int):
    """
    Remove the recurring sync job for a specific business.
    
    Args:
        business_id: ID of the business
    """
    global scheduler
    
    if scheduler is None:
        logger.warning("Scheduler not running")
        return False
    
    job_id = f"sync_business_{business_id}"
    
    try:
        scheduler.remove_job(job_id)
        logger.info(f"Removed sync job for business {business_id}")
        return True
        
    except Exception as e:
        logger.warning(f"Failed to remove sync job for business {business_id}: {e}")
        return False


def trigger_sync_now(business_id: Optional[int] = None):
    """
    Manually trigger an immediate sync.
    
    Args:
        business_id: Optional business ID. If None, syncs all businesses.
    """
    global scheduler
    
    if scheduler is None:
        logger.error("Cannot trigger sync: scheduler not running")
        return False
    
    try:
        if business_id:
            # Sync specific business
            scheduler.add_job(
                func=sync_business_job,
                args=[business_id],
                id=f"manual_sync_business_{business_id}_{datetime.utcnow().timestamp()}",
                name=f"Manual Sync Business {business_id}"
            )
            logger.info(f"Triggered manual sync for business {business_id}")
        else:
            # Sync all businesses
            scheduler.add_job(
                func=sync_all_businesses_job,
                id=f"manual_sync_all_{datetime.utcnow().timestamp()}",
                name="Manual Sync All Businesses"
            )
            logger.info("Triggered manual sync for all businesses")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to trigger manual sync: {e}")
        return False
