"""AnalyticsSummary model for aggregated analytics data."""

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, TIMESTAMP, Date, text
from sqlalchemy.orm import relationship
from datetime import datetime, date
from typing import Dict, Any

from app.db.database import Base


class AnalyticsSummary(Base):
    """Aggregated analytics data for time periods."""
    
    __tablename__ = "analytics_summaries"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Platform
    platform = Column(String(20), nullable=False)  # linkedin, twitter, facebook, instagram, or 'all'
    
    # Time Period
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly, yearly
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False, index=True)
    
    # Summary Metrics
    total_posts = Column(Integer, nullable=False, default=0, server_default="0")
    total_likes = Column(Integer, nullable=False, default=0, server_default="0")
    total_comments = Column(Integer, nullable=False, default=0, server_default="0")
    total_shares = Column(Integer, nullable=False, default=0, server_default="0")
    total_impressions = Column(Integer, nullable=False, default=0, server_default="0")
    total_reach = Column(Integer, nullable=False, default=0, server_default="0")
    total_clicks = Column(Integer, nullable=False, default=0, server_default="0")
    
    # Calculated Metrics
    avg_engagement_rate = Column(Numeric(5, 2), nullable=False, default=0.0, server_default="0.0")
    avg_impressions = Column(Integer, nullable=False, default=0, server_default="0")
    follower_growth = Column(Integer, nullable=False, default=0, server_default="0")
    
    # Best Performing
    best_post_id = Column(Integer, ForeignKey("published_posts.id", ondelete="SET NULL"), nullable=True)
    best_post_engagement_rate = Column(Numeric(5, 2), nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, server_default=text("NOW()"))
    updated_at = Column(TIMESTAMP, nullable=True, onupdate=datetime.utcnow)
    
    # Relationships
    business = relationship("Business", back_populates="analytics_summaries")
    best_post = relationship("PublishedPost", foreign_keys=[best_post_id])
    
    @property
    def total_engagement(self) -> int:
        """Calculate total engagement."""
        return self.total_likes + self.total_comments + self.total_shares
    
    @property
    def period_duration_days(self) -> int:
        """Calculate duration of the period in days."""
        if isinstance(self.period_start, date) and isinstance(self.period_end, date):
            return (self.period_end - self.period_start).days + 1
        return 0
    
    def calculate_avg_engagement_rate(self) -> float:
        """Calculate average engagement rate."""
        if self.total_impressions == 0:
            return 0.0
        return round((self.total_engagement / self.total_impressions) * 100, 2)
    
    def calculate_avg_impressions(self) -> int:
        """Calculate average impressions per post."""
        if self.total_posts == 0:
            return 0
        return round(self.total_impressions / self.total_posts)
    
    def update_calculated_metrics(self):
        """Update calculated metrics."""
        self.avg_engagement_rate = self.calculate_avg_engagement_rate()
        self.avg_impressions = self.calculate_avg_impressions()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "business_id": self.business_id,
            "platform": self.platform,
            "period_type": self.period_type,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "period_duration_days": self.period_duration_days,
            "total_posts": self.total_posts,
            "total_likes": self.total_likes,
            "total_comments": self.total_comments,
            "total_shares": self.total_shares,
            "total_impressions": self.total_impressions,
            "total_reach": self.total_reach,
            "total_clicks": self.total_clicks,
            "total_engagement": self.total_engagement,
            "avg_engagement_rate": float(self.avg_engagement_rate),
            "avg_impressions": self.avg_impressions,
            "follower_growth": self.follower_growth,
            "best_post_id": self.best_post_id,
            "best_post_engagement_rate": float(self.best_post_engagement_rate) if self.best_post_engagement_rate else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f"<AnalyticsSummary(id={self.id}, business_id={self.business_id}, platform={self.platform}, period={self.period_type}, posts={self.total_posts})>"
