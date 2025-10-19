"""
Publishing Schemas

Pydantic schemas for content publishing API.
"""
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class PublishRequest(BaseModel):
    """Request schema for publishing content to social media."""
    business_id: int = Field(..., description="Business ID")
    strategy_id: Optional[int] = Field(None, description="Optional strategy ID to link post to")
    content_text: str = Field(..., min_length=1, max_length=3000, description="Post content text")
    content_images: Optional[List[str]] = Field(None, description="Optional image URLs")
    content_links: Optional[List[str]] = Field(None, description="Optional links in post")
    scheduled_for: Optional[datetime] = Field(None, description="Schedule for future publication")
    
    @validator('content_text')
    def validate_content_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Content text cannot be empty')
        return v.strip()
    
    @validator('scheduled_for')
    def validate_scheduled_time(cls, v):
        if v:
            # Make comparison timezone-aware
            now = datetime.now(timezone.utc)
            compare_time = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
            if compare_time < now:
                raise ValueError('Scheduled time must be in the future')
        return v


class PublishResponse(BaseModel):
    """Response schema after publishing content."""
    id: int
    business_id: int
    platform: str
    status: str
    content_text: str
    platform_post_id: Optional[str] = None
    platform_post_url: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    published_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PublishedPostResponse(BaseModel):
    """Detailed response for published post."""
    id: int
    business_id: int
    strategy_id: Optional[int] = None
    social_account_id: int
    
    # Content
    content_text: str
    content_images: Optional[List[str]] = None
    content_links: Optional[List[str]] = None
    
    # Platform Details
    platform: str
    platform_post_id: Optional[str] = None
    platform_post_url: Optional[str] = None
    
    # Publishing Info
    status: str
    scheduled_for: Optional[datetime] = None
    published_at: Optional[datetime] = None
    
    # Error Tracking
    error_message: Optional[str] = None
    retry_count: int = 0
    last_retry_at: Optional[datetime] = None
    
    # Engagement Metrics
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    impressions_count: int = 0
    last_metrics_sync: Optional[datetime] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PublishedPostListResponse(BaseModel):
    """Response for listing published posts with pagination."""
    posts: List[PublishedPostResponse]
    total: int
    limit: int
    offset: int


class RetryPostRequest(BaseModel):
    """Request to retry a failed post."""
    post_id: int = Field(..., description="Published post ID to retry")
