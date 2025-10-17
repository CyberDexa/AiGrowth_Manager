"""Pydantic schemas for analytics endpoints."""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal


# ============================================================================
# Post Analytics Schemas
# ============================================================================

class PostAnalyticsBase(BaseModel):
    """Base schema for post analytics."""
    published_post_id: int
    business_id: int
    platform: str
    
    # Engagement Metrics
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    reactions_count: int = 0
    retweets_count: int = 0
    quote_tweets_count: int = 0
    
    # Reach Metrics
    impressions: int = 0
    reach: int = 0
    clicks: int = 0
    
    # Video Metrics
    video_views: int = 0
    video_watch_time: int = 0
    
    # Calculated Metrics
    engagement_rate: float = 0.0
    click_through_rate: float = 0.0
    
    # Metadata
    platform_post_id: Optional[str] = None
    platform_post_url: Optional[str] = None


class PostAnalyticsCreate(PostAnalyticsBase):
    """Schema for creating post analytics."""
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class PostAnalyticsUpdate(BaseModel):
    """Schema for updating post analytics."""
    likes_count: Optional[int] = None
    comments_count: Optional[int] = None
    shares_count: Optional[int] = None
    reactions_count: Optional[int] = None
    retweets_count: Optional[int] = None
    quote_tweets_count: Optional[int] = None
    impressions: Optional[int] = None
    reach: Optional[int] = None
    clicks: Optional[int] = None
    video_views: Optional[int] = None
    video_watch_time: Optional[int] = None
    engagement_rate: Optional[float] = None
    click_through_rate: Optional[float] = None


class PostAnalyticsResponse(PostAnalyticsBase):
    """Schema for post analytics response."""
    id: int
    total_engagement: int
    total_interactions: int
    fetched_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Optional post content preview
    content_preview: Optional[str] = None
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Analytics Summary Schemas
# ============================================================================

class AnalyticsSummaryBase(BaseModel):
    """Base schema for analytics summary."""
    business_id: int
    platform: str
    period_type: str  # daily, weekly, monthly, yearly
    period_start: date
    period_end: date
    
    # Summary Metrics
    total_posts: int = 0
    total_likes: int = 0
    total_comments: int = 0
    total_shares: int = 0
    total_impressions: int = 0
    total_reach: int = 0
    total_clicks: int = 0
    
    # Calculated Metrics
    avg_engagement_rate: float = 0.0
    avg_impressions: int = 0
    follower_growth: int = 0
    
    # Best Performing
    best_post_id: Optional[int] = None
    best_post_engagement_rate: Optional[float] = None


class AnalyticsSummaryCreate(AnalyticsSummaryBase):
    """Schema for creating analytics summary."""
    pass


class AnalyticsSummaryResponse(AnalyticsSummaryBase):
    """Schema for analytics summary response."""
    id: int
    total_engagement: int
    period_duration_days: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Dashboard Overview Schemas
# ============================================================================

class PlatformMetrics(BaseModel):
    """Metrics for a single platform."""
    platform: str
    total_posts: int
    total_likes: int
    total_comments: int
    total_shares: int
    total_impressions: int
    total_reach: int
    avg_engagement_rate: float
    percentage_of_total: float = 0.0


class EngagementTrend(BaseModel):
    """Engagement data point for trend chart."""
    date: str  # ISO format date
    engagement_rate: float
    total_engagement: int
    impressions: int
    posts_count: int = 0


class TopPost(BaseModel):
    """Top performing post summary."""
    id: int
    published_post_id: int
    content_preview: str
    platform: str
    published_at: datetime
    engagement_rate: float
    likes_count: int
    comments_count: int
    shares_count: int
    impressions: int
    platform_post_url: Optional[str] = None


class BestPostingTime(BaseModel):
    """Best time to post analysis."""
    day_of_week: str
    hour_of_day: int
    avg_engagement_rate: float
    posts_count: int
    confidence_score: float  # 0-100, based on sample size


class AnalyticsOverview(BaseModel):
    """Complete analytics overview for dashboard."""
    
    # Time Period
    period_start: date
    period_end: date
    
    # Overall Summary
    summary: Dict[str, Any] = Field(
        description="Overall metrics across all platforms",
        example={
            "total_posts": 45,
            "total_likes": 1234,
            "total_comments": 234,
            "total_shares": 89,
            "total_impressions": 45678,
            "total_reach": 38901,
            "avg_engagement_rate": 6.8
        }
    )
    
    # Platform Breakdown
    by_platform: List[PlatformMetrics] = Field(
        description="Metrics broken down by platform"
    )
    
    # Trends Over Time
    trends: List[EngagementTrend] = Field(
        description="Daily engagement trends"
    )
    
    # Top Performing Posts
    top_posts: List[TopPost] = Field(
        description="Best performing posts by engagement rate",
        max_items=10
    )
    
    # Best Posting Times
    best_times: List[BestPostingTime] = Field(
        description="Optimal times to post",
        max_items=7
    )


