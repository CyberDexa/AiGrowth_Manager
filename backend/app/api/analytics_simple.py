"""
Simple Analytics API - Direct database queries without dependencies
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from datetime import datetime, timedelta

from app.db.database import get_db
from app.core.auth import get_current_user
from app.models.published_post import PublishedPost
from app.models.business import Business

router = APIRouter(prefix="/api/v1/analytics-simple", tags=["Analytics Simple"])


@router.get("/overview")
async def get_simple_overview(
    business_id: int = Query(...),
    days: int = Query(30),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Simple analytics overview using direct database queries"""
    
    # Verify business ownership
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == current_user["sub"]
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get published posts
    posts = db.query(PublishedPost).filter(
        PublishedPost.business_id == business_id,
        PublishedPost.status == "published",
        PublishedPost.published_at >= start_date
    ).all()
    
    # Calculate totals
    total_posts = len(posts)
    total_likes = sum(p.likes_count or 0 for p in posts)
    total_comments = sum(p.comments_count or 0 for p in posts)
    total_shares = sum(p.shares_count or 0 for p in posts)
    total_impressions = sum(p.impressions_count or 0 for p in posts)
    total_engagement = total_likes + total_comments + total_shares
    
    avg_engagement_rate = 0
    if total_impressions > 0:
        avg_engagement_rate = (total_engagement / total_impressions) * 100
    
    # Platform breakdown
    by_platform = {}
    for post in posts:
        platform = post.platform
        if platform not in by_platform:
            by_platform[platform] = {
                "posts": 0,
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "impressions": 0
            }
        by_platform[platform]["posts"] += 1
        by_platform[platform]["likes"] += post.likes_count or 0
        by_platform[platform]["comments"] += post.comments_count or 0
        by_platform[platform]["shares"] += post.shares_count or 0
        by_platform[platform]["impressions"] += post.impressions_count or 0
    
    # Top posts
    top_posts = sorted(
        posts,
        key=lambda p: (p.likes_count or 0) + (p.comments_count or 0) + (p.shares_count or 0),
        reverse=True
    )[:10]
    
    top_posts_data = []
    for post in top_posts:
        engagement = (post.likes_count or 0) + (post.comments_count or 0) + (post.shares_count or 0)
        eng_rate = 0
        if post.impressions_count and post.impressions_count > 0:
            eng_rate = (engagement / post.impressions_count) * 100
        
        top_posts_data.append({
            "id": post.id,
            "platform": post.platform,
            "content_preview": post.content_text[:100] + "..." if len(post.content_text) > 100 else post.content_text,
            "published_at": post.published_at.isoformat() if post.published_at else None,
            "likes": post.likes_count or 0,
            "comments": post.comments_count or 0,
            "shares": post.shares_count or 0,
            "impressions": post.impressions_count or 0,
            "engagement": engagement,
            "engagement_rate": round(eng_rate, 2)
        })
    
    # Trend data (daily)
    trends = []
    current_date = start_date
    while current_date <= end_date:
        day_posts = [p for p in posts if p.published_at and p.published_at.date() == current_date.date()]
        day_engagement = sum(
            (p.likes_count or 0) + (p.comments_count or 0) + (p.shares_count or 0)
            for p in day_posts
        )
        trends.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "posts": len(day_posts),
            "engagement": day_engagement
        })
        current_date += timedelta(days=1)
    
    return {
        "summary": {
            "total_posts": total_posts,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "total_engagement": total_engagement,
            "total_impressions": total_impressions,
            "total_reach": total_impressions,  # Same as impressions for now
            "avg_engagement_rate": round(avg_engagement_rate, 2)
        },
        "by_platform": by_platform,
        "top_posts": top_posts_data,
        "trends": trends,
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        }
    }


@router.get("/posts")
async def get_simple_posts(
    business_id: int = Query(...),
    limit: int = Query(10),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get list of published posts with metrics"""
    
    # Verify business ownership
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == current_user["user_id"]
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Get posts
    posts = db.query(PublishedPost).filter(
        PublishedPost.business_id == business_id,
        PublishedPost.status == "published"
    ).order_by(PublishedPost.published_at.desc()).limit(limit).all()
    
    posts_data = []
    for post in posts:
        engagement = (post.likes_count or 0) + (post.comments_count or 0) + (post.shares_count or 0)
        eng_rate = 0
        if post.impressions_count and post.impressions_count > 0:
            eng_rate = (engagement / post.impressions_count) * 100
        
        posts_data.append({
            "id": post.id,
            "platform": post.platform,
            "content_preview": post.content_text[:100] + "..." if len(post.content_text) > 100 else post.content_text,
            "published_at": post.published_at.isoformat() if post.published_at else None,
            "platform_post_url": post.platform_post_url,
            "likes": post.likes_count or 0,
            "comments": post.comments_count or 0,
            "shares": post.shares_count or 0,
            "impressions": post.impressions_count or 0,
            "engagement": engagement,
            "engagement_rate": round(eng_rate, 2)
        })
    
    return {"posts": posts_data}
