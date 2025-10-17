"""
Content model - stores generated social media posts
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Enum, Boolean
from sqlalchemy.orm import relationship
import enum

from app.db.database import Base


class Platform(str, enum.Enum):
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"


class ContentType(str, enum.Enum):
    POST = "post"
    THREAD = "thread"
    ARTICLE = "article"
    STORY = "story"


class ContentTone(str, enum.Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    EDUCATIONAL = "educational"
    PROMOTIONAL = "promotional"
    INSPIRATIONAL = "inspirational"


class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"


class Content(Base):
    __tablename__ = "content"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to business
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    
    # Content details
    platform = Column(Enum(Platform), nullable=False)
    content_type = Column(Enum(ContentType), default=ContentType.POST)
    tone = Column(Enum(ContentTone), default=ContentTone.PROFESSIONAL)
    text = Column(Text, nullable=False)
    media_urls = Column(Text, nullable=True)  # JSON string of URLs
    hashtags = Column(Text, nullable=True)  # Comma-separated hashtags
    
    # Scheduling
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT, nullable=False)
    scheduled_for = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    
    # External IDs (after posting)
    external_id = Column(String, nullable=True)  # Platform's post ID
    external_url = Column(String, nullable=True)  # Link to the post
    
    # AI generation
    ai_generated = Column(Boolean, default=True)
    ai_model = Column(String, default="gpt-4")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    business = relationship("Business", back_populates="content")
    metrics = relationship("ContentMetrics", back_populates="content", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Content {self.platform.value} - {self.status.value}>"
