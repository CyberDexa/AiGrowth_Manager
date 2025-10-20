"""
Business model - stores business information from onboarding
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.database import Base


class Business(Base):
    __tablename__ = "businesses"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to user
    user_id = Column(String, ForeignKey("users.clerk_id"), nullable=False)
    
    # Business information (from onboarding)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    target_audience = Column(Text, nullable=True)
    marketing_goals = Column(Text, nullable=True)
    
    # Industry and size (optional, for future use)
    industry = Column(String, nullable=True)
    company_size = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="businesses")
    strategies = relationship("Strategy", back_populates="business", cascade="all, delete-orphan")
    social_accounts = relationship("SocialAccount", back_populates="business", cascade="all, delete-orphan")
    content = relationship("Content", back_populates="business", cascade="all, delete-orphan")
    metrics = relationship("BusinessMetrics", back_populates="business", cascade="all, delete-orphan")
    published_posts = relationship("PublishedPost", back_populates="business", cascade="all, delete-orphan")
    scheduled_posts = relationship("ScheduledPost", back_populates="business", cascade="all, delete-orphan")
    images = relationship("Image", back_populates="business", cascade="all, delete-orphan")
    post_analytics = relationship("PostAnalytics", back_populates="business", cascade="all, delete-orphan")
    analytics_summaries = relationship("AnalyticsSummary", back_populates="business", cascade="all, delete-orphan")
    content_templates = relationship("ContentTemplate", back_populates="business", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Business {self.name}>"
