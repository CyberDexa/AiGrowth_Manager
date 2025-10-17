"""
Image Schemas for API Request/Response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class ImageBase(BaseModel):
    """Base image schema"""
    original_filename: str
    mime_type: str
    width: int
    height: int


class ImageCreate(ImageBase):
    """Schema for creating image"""
    business_id: int
    storage_provider: str = "cloudinary"
    storage_url: str
    cloudinary_public_id: Optional[str] = None
    file_size_bytes: int
    ai_generated: bool = False
    ai_prompt: Optional[str] = None
    ai_model: Optional[str] = None


class ImageUpdate(BaseModel):
    """Schema for updating image"""
    ai_prompt: Optional[str] = None
    ai_model: Optional[str] = None


class ImageResponse(ImageBase):
    """Schema for image response"""
    id: int
    business_id: int
    storage_provider: str
    storage_url: str
    cloudinary_public_id: Optional[str]
    file_size_bytes: int
    ai_generated: bool
    ai_prompt: Optional[str]
    ai_model: Optional[str]
    aspect_ratio: float
    size_mb: float
    created_at: datetime
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ImageListResponse(BaseModel):
    """Schema for paginated image list"""
    images: list[ImageResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ImageUploadResponse(BaseModel):
    """Schema for image upload response"""
    success: bool
    message: str
    image: Optional[ImageResponse] = None


class ImageDeleteResponse(BaseModel):
    """Schema for image deletion response"""
    success: bool
    message: str


class InstagramImageValidation(BaseModel):
    """Schema for Instagram image validation"""
    is_valid: bool
    warnings: list[str] = []
    dimensions: dict
    aspect_ratio: float


class AIImageGenerateRequest(BaseModel):
    """Schema for AI image generation request"""
    prompt: str = Field(..., min_length=1, max_length=1000)
    business_id: int
    size: str = Field(default="1024x1024", pattern="^(1024x1024|1792x1024|1024x1792)$")
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()


class AIImageGenerateResponse(BaseModel):
    """Schema for AI image generation response"""
    success: bool
    message: str
    job_id: Optional[str] = None
    image: Optional[ImageResponse] = None


class AIImageStatusResponse(BaseModel):
    """Schema for AI image generation status"""
    job_id: str
    status: str  # 'pending', 'processing', 'completed', 'failed'
    progress: Optional[int] = None  # 0-100
    image: Optional[ImageResponse] = None
    error: Optional[str] = None
