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
    
    # Account status
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    business = relationship("Business", back_populates="social_accounts")
    
    def __repr__(self):
        return f"<SocialAccount {self.platform} - {self.platform_username}>"
