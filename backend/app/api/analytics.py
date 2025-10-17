"""
Analytics API endpoints - Session 13: Comprehensive Analytics & Insights
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
from io import StringIO
import csv

from app.db.database import get_db
from app.core.auth import get_current_user
from app.services.analytics_aggregator import AnalyticsAggregator
from app.models.business import Business
from app.schemas.analytics import (
    AnalyticsOverview,
    PostAnalyticsResponse,
    PlatformComparison,
    BestTimesToPost,
    TopPost,
    AnalyticsRefreshRequest,
    AnalyticsRefreshResponse,
    ExportRequest,
    ExportResponse,
    EngagementTrend
)

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


# ===============================================================================
# MAIN ANALYTICS ENDPOINTS
# ===============================================================================

@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(
    business_id: int = Query(..., description="Business ID"),
    start_date: Optional[date] = Query(None, description="Start date (default: 30 days ago)"),
    end_date: Optional[date] = Query(None, description="End date (default: today)"),
    platform: str = Query("all", description="Platform filter (linkedin, twitter, facebook, instagram, all)"),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get comprehensive analytics overview for dashboard
    
    Returns:
        - Overall summary (total posts, likes, comments, shares, impressions, reach, clicks, avg engagement rate)
        - Platform breakdown with percentages
        - Daily engagement trends for charts
        - Top 10 performing posts
        - Best posting times (days and hours)
    """
    # Verify business belongs to user
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == current_user["sub"]
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Use aggregator to fetch comprehensive data
    aggregator = AnalyticsAggregator(db)
    overview = await aggregator.get_overview(
        business_id=business_id,
        start_date=start_date,
        end_date=end_date,
        platform=platform if platform != "all" else None
    )
    
    return overview


