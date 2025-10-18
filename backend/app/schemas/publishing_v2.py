"""
Publishing API Request/Response Schemas
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class PublishRequest(BaseModel):
    """Request model for immediate publishing."""
    content: str = Field(..., description="Content text to publish", min_length=1)
    platform: str = Field(..., description="Platform to publish to", pattern="^(linkedin|twitter|meta)$")
    social_account_id: int = Field(..., description="Social account ID to publish from")
    platform_params: Optional[Dict[str, Any]] = Field(default=None, description="Platform-specific parameters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Excited to announce our new product launch!",
                "platform": "linkedin",
                "social_account_id": 1,
                "platform_params": {
                    "visibility": "PUBLIC"
                }
            }
        }


class MultiPlatformPublishRequest(BaseModel):
    """Request model for publishing to multiple platforms."""
    content: str = Field(..., description="Content text to publish", min_length=1)
    platforms: List[Dict[str, Any]] = Field(..., description="List of platforms with their configs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Check out our latest blog post!",
                "platforms": [
                    {
                        "platform": "linkedin",
                        "social_account_id": 1,
                        "platform_params": {"visibility": "PUBLIC"}
                    },
                    {
                        "platform": "twitter",
                        "social_account_id": 2,
                        "platform_params": {"allow_threads": True}
                    }
                ]
            }
        }


class SchedulePublishRequest(BaseModel):
    """Request model for scheduling a post."""
    content: str = Field(..., description="Content text to publish", min_length=1)
    platform: str = Field(..., description="Platform to publish to", pattern="^(linkedin|twitter|meta)$")
    social_account_id: int = Field(..., description="Social account ID to publish from")
    scheduled_for: datetime = Field(..., description="When to publish (UTC timestamp)")
    platform_params: Optional[Dict[str, Any]] = Field(default=None, description="Platform-specific parameters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Happy Monday! Here's our weekly tip...",
                "platform": "linkedin",
                "social_account_id": 1,
                "scheduled_for": "2025-01-20T10:00:00Z",
                "platform_params": {"visibility": "PUBLIC"}
            }
        }


class PublishResponse(BaseModel):
    """Response model for publish operations."""
    success: bool
    platform: str
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    published_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "platform": "linkedin",
                "post_id": "urn:li:share:1234567890",
                "post_url": "https://www.linkedin.com/feed/update/urn:li:share:1234567890",
                "metadata": {
                    "character_count": 150,
                    "visibility": "PUBLIC"
                },
                "published_at": "2025-01-16T12:00:00Z"
            }
        }


class MultiPlatformPublishResponse(BaseModel):
    """Response model for multi-platform publishing."""
    results: List[PublishResponse]
    total_platforms: int
    successful_publishes: int
    failed_publishes: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "success": True,
                        "platform": "linkedin",
                        "post_id": "urn:li:share:123",
                        "post_url": "https://www.linkedin.com/feed/update/urn:li:share:123"
                    },
                    {
                        "success": False,
                        "platform": "twitter",
                        "error": "Rate limit exceeded"
                    }
                ],
                "total_platforms": 2,
                "successful_publishes": 1,
                "failed_publishes": 1
            }
        }


class UpdateScheduledPostRequest(BaseModel):
    """Request model for updating a scheduled post."""
    scheduled_for: datetime
    content_text: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "scheduled_for": "2025-01-22T15:00:00Z",
                "content_text": "Updated content for the post"
            }
        }


class ScheduledPostResponse(BaseModel):
    """Response model for scheduled post."""
    id: int
    content_text: str
    platform: str
    social_account_id: int
    scheduled_for: datetime
    status: str
    celery_task_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "content_text": "Happy Monday! Here's our weekly tip...",
                "platform": "linkedin",
                "social_account_id": 1,
                "scheduled_for": "2025-01-20T10:00:00Z",
                "status": "pending",
                "celery_task_id": "abcd-1234-efgh-5678",
                "created_at": "2025-01-16T12:00:00Z"
            }
        }


class ScheduledPostListResponse(BaseModel):
    """Response model for list of scheduled posts."""
    scheduled_posts: List[ScheduledPostResponse]
    total: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "scheduled_posts": [
                    {
                        "id": 1,
                        "content_text": "Happy Monday!",
                        "platform": "linkedin",
                        "scheduled_for": "2025-01-20T10:00:00Z",
                        "status": "pending"
                    }
                ],
                "total": 1
            }
        }


class CancelScheduledPostResponse(BaseModel):
    """Response model for canceling a scheduled post."""
    success: bool
    message: str
    scheduled_post_id: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Scheduled post cancelled successfully",
                "scheduled_post_id": 1
            }
        }
