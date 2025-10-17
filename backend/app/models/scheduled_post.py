"""
Scheduled Post Model

Tracks posts scheduled for future publishing.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


class ScheduledPost(Base):
    """
    Model for scheduled social media posts.
    
    Stores post content, scheduling info, and platform details
    for future publishing via Celery tasks.
    """
    __tablename__ = "scheduled_posts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    social_account_id = Column(Integer, ForeignKey("social_accounts.id"), nullable=False)
    
    # Content
    content_text = Column(Text, nullable=False)
    platform_params = Column(JSON, nullable=True)  # Platform-specific parameters (image_url, visibility, etc.)
    
    # Platform Details
    platform = Column(String(50), nullable=False, index=True)  # 'linkedin', 'twitter', 'meta'
    
    # Scheduling Info
    scheduled_for = Column(TIMESTAMP, nullable=False, index=True)  # When to publish
    status = Column(String(50), nullable=False, default="pending", index=True)  # pending, publishing, published, failed, cancelled
    
    # Publishing Results (populated after publishing)
    published_post_id = Column(Integer, ForeignKey("published_posts.id"), nullable=True)
    platform_post_id = Column(String(255), nullable=True)
    platform_post_url = Column(Text, nullable=True)
    
    # Error Tracking
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(TIMESTAMP, nullable=True)
    
    # Celery Task ID (for cancellation)
    celery_task_id = Column(String(255), nullable=True, index=True)
    
    # Metadata
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    published_at = Column(TIMESTAMP, nullable=True)  # Actual publish time
    
    # Relationships
    business = relationship("Business", back_populates="scheduled_posts")
    social_account = relationship("SocialAccount", back_populates="scheduled_posts")
    published_post = relationship("PublishedPost", foreign_keys=[published_post_id], uselist=False)

    def __repr__(self):
        return f"<ScheduledPost(id={self.id}, platform={self.platform}, status={self.status}, scheduled_for={self.scheduled_for})>"
