from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from app.db.database import Base


class ContentTemplate(Base):
    __tablename__ = "content_templates"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    platform = Column(String(50), nullable=True, index=True)
    template_structure = Column(Text, nullable=False)
    placeholders = Column(JSON, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False, index=True)
    use_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    business = relationship("Business", back_populates="content_templates")
