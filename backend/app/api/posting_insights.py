"""
Posting Time Recommendations API
Analyzes engagement patterns to suggest optimal posting times
"""
from typing import List, Dict, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import statistics

from app.db.database import get_db
from app.core.auth import get_current_user
from app.models.published_post import PublishedPost
from app.models.business import Business

router = APIRouter()


# Pydantic schemas
class TimeSlot(BaseModel):
    day: str = Field(..., description="Day of week (Monday, Tuesday, etc.)")
    hour: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")
    avg_engagement_rate: float = Field(..., description="Average engagement rate for this time slot")
    post_count: int = Field(..., description="Number of posts at this time")
    confidence: str = Field(..., description="Confidence level: high, medium, low")


class PlatformRecommendation(BaseModel):
    platform: str
    best_times: List[TimeSlot]
    overall_best_day: str
    overall_best_hour: int
    total_posts_analyzed: int
    avg_engagement_rate: float
    insights: List[str]


class RecommendationsResponse(BaseModel):
    recommendations: List[PlatformRecommendation]
    business_id: int
    analysis_period_days: int
    last_updated: datetime


# Platform-specific default best times (industry benchmarks)
PLATFORM_DEFAULTS = {
    "twitter": {
        "best_days": ["Wednesday", "Friday"],
        "best_hours": [9, 12, 15, 17],
        "insights": [
            "Twitter sees highest engagement during work breaks",
            "Mid-week posts (Wed-Fri) perform 23% better",
            "Avoid posting after 8 PM - engagement drops significantly"
        ]
    },
    "linkedin": {
        "best_days": ["Tuesday", "Wednesday", "Thursday"],
        "best_hours": [7, 8, 12, 17, 18],
        "insights": [
            "LinkedIn users are most active before work (7-9 AM)",
            "Lunch time (12-1 PM) shows strong engagement",
            "Tuesday-Thursday are peak professional browsing days"
        ]
    },
    "facebook": {
        "best_days": ["Wednesday", "Thursday", "Friday"],
        "best_hours": [11, 13, 15, 19, 20],
        "insights": [
            "Facebook engagement peaks mid-week afternoons",
            "Evening posts (7-9 PM) catch leisure browsing",
            "Weekend posts perform 15% worse than weekdays"
        ]
    },
    "instagram": {
        "best_days": ["Wednesday", "Friday", "Saturday"],
        "best_hours": [11, 14, 19, 21],
        "insights": [
            "Instagram Stories peak at lunch (11 AM-1 PM)",
            "Feed posts perform best in evening (7-9 PM)",
            "Weekend posts get 31% more likes than weekdays"
        ]
    }
}


def calculate_engagement_rate(post: PublishedPost) -> float:
    """Calculate engagement rate for a post"""
    total_engagement = (
        (post.likes_count or 0) +
        (post.comments_count or 0) +
        (post.shares_count or 0)
    )
    impressions = post.impressions_count or 0
    
    if impressions > 0:
        return (total_engagement / impressions) * 100
    elif total_engagement > 0:
        # If no impressions data, use engagement count as proxy
        return float(total_engagement)
    
    return 0.0


def get_confidence_level(post_count: int) -> str:
    """Determine confidence level based on sample size"""
    if post_count >= 20:
        return "high"
    elif post_count >= 10:
        return "medium"
    else:
        return "low"


def analyze_platform_timing(
    posts: List[PublishedPost],
    platform: str
) -> PlatformRecommendation:
    """Analyze posting times for a specific platform"""
    
    if not posts:
        # Return default recommendations if no data
        defaults = PLATFORM_DEFAULTS.get(platform.lower(), PLATFORM_DEFAULTS["twitter"])
        return PlatformRecommendation(
            platform=platform,
            best_times=[
                TimeSlot(
                    day=day,
                    hour=hour,
                    avg_engagement_rate=0.0,
                    post_count=0,
                    confidence="low"
                )
                for day in defaults["best_days"]
                for hour in defaults["best_hours"][:2]
            ][:5],
            overall_best_day=defaults["best_days"][0],
            overall_best_hour=defaults["best_hours"][0],
            total_posts_analyzed=0,
            avg_engagement_rate=0.0,
            insights=defaults["insights"]
        )
    
    # Group posts by day of week and hour
    time_slot_data: Dict[tuple, List[float]] = {}
    
    for post in posts:
        if not post.published_at:
            continue
        
        day = post.published_at.strftime("%A")
        hour = post.published_at.hour
        engagement_rate = calculate_engagement_rate(post)
        
        key = (day, hour)
        if key not in time_slot_data:
            time_slot_data[key] = []
        time_slot_data[key].append(engagement_rate)
    
    # Calculate average engagement for each time slot
    time_slots = []
    for (day, hour), engagement_rates in time_slot_data.items():
        if engagement_rates:
            avg_rate = statistics.mean(engagement_rates)
            post_count = len(engagement_rates)
            confidence = get_confidence_level(post_count)
            
            time_slots.append(TimeSlot(
                day=day,
                hour=hour,
                avg_engagement_rate=round(avg_rate, 2),
                post_count=post_count,
                confidence=confidence
            ))
    
    # Sort by engagement rate and get top 5
    time_slots.sort(key=lambda x: x.avg_engagement_rate, reverse=True)
    best_times = time_slots[:5]
    
    # Calculate overall stats
    all_engagement_rates = [calculate_engagement_rate(p) for p in posts if calculate_engagement_rate(p) > 0]
    avg_engagement = statistics.mean(all_engagement_rates) if all_engagement_rates else 0.0
    
    # Find overall best day and hour
    overall_best_day = best_times[0].day if best_times else "Wednesday"
    overall_best_hour = best_times[0].hour if best_times else 12
    
    # Generate personalized insights
    insights = []
    if len(posts) >= 10:
        insights.append(f"Based on your {len(posts)} posts, we've identified your audience's peak activity times")
        
        if best_times and best_times[0].avg_engagement_rate > avg_engagement * 1.5:
            insights.append(f"Posts at {overall_best_hour}:00 on {overall_best_day}s perform 50%+ better than average")
        
        # Day of week analysis
        day_performance = {}
        for post in posts:
            if post.published_at:
                day = post.published_at.strftime("%A")
                rate = calculate_engagement_rate(post)
                if day not in day_performance:
                    day_performance[day] = []
                day_performance[day].append(rate)
        
        if day_performance:
            best_day = max(day_performance.items(), key=lambda x: statistics.mean(x[1]) if x[1] else 0)
            worst_day = min(day_performance.items(), key=lambda x: statistics.mean(x[1]) if x[1] else 0)
            if best_day[0] != worst_day[0]:
                insights.append(f"{best_day[0]} posts outperform {worst_day[0]} posts significantly")
    else:
        # Use platform defaults for insights
        defaults = PLATFORM_DEFAULTS.get(platform.lower(), PLATFORM_DEFAULTS["twitter"])
        insights.extend(defaults["insights"])
    
    return PlatformRecommendation(
        platform=platform,
        best_times=best_times,
        overall_best_day=overall_best_day,
        overall_best_hour=overall_best_hour,
        total_posts_analyzed=len(posts),
        avg_engagement_rate=round(avg_engagement, 2),
        insights=insights[:3]
    )