# ============================================================================
# Query Parameters Schemas
# ============================================================================

class AnalyticsQueryParams(BaseModel):
    """Query parameters for analytics endpoints."""
    business_id: int = Field(..., description="Business ID to fetch analytics for")
    platform: Optional[str] = Field(None, description="Filter by platform (linkedin, twitter, facebook, instagram)")
    start_date: Optional[date] = Field(None, description="Start date for analytics period")
    end_date: Optional[date] = Field(None, description="End date for analytics period")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results to return")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """Ensure end_date is after start_date."""
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError('end_date must be after start_date')
        return v
    
    @validator('platform')
    def validate_platform(cls, v):
        """Validate platform value."""
        if v and v not in ['linkedin', 'twitter', 'facebook', 'instagram', 'all']:
            raise ValueError('Invalid platform. Must be: linkedin, twitter, facebook, instagram, or all')
        return v


# ============================================================================
# Platform Comparison Schemas
# ============================================================================

class PlatformComparison(BaseModel):
    """Comparison of performance across platforms."""
    period_start: date
    period_end: date
    platforms: List[PlatformMetrics]
    
    # Winner Analysis
    best_platform: str = Field(description="Platform with highest engagement rate")
    best_engagement_rate: float
    
    # Growth Analysis
    fastest_growing: str = Field(description="Platform with highest growth")
    growth_percentage: float


# ============================================================================
# Time-Based Insights Schemas
# ============================================================================

class DayOfWeekInsight(BaseModel):
    """Engagement insights by day of week."""
    day: str  # Monday, Tuesday, etc.
    day_number: int  # 0-6 (Monday=0)
    posts_count: int
    avg_engagement_rate: float
    total_impressions: int
    best_hour: int  # 0-23


class HourOfDayInsight(BaseModel):
    """Engagement insights by hour of day."""
    hour: int  # 0-23
    posts_count: int
    avg_engagement_rate: float
    total_impressions: int


class BestTimesToPost(BaseModel):
    """Complete time-based insights."""
    by_day: List[DayOfWeekInsight]
    by_hour: List[HourOfDayInsight]
    recommendations: List[str] = Field(
        description="Actionable recommendations",
        example=[
            "Post on Tuesday at 2 PM for best engagement (9.5% avg)",
            "Avoid posting on Friday evenings (7.1% avg)",
            "Your audience is most active between 9 AM - 5 PM"
        ]
    )


# ============================================================================
# Export Schemas
# ============================================================================

class ExportFormat(BaseModel):
    """Export format options."""
    format: str = Field("csv", description="Export format (csv, json)")
    include_charts: bool = Field(False, description="Include chart data in export")
    
    @validator('format')
    def validate_format(cls, v):
        """Validate export format."""
        if v not in ['csv', 'json', 'pdf']:
            raise ValueError('Invalid format. Must be: csv, json, or pdf')
        return v


class ExportRequest(BaseModel):
    """Request schema for exporting analytics."""
    business_id: int
    platform: Optional[str] = None
    start_date: date
    end_date: date
    format: str = "csv"
    include_summary: bool = True
    include_posts: bool = True
    include_trends: bool = True


class ExportResponse(BaseModel):
    """Response schema for export."""
    success: bool
    file_url: Optional[str] = None
    file_name: str
    format: str
    records_exported: int
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Refresh/Sync Schemas
# ============================================================================

class AnalyticsRefreshRequest(BaseModel):
    """Request to refresh analytics from platform APIs."""
    business_id: int = Field(
        description="Business ID to refresh analytics for"
    )
    platforms: Optional[List[str]] = Field(
        None,
        description="List of platforms to sync (linkedin, twitter, facebook, instagram). None = all platforms"
    )
    limit: Optional[int] = Field(
        None,
        description="Maximum number of posts to sync per platform"
    )


class AnalyticsRefreshResponse(BaseModel):
    """Response for analytics refresh."""
    business_id: int
    platforms: List[str]
    posts_updated: int
    last_synced_at: datetime
    status: str  # "completed", "partial", "failed"
    message: str
    sync_details: Optional[Dict[str, Any]] = None


# ============================================================================
# Error Schemas
# ============================================================================

class AnalyticsError(BaseModel):
    """Error response for analytics endpoints."""
    error: str
    detail: str
    platform: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Metric Calculation Schemas
# ============================================================================

class EngagementMetrics(BaseModel):
    """Calculated engagement metrics."""
    engagement_rate: float = Field(description="(likes + comments + shares) / impressions * 100")
    click_through_rate: float = Field(description="clicks / impressions * 100")
    virality_score: float = Field(description="shares / impressions * 100")
    comment_rate: float = Field(description="comments / impressions * 100")
    video_completion_rate: Optional[float] = Field(None, description="For video posts only")


class GrowthMetrics(BaseModel):
    """Growth comparison metrics."""
    current_period: Dict[str, Any]
    previous_period: Dict[str, Any]
    growth_percentage: float
    growth_trend: str  # "up", "down", "stable"
