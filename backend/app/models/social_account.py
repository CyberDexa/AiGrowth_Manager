"""
SocialAccount model - stores connected social media accounts
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class SocialAccount(Base):
    __tablename__ = "social_accounts"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to business
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    
    # Platform details
    platform = Column(String, nullable=False)  # linkedin, twitter, facebook, instagram
    platform_user_id = Column(String, nullable=False)  # User ID on the platform
    platform_username = Column(String, nullable=True)  # Username/handle
    
    # OAuth tokens (encrypted in production!)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    
    # Meta/Facebook specific fields
    page_id = Column(String, nullable=True)  # Facebook Page ID
    page_name = Column(String, nullable=True)  # Facebook Page name
    page_access_token = Column(Text, nullable=True)  # Page Access Token (never expires!)
    instagram_account_id = Column(String, nullable=True)  # Instagram Business account ID
    instagram_username = Column(String, nullable=True)  # Instagram username
    
    # Account status
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    business = relationship("Business", back_populates="social_accounts")
    published_posts = relationship("PublishedPost", back_populates="social_account", cascade="all, delete-orphan")
    scheduled_posts = relationship("ScheduledPost", back_populates="social_account", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SocialAccount {self.platform} - {self.platform_username}>"