@router.get("/recommendations", response_model=RecommendationsResponse)
async def get_posting_recommendations(
    business_id: int,
    days: int = 90,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get posting time recommendations based on engagement analysis
    
    Analyzes historical post performance to identify optimal posting times
    for each platform. Returns personalized recommendations with confidence levels.
    """
    # Verify business ownership
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == current_user["sub"]
    ).first()
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found or access denied"
        )
    
    # Calculate date range
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get all published posts for this business within date range
    posts = db.query(PublishedPost).filter(
        PublishedPost.business_id == business_id,
        PublishedPost.status == "published",
        PublishedPost.published_at >= cutoff_date
    ).all()
    
    # Group posts by platform
    platform_posts: Dict[str, List[PublishedPost]] = {}
    for post in posts:
        platform = post.platform.lower()
        if platform not in platform_posts:
            platform_posts[platform] = []
        platform_posts[platform].append(post)
    
    # Analyze each platform
    recommendations = []
    for platform, platform_post_list in platform_posts.items():
        recommendation = analyze_platform_timing(platform_post_list, platform)
        recommendations.append(recommendation)
    
    # Add default recommendations for platforms without data
    existing_platforms = set(platform_posts.keys())
    all_platforms = {"twitter", "linkedin", "facebook", "instagram"}
    missing_platforms = all_platforms - existing_platforms
    
    for platform in missing_platforms:
        recommendation = analyze_platform_timing([], platform)
        recommendations.append(recommendation)
    
    return RecommendationsResponse(
        recommendations=recommendations,
        business_id=business_id,
        analysis_period_days=days,
        last_updated=datetime.utcnow()
    )


@router.get("/best-time-now", response_model=Dict[str, Any])
async def get_best_time_now(
    business_id: int,
    platform: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if now is a good time to post on a specific platform
    
    Returns whether the current time is optimal based on recommendations
    """
    # Verify business ownership
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == current_user["sub"]
    ).first()
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found or access denied"
        )
    
    # Get recommendations
    cutoff_date = datetime.utcnow() - timedelta(days=90)
    posts = db.query(PublishedPost).filter(
        PublishedPost.business_id == business_id,
        PublishedPost.platform == platform,
        PublishedPost.status == "published",
        PublishedPost.published_at >= cutoff_date
    ).all()
    
    recommendation = analyze_platform_timing(posts, platform)
    
    # Check current time
    now = datetime.now()
    current_day = now.strftime("%A")
    current_hour = now.hour
    
    # Check if current time matches any best time
    is_optimal = False
    matching_slot = None
    
    for time_slot in recommendation.best_times:
        if time_slot.day == current_day and time_slot.hour == current_hour:
            is_optimal = True
            matching_slot = time_slot
            break
    
    # Find next best time
    next_best = None
    if recommendation.best_times:
        # Simple approach: suggest the overall best time
        next_best = {
            "day": recommendation.overall_best_day,
            "hour": recommendation.overall_best_hour,
            "formatted": f"{recommendation.overall_best_day} at {recommendation.overall_best_hour}:00"
        }
    
    return {
        "is_optimal_time": is_optimal,
        "current_time": {
            "day": current_day,
            "hour": current_hour,
            "formatted": now.strftime("%A at %I:%M %p")
        },
        "matching_slot": matching_slot,
        "next_best_time": next_best,
        "recommendation": recommendation
    }
