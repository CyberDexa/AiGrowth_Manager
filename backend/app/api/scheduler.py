"""
Scheduler Management API Endpoints

Provides endpoints to view and control the background analytics sync scheduler.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.scheduler import (
    get_scheduler_status,
    trigger_sync_now,
    add_business_sync_job,
    remove_business_sync_job
)

router = APIRouter(prefix="/api/v1/scheduler", tags=["scheduler"])


@router.get("/status")
async def get_status():
    """
    Get the current status of the background scheduler.
    
    Returns:
        - running: Whether scheduler is active
        - jobs: List of scheduled jobs with next run times
        - state: Scheduler state (running, paused, stopped)
    """
    try:
        status = get_scheduler_status()
        return {
            "success": True,
            "status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get scheduler status: {str(e)}")


@router.post("/trigger-sync")
async def trigger_manual_sync(business_id: Optional[int] = None):
    """
    Manually trigger an immediate analytics sync.
    
    Args:
        business_id: Optional business ID. If not provided, syncs all businesses.
    
    Returns:
        Success message
    """
    try:
        success = trigger_sync_now(business_id=business_id)
        
        if success:
            message = f"Sync triggered for business {business_id}" if business_id else "Sync triggered for all businesses"
            return {
                "success": True,
                "message": message
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to trigger sync")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger sync: {str(e)}")


@router.post("/business/{business_id}/schedule")
async def schedule_business_sync(
    business_id: int,
    interval_hours: int = 24,
    db: Session = Depends(get_db)
):
    """
    Add or update a recurring sync job for a specific business.
    
    Args:
        business_id: ID of the business to sync
        interval_hours: How often to sync (in hours). Default: 24 hours
    
    Returns:
        Success message with job details
    """
    # Verify business exists
    from app.models.business import Business
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail=f"Business {business_id} not found")
    
    try:
        success = add_business_sync_job(business_id, interval_hours)
        
        if success:
            return {
                "success": True,
                "message": f"Scheduled sync for business {business_id} every {interval_hours} hours",
                "business_id": business_id,
                "interval_hours": interval_hours
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to schedule sync job")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule sync: {str(e)}")


@router.delete("/business/{business_id}/schedule")
async def remove_business_schedule(business_id: int):
    """
    Remove the recurring sync job for a specific business.
    
    Args:
        business_id: ID of the business
    
    Returns:
        Success message
    """
    try:
        success = remove_business_sync_job(business_id)
        
        if success:
            return {
                "success": True,
                "message": f"Removed scheduled sync for business {business_id}",
                "business_id": business_id
            }
        else:
            return {
                "success": False,
                "message": f"No scheduled sync found for business {business_id}",
                "business_id": business_id
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove schedule: {str(e)}")


@router.get("/jobs")
async def list_scheduled_jobs():
    """
    List all currently scheduled jobs.
    
    Returns:
        List of jobs with their details
    """
    try:
        status = get_scheduler_status()
        return {
            "success": True,
            "scheduler_running": status["running"],
            "jobs": status["jobs"],
            "total_jobs": len(status["jobs"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")
