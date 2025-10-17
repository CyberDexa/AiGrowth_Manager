"""PostAnalytics model for storing post performance metrics."""

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, TIMESTAMP, Text, text
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any

from app.db.database import Base


class PostAnalytics(Base):
    """PostAnalytics model for storing post performance metrics"""
    
    __tablename__ = "post_analytics"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    published_post_id = Column(Integer, ForeignKey("published_posts.id", ondelete="CASCADE"), nullable=False, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Platform
    platform = Column(String(20), nullable=False, index=True)  # linkedin, twitter, facebook, instagram
    
    # Engagement Metrics
    likes_count = Column(Integer, nullable=False, default=0, server_default="0")
    comments_count = Column(Integer, nullable=False, default=0, server_default="0")
    shares_count = Column(Integer, nullable=False, default=0, server_default="0")
    reactions_count = Column(Integer, nullable=False, default=0, server_default="0")  # Facebook reactions
    retweets_count = Column(Integer, nullable=False, default=0, server_default="0")  # Twitter specific
    quote_tweets_count = Column(Integer, nullable=False, default=0, server_default="0")  # Twitter specific
    
    # Reach Metrics
    impressions = Column(Integer, nullable=False, default=0, server_default="0")
    reach = Column(Integer, nullable=False, default=0, server_default="0")
    clicks = Column(Integer, nullable=False, default=0, server_default="0")
    
    # Video Metrics (optional)
    video_views = Column(Integer, nullable=False, default=0, server_default="0")
    video_watch_time = Column(Integer, nullable=False, default=0, server_default="0")  # seconds
    
    # Calculated Metrics
    engagement_rate = Column(Numeric(5, 2), nullable=False, default=0.0, server_default="0.0")  # (likes+comments+shares)/impressions * 100
    click_through_rate = Column(Numeric(5, 2), nullable=False, default=0.0, server_default="0.0")  # clicks/impressions * 100
    
    # Metadata
    fetched_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    platform_post_id = Column(String(255), nullable=True)  # Platform's internal post ID
    platform_post_url = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, server_default=text("NOW()"))
    updated_at = Column(TIMESTAMP, nullable=True, onupdate=datetime.utcnow)
    
    # Relationships
    published_post = relationship("PublishedPost", back_populates="analytics")
    business = relationship("Business", back_populates="post_analytics")
    
    @property
    def total_engagement(self) -> int:
        """Calculate total engagement (likes + comments + shares)."""
        return self.likes_count + self.comments_count + self.shares_count
    
    @property
    def total_interactions(self) -> int:
        """Calculate total interactions including reactions and retweets."""
        return (self.likes_count + self.comments_count + self.shares_count + 
                self.reactions_count + self.retweets_count + self.quote_tweets_count)
    
    def calculate_engagement_rate(self) -> float:
        """Calculate engagement rate as percentage."""
        if self.impressions == 0:
            return 0.0
        return round((self.total_engagement / self.impressions) * 100, 2)
    
    def calculate_click_through_rate(self) -> float:
        """Calculate click-through rate as percentage."""
        if self.impressions == 0:
            return 0.0
        return round((self.clicks / self.impressions) * 100, 2)
    
    def update_calculated_metrics(self):
        """Update engagement_rate and click_through_rate."""
        self.engagement_rate = self.calculate_engagement_rate()
        self.click_through_rate = self.calculate_click_through_rate()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "published_post_id": self.published_post_id,
            "business_id": self.business_id,
            "platform": self.platform,
            "likes_count": self.likes_count,
            "comments_count": self.comments_count,
            "shares_count": self.shares_count,
            "reactions_count": self.reactions_count,
            "retweets_count": self.retweets_count,
            "quote_tweets_count": self.quote_tweets_count,
            "impressions": self.impressions,
            "reach": self.reach,
            "clicks": self.clicks,
            "video_views": self.video_views,
            "video_watch_time": self.video_watch_time,
            "engagement_rate": float(self.engagement_rate),
            "click_through_rate": float(self.click_through_rate),
            "total_engagement": self.total_engagement,
            "total_interactions": self.total_interactions,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
            "platform_post_id": self.platform_post_id,
            "platform_post_url": self.platform_post_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f"<PostAnalytics(id={self.id}, post_id={self.published_post_id}, platform={self.platform}, engagement_rate={self.engagement_rate}%)>"
