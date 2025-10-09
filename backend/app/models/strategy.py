"""
Strategy model - stores AI-generated marketing strategies
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship

from app.db.database import Base


class Strategy(Base):
    __tablename__ = "strategies"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to business
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    
    # Strategy details
    title = Column(String, nullable=False)
    overview = Column(Text, nullable=True)
    target_audience_analysis = Column(Text, nullable=True)
    content_pillars = Column(JSON, nullable=True)  # Array of content themes
    posting_frequency = Column(JSON, nullable=True)  # Dict of platform: frequency
    
    # AI generation metadata
    ai_model = Column(String, default="gpt-4")
    prompt_version = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    business = relationship("Business", back_populates="strategies")
    
    def __repr__(self):
        return f"<Strategy {self.title}>"
