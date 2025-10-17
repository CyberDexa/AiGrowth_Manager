"""
Published Post Model

Tracks content published to social media platforms.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean, ARRAY, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class PublishedPost(Base):
    """
    Model for tracking published social media posts.
    
    Stores post content, platform details, publishing status,
    and engagement metrics for analytics.
    """
    __tablename__ = "published_posts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True, index=True)
    social_account_id = Column(Integer, ForeignKey("social_accounts.id"), nullable=False)
    
    # Content
    content_text = Column(Text, nullable=False)
    content_images = Column(ARRAY(Text), nullable=True)  # Future: array of image URLs
    content_links = Column(ARRAY(Text), nullable=True)   # Array of links shared
    
    # Platform Details
    platform = Column(String(50), nullable=False, index=True)  # 'linkedin', 'twitter', 'facebook'
    platform_post_id = Column(String(255), nullable=True)      # LinkedIn: 'urn:li:share:123'
    platform_post_url = Column(Text, nullable=True)             # Direct URL to post
    
    # Publishing Info
    status = Column(String(50), nullable=False, default="pending", index=True)  # pending, published, failed, scheduled
    scheduled_for = Column(TIMESTAMP, nullable=True, index=True)  # When to publish (if scheduled)
    published_at = Column(TIMESTAMP, nullable=True)               # When actually published
    
    # Error Tracking
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(TIMESTAMP, nullable=True)
    
    # Engagement Metrics (for future analytics)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    impressions_count = Column(Integer, default=0)
    last_metrics_sync = Column(TIMESTAMP, nullable=True)
    
    # Metadata
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    business = relationship("Business", back_populates="published_posts")
    strategy = relationship("Strategy", back_populates="published_posts")
    social_account = relationship("SocialAccount", back_populates="published_posts")
    analytics = relationship("PostAnalytics", back_populates="published_post", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PublishedPost(id={self.id}, platform={self.platform}, status={self.status})>"
