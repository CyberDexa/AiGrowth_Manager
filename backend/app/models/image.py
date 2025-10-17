"""
Image Model
Stores metadata for uploaded and AI-generated images
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Image(Base):
    """Image model for storing image metadata"""
    
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    
    # File information
    original_filename = Column(String(255), nullable=False)
    storage_provider = Column(String(20), nullable=False, default="cloudinary")  # 'cloudinary' or 's3'
    storage_url = Column(Text, nullable=False)  # Full CDN URL
    cloudinary_public_id = Column(String(255), nullable=True)  # Cloudinary-specific ID
    
    # File metadata
    file_size_bytes = Column(BigInteger, nullable=False)
    mime_type = Column(String(50), nullable=False)  # image/jpeg, image/png, etc.
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    
    # AI Generation metadata
    ai_generated = Column(Boolean, default=False, nullable=False)
    ai_prompt = Column(Text, nullable=True)  # Store the prompt if AI-generated
    ai_model = Column(String(50), nullable=True)  # e.g., 'dall-e-3', 'stable-diffusion'
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    business = relationship("Business", back_populates="images")
    
    def __repr__(self):
        return f"<Image(id={self.id}, filename='{self.original_filename}', business_id={self.business_id})>"
    
    @property
    def is_deleted(self) -> bool:
        """Check if image is soft-deleted"""
        return self.deleted_at is not None
    
    @property
    def aspect_ratio(self) -> float:
        """Calculate aspect ratio"""
        if self.height == 0:
            return 0
        return self.width / self.height
    
    @property
    def size_mb(self) -> float:
        """Get file size in MB"""
        return self.file_size_bytes / (1024 * 1024)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "business_id": self.business_id,
            "original_filename": self.original_filename,
            "storage_provider": self.storage_provider,
            "storage_url": self.storage_url,
            "cloudinary_public_id": self.cloudinary_public_id,
            "file_size_bytes": self.file_size_bytes,
            "mime_type": self.mime_type,
            "width": self.width,
            "height": self.height,
            "ai_generated": self.ai_generated,
            "ai_prompt": self.ai_prompt,
            "ai_model": self.ai_model,
            "aspect_ratio": self.aspect_ratio,
            "size_mb": round(self.size_mb, 2),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None
        }
