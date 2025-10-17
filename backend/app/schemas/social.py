"""
Pydantic schemas for social media accounts
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SocialAccountBase(BaseModel):
    """Base schema for social account"""
    platform: str  # 'linkedin', 'twitter', 'facebook', 'instagram'
    platform_username: Optional[str] = None


class SocialAccountCreate(SocialAccountBase):
    """Schema for creating a social account"""
    business_id: int
    platform_user_id: str
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None


class SocialAccountUpdate(BaseModel):
    """Schema for updating a social account"""
    platform_username: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class SocialAccountResponse(SocialAccountBase):
    """Schema for social account response (without sensitive data)"""
    id: int
    business_id: int
    platform_user_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    token_expires_at: Optional[datetime] = None
    
    # Don't include access_token or refresh_token in responses
    
    class Config:
        from_attributes = True


class OAuthCallbackData(BaseModel):
    """Schema for OAuth callback data"""
    code: str
    state: Optional[str] = None
    error: Optional[str] = None
    error_description: Optional[str] = None