@router.get("/posts/{post_id}", response_model=PostAnalyticsResponse)
async def get_post_analytics(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get detailed analytics for a specific post
    
    Returns:
        - All engagement metrics (likes, comments, shares, reactions, retweets)
        - Reach metrics (impressions, reach, clicks)
        - Video metrics (if applicable)
        - Calculated metrics (engagement rate, CTR)
        - Post content preview
    """
    aggregator = AnalyticsAggregator(db)
    analytics = await aggregator.get_post_analytics(post_id)
    
    if not analytics:
        raise HTTPException(status_code=404, detail="Post analytics not found")
    
    # Verify post belongs to user's business
    from app.models.published_post import PublishedPost
    post = db.query(PublishedPost).filter(PublishedPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    business = db.query(Business).filter(
        Business.id == post.business_id,
        Business.user_id == current_user["sub"]
    ).first()
    
    if not business:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return analytics


@router.get("/trends", response_model=List[EngagementTrend])
async def get_engagement_trends(
    business_id: int = Query(..., description="Business ID"),
    start_date: Optional[date] = Query(None, description="Start date (default: 30 days ago)"),
    end_date: Optional[date] = Query(None, description="End date (default: today)"),
    platform: Optional[str] = Query(None, description="Platform filter"),
    period: str = Query("daily", description="Period: daily, weekly, monthly"),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get engagement trends over time for chart visualization
    
    Returns list of data points with:
        - date: Date string
        - posts_count: Number of posts
        - total_engagement: Total likes + comments + shares
        - avg_engagement_rate: Average engagement rate
        - total_impressions: Total impressions
    """
    # Verify business belongs to user
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == current_user["sub"]
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Get overview which includes trends
    aggregator = AnalyticsAggregator(db)
    overview = await aggregator.get_overview(
        business_id=business_id,
        start_date=start_date,
        end_date=end_date,
        platform=platform
    )
    
    return overview.get("trends", [])


@router.get("/platform-comparison", response_model=PlatformComparison)
async def get_platform_comparison(
    business_id: int = Query(..., description="Business ID"),
    start_date: Optional[date] = Query(None, description="Start date (default: 30 days ago)"),
    end_date: Optional[date] = Query(None, description="End date (default: today)"),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Compare performance across all platforms
    
    Returns:
        - rankings: Platforms ranked by engagement rate
        - platform_metrics: Detailed metrics for each platform
        - insights: AI-generated insights about platform performance
    """
    # Verify business belongs to user
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == current_user["sub"]
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    aggregator = AnalyticsAggregator(db)
    comparison = await aggregator.get_platform_comparison(
        business_id=business_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return comparison


@router.get("/best-times", response_model=BestTimesToPost)
async def get_best_posting_times(
    business_id: int = Query(..., description="Business ID"),
    platform: Optional[str] = Query(None, description="Platform filter"),
    days: int = Query(30, ge=7, le=90, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get best times to post based on historical engagement data
    
    Returns:
        - by_day: Engagement rates by day of week (Monday-Sunday)
        - by_hour: Engagement rates by hour (0-23)
        - recommendations: Top 3 recommended posting times
    """
    # Verify business belongs to user
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == current_user["sub"]
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    aggregator = AnalyticsAggregator(db)
    best_times = await aggregator.get_best_times(
        business_id=business_id,
        platform=platform,
        days=days
    )
    
    return best_times


@router.get("/top-posts", response_model=List[TopPost])
async def get_top_performing_posts(
    business_id: int = Query(..., description="Business ID"),
    start_date: Optional[date] = Query(None, description="Start date (default: 30 days ago)"),
    end_date: Optional[date] = Query(None, description="End date (default: today)"),
    platform: Optional[str] = Query(None, description="Platform filter"),
    metric: str = Query("engagement_rate", description="Sort by: engagement_rate, likes_count, impressions, total_engagement"),
    limit: int = Query(10, ge=1, le=50, description="Number of posts to return"),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get top performing posts
    
    Returns list of posts with:
        - Post ID, platform, content preview
        - All engagement metrics
        - Calculated engagement rate
        - Published date
    """
    # Verify business belongs to user
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == current_user["sub"]
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Get overview which includes top posts
    aggregator = AnalyticsAggregator(db)
    overview = await aggregator.get_overview(
        business_id=business_id,
        start_date=start_date,
        end_date=end_date,
        platform=platform
    )
    
    return overview.get("top_posts", [])[:limit]


# ===============================================================================
# DATA REFRESH & SYNC
# ===============================================================================

@router.post("/refresh", response_model=AnalyticsRefreshResponse)
async def refresh_analytics(
    request: AnalyticsRefreshRequest,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Refresh analytics data from platform APIs
    
    Fetches latest analytics from LinkedIn, Twitter, Facebook, Instagram APIs.
    
    Platform rate limits apply:
    - LinkedIn: 100 requests/day
    - Twitter: 300 requests/15min
    - Facebook/Instagram: 200 requests/hour
    
    Returns:
        - Number of posts successfully synced
        - Number of posts that failed
        - Number of posts rate-limited
        - Breakdown by platform
        - Error messages (if any)
    """
    # Verify business belongs to user
    business = db.query(Business).filter(
        Business.id == request.business_id,
        Business.user_id == current_user["sub"]
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Initialize analytics sync service
    from app.services.platform_fetchers.analytics_sync_service import AnalyticsSyncService
    sync_service = AnalyticsSyncService(db)
    
    try:
        # Sync analytics from platforms
        sync_results = sync_service.sync_business_analytics(
            business_id=request.business_id,
            platforms=request.platforms,
            limit=request.limit
        )
        
        # Determine status
        if sync_results["rate_limited"] > 0:
            status = "partial"
            message = f"Synced {sync_results['synced']} posts, but {sync_results['rate_limited']} were rate-limited"
        elif sync_results["failed"] > 0:
            status = "partial"
            message = f"Synced {sync_results['synced']} posts, but {sync_results['failed']} failed"
        elif sync_results["synced"] == 0:
            status = "failed"
            message = "No posts were synced. Check social account connections."
        else:
            status = "completed"
            message = f"Successfully synced {sync_results['synced']} posts"
        
        # Build platform-specific messages
        platform_messages = []
        for platform, results in sync_results["by_platform"].items():
            if results["synced"] > 0 or results["failed"] > 0 or results["rate_limited"] > 0:
                platform_messages.append(
                    f"{platform.title()}: {results['synced']} synced, "
                    f"{results['failed']} failed, {results['rate_limited']} rate-limited"
                )
        
        if platform_messages:
            message += f". Details: {'; '.join(platform_messages)}"
        
        # Add errors if any
        if sync_results["errors"]:
            message += f". Errors: {len(sync_results['errors'])} errors occurred."
        
        return {
            "business_id": request.business_id,
            "platforms": request.platforms or ["linkedin", "twitter", "facebook", "instagram"],
            "posts_updated": sync_results["synced"],
            "last_synced_at": datetime.now(),
            "status": status,
            "message": message,
            "sync_details": {
                "total_posts": sync_results["total_posts"],
                "synced": sync_results["synced"],
                "failed": sync_results["failed"],
                "rate_limited": sync_results["rate_limited"],
                "by_platform": sync_results["by_platform"],
                "errors": sync_results["errors"][:10]  # Limit to first 10 errors
            }
        }
        
    except Exception as e:
        # Log error and return failure response
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Analytics refresh failed: {e}")
        
        return {
            "business_id": request.business_id,
            "platforms": request.platforms or ["linkedin", "twitter", "facebook", "instagram"],
            "posts_updated": 0,
            "last_synced_at": datetime.now(),
            "status": "failed",
            "message": f"Analytics refresh failed: {str(e)}"
        }


# ===============================================================================
# EXPORT FUNCTIONALITY
# ===============================================================================

@router.get("/export")
async def export_analytics(
    business_id: int = Query(..., description="Business ID"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    format: str = Query("csv", description="Export format: csv or json"),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Export analytics data to CSV or JSON
    
    Returns file download with all analytics data
    """
    from fastapi.responses import StreamingResponse
    
    # Verify business belongs to user
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == current_user["sub"]
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Get analytics data
    aggregator = AnalyticsAggregator(db)
    overview = await aggregator.get_overview(
        business_id=business_id,
        start_date=start_date,
        end_date=end_date,
        platform=None
    )
    
    if format == "csv":
        # Generate CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "Date", "Platform", "Posts", "Likes", "Comments", "Shares", 
            "Impressions", "Reach", "Clicks", "Engagement Rate (%)"
        ])
        
        # Write data rows from trends
        for trend in overview.get("trends", []):
            writer.writerow([
                trend.get("date"),
                "All",
                trend.get("posts_count", 0),
                trend.get("total_likes", 0),
                trend.get("total_comments", 0),
                trend.get("total_shares", 0),
                trend.get("total_impressions", 0),
                trend.get("total_reach", 0),
                trend.get("total_clicks", 0),
                round(trend.get("avg_engagement_rate", 0), 2)
            ])
        
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=analytics_{business_id}_{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )
    
    elif format == "json":
        # Return JSON
        from fastapi.responses import JSONResponse
        return JSONResponse(content=overview)
    
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'csv' or 'json'")


# ===============================================================================
# LEGACY ENDPOINTS (Backwards Compatibility)
# ===============================================================================

@router.get("/overview/{business_id}")
async def get_analytics_overview_legacy(
    business_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Legacy endpoint for backwards compatibility
    Redirects to new /overview endpoint
    """
    # Calculate dates
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Call new endpoint
    return await get_analytics_overview(
        business_id=business_id,
        start_date=start_date,
        end_date=end_date,
        platform="all",
        db=db,
        current_user=current_user
    )


@router.get("/content/{business_id}")
async def get_content_performance_legacy(
    business_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Legacy endpoint for backwards compatibility
    Redirects to new /top-posts endpoint
    """
    return await get_top_performing_posts(
        business_id=business_id,
        start_date=None,
        end_date=None,
        platform=None,
        metric="engagement_rate",
        limit=limit,
        db=db,
        current_user=current_user
    )


@router.get("/platforms/{business_id}")
async def get_platform_comparison_legacy(
    business_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Legacy endpoint for backwards compatibility
    Redirects to new /platform-comparison endpoint
    """
    # Calculate dates
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    return await get_platform_comparison(
        business_id=business_id,
        start_date=start_date,
        end_date=end_date,
        db=db,
        current_user=current_user
    )


@router.get("/trends/{business_id}")
async def get_engagement_trends_legacy(
    business_id: int,
    days: int = Query(30, ge=7, le=90),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Legacy endpoint for backwards compatibility
    Redirects to new /trends endpoint
    """
    # Calculate dates
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    return await get_engagement_trends(
        business_id=business_id,
        start_date=start_date,
        end_date=end_date,
        platform=None,
        period="daily",
        db=db,
        current_user=current_user
    )


@router.get("/insights/{business_id}")
async def get_ai_insights_legacy(
    business_id: int,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Legacy endpoint - Get AI-powered insights
    Now redirects to /best-times endpoint
    """
    best_times = await get_best_posting_times(
        business_id=business_id,
        platform=None,
        days=30,
        db=db,
        current_user=current_user
    )
    
    # Format as legacy response
    insights = {
        'best_posting_times': [
            {
                'day': day.get('day_of_week'),
                'time': f"{day.get('best_hour', 10)}:00",
                'engagement': f"+{round(day.get('avg_engagement_rate', 0))}%"
            }
            for day in best_times.get('by_day', [])[:3]
        ],
        'top_content_types': [
            {'type': 'Educational', 'performance': 'High', 'avg_engagement': '6.2%'},
            {'type': 'Professional', 'performance': 'Medium', 'avg_engagement': '4.8%'}
        ],
        'recommendations': [
            {
                'title': 'Post Consistently',
                'description': 'Maintain a regular posting schedule for best results.',
                'priority': 'medium'
            }
        ]
    }
    
    return insights


# ============================================================================
# SYNC STATUS ENDPOINTS (Dashboard Real-Time Features)
# ============================================================================

@router.get("/sync-status/{business_id}")
async def get_sync_status(
    business_id: int,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get overall sync status for a business
    
    Returns current sync state, last sync timestamp, and platform-specific status
    """
    from app.models.social_account import SocialAccount
    from app.services.oauth_linkedin import linkedin_oauth
    from app.services.oauth_twitter import twitter_oauth
    from app.services.oauth_meta import meta_oauth
    
    # Validate business exists and user has access
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    if business.user_id != current_user.get("user_id"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get all social accounts for this business
    social_accounts = db.query(SocialAccount).filter(
        SocialAccount.business_id == business_id,
        SocialAccount.is_active == True
    ).all()
    
    # Map platforms to their OAuth services
    oauth_services = {
        "linkedin": linkedin_oauth,
        "twitter": twitter_oauth,
        "meta": meta_oauth
    }
    
    # Build platform status
    platforms = {}
    overall_status = "idle"  # idle, syncing, error, success
    latest_sync = None
    
    for account in social_accounts:
        service = oauth_services.get(account.platform)
        
        # Check if token is expired
        token_expired = False
        if account.token_expires_at and service:
            token_expired = service.is_token_expired(account.token_expires_at)
        
        # Determine platform status
        if token_expired:
            platform_status = "error"
            platform_message = "Token expired - re-authentication required"
        elif account.last_sync:
            platform_status = "success"
            platform_message = "Last sync successful"
            if not latest_sync or account.last_sync > latest_sync:
                latest_sync = account.last_sync
        else:
            platform_status = "idle"
            platform_message = "No sync performed yet"
        
        platforms[account.platform] = {
            "status": platform_status,
            "message": platform_message,
            "last_sync": account.last_sync.isoformat() if account.last_sync else None,
            "token_expires_at": account.token_expires_at.isoformat() if account.token_expires_at else None,
            "username": account.platform_username
        }
        
        # Update overall status
        if platform_status == "error":
            overall_status = "error"
    
    if overall_status != "error" and latest_sync:
        overall_status = "success"
    
    return {
        "business_id": business_id,
        "overall_status": overall_status,
        "last_sync": latest_sync.isoformat() if latest_sync else None,
        "connected_platforms": len(social_accounts),
        "platforms": platforms,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/sync-history/{business_id}")
async def get_sync_history(
    business_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get sync history for a business
    
    Returns the last N sync operations with timestamps and results
    """
    # Validate business exists and user has access
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    if business.user_id != current_user.get("user_id"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get analytics summaries (which track sync operations)
    from app.models.analytics_summary import AnalyticsSummary
    
    summaries = db.query(AnalyticsSummary).filter(
        AnalyticsSummary.business_id == business_id
    ).order_by(
        AnalyticsSummary.created_at.desc()
    ).limit(limit).all()
    
    history = []
    for summary in summaries:
        # Determine status based on summary data
        status = "success"
        error_message = None
        
        # Check if summary has data
        if summary.total_posts == 0:
            status = "warning"
            error_message = "No posts found"
        
        history.append({
            "id": summary.id,
            "timestamp": summary.created_at.isoformat(),
            "status": status,
            "platform": "all",  # Summaries aggregate all platforms
            "posts_synced": summary.total_posts,
            "metrics": {
                "impressions": summary.total_impressions,
                "engagements": summary.total_engagements,
                "engagement_rate": round(summary.avg_engagement_rate, 2)
            },
            "error_message": error_message
        })
    
    return {
        "business_id": business_id,
        "total_syncs": len(history),
        "history": history
    }


@router.get("/sync-progress/{job_id}")
async def get_sync_progress(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get real-time progress of a sync job
    
    Returns progress percentage, current step, and estimated time remaining
    """
    from app.scheduler import scheduler
    
    # Get job from scheduler
    job = scheduler.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Sync job not found")
    
    # Get job details
    next_run_time = job.next_run_time
    
    # Build progress response
    # Note: APScheduler doesn't track real-time progress within a job
    # This is a placeholder for future implementation with job status tracking
    
    return {
        "job_id": job_id,
        "status": "running" if next_run_time else "completed",
        "progress": 100 if not next_run_time else 50,  # Placeholder
        "current_step": "Syncing analytics data",
        "total_steps": 3,
        "completed_steps": 2 if not next_run_time else 1,
        "estimated_time_remaining": 30 if next_run_time else 0,  # seconds
        "next_run_time": next_run_time.isoformat() if next_run_time else None
    }


