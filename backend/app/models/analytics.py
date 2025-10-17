"""
Analytics models for tracking content performance metrics
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class ContentMetrics(Base):
    """
    Stores performance metrics for content items
    """
    __tablename__ = "content_metrics"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.id", ondelete="CASCADE"), nullable=False)
    
    # Engagement metrics
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    
    # Calculated metrics
    engagement_rate = Column(Float, default=0.0)  # (likes + shares + comments) / views * 100
    click_through_rate = Column(Float, default=0.0)  # clicks / views * 100
    
    # Metadata
    measured_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    platform_data = Column(JSON, nullable=True)  # Store platform-specific extra data
    
    # Relationships
    content = relationship("Content", back_populates="metrics")

    def calculate_engagement_rate(self):
        """Calculate engagement rate percentage"""
        if self.views > 0:
            total_engagement = (self.likes or 0) + (self.shares or 0) + (self.comments or 0)
            self.engagement_rate = (total_engagement / self.views) * 100
        else:
            self.engagement_rate = 0.0
    
    def calculate_ctr(self):
        """Calculate click-through rate percentage"""
        if self.views > 0:
            self.click_through_rate = ((self.clicks or 0) / self.views) * 100
        else:
            self.click_through_rate = 0.0


class BusinessMetrics(Base):
    """
    Stores aggregated metrics for businesses over time
    """
    __tablename__ = "business_metrics"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    
    # Aggregated metrics
    total_posts = Column(Integer, default=0)
    total_reach = Column(Integer, default=0)
    total_engagement = Column(Integer, default=0)
    avg_engagement_rate = Column(Float, default=0.0)
    
    # Platform breakdown (JSON)
    platform_breakdown = Column(JSON, nullable=True)  # {"linkedin": {...}, "twitter": {...}}
    
    # Time period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    business = relationship("Business", back_populates="metrics")
