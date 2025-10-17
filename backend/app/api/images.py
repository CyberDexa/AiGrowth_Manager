"""
Image API Endpoints
Handles image upload, listing, deletion, and AI generation
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
from datetime import datetime
import math

from app.db.database import get_db
from app.models.image import Image
from app.schemas.image import (
    ImageResponse,
    ImageListResponse,
    ImageUploadResponse,
    ImageDeleteResponse,
    InstagramImageValidation,
    AIImageGenerateRequest,
    AIImageGenerateResponse
)
from app.services.image_storage import ImageStorageService
from app.services.ai_image_generator import AIImageGenerator

router = APIRouter(prefix="/images", tags=["images"])


@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(
    business_id: int = Query(..., description="Business ID"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload an image to Cloudinary and save metadata to database
    
    - **business_id**: ID of the business uploading the image
    - **file**: Image file (JPG, PNG, WebP, max 10MB)
    """
    try:
        # Upload to Cloudinary
        upload_result = await ImageStorageService.upload_image(
            file=file,
            business_id=business_id
        )
        
        # Create database record
        db_image = Image(
            business_id=business_id,
            original_filename=file.filename,
            storage_provider="cloudinary",
            storage_url=upload_result["url"],
            cloudinary_public_id=upload_result["public_id"],
            file_size_bytes=upload_result["size"],
            mime_type=file.content_type,
            width=upload_result["width"],
            height=upload_result["height"],
            ai_generated=False
        )
        
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        
        return ImageUploadResponse(
            success=True,
            message="Image uploaded successfully",
            image=ImageResponse.from_orm(db_image)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image: {str(e)}"
        )


@router.get("", response_model=ImageListResponse)
def list_images(
    business_id: int = Query(..., description="Business ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    ai_generated: Optional[bool] = Query(None, description="Filter by AI generated"),
    search: Optional[str] = Query(None, description="Search by filename"),
    db: Session = Depends(get_db)
):
    """
    List images for a business with pagination and filtering
    
    - **business_id**: ID of the business
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **ai_generated**: Filter by AI generated (optional)
    - **search**: Search by filename (optional)
    """
    try:
        # Build query
        query = db.query(Image).filter(
            and_(
                Image.business_id == business_id,
                Image.deleted_at.is_(None)
            )
        )
        
        # Apply filters
        if ai_generated is not None:
            query = query.filter(Image.ai_generated == ai_generated)
        
        if search:
            query = query.filter(Image.original_filename.ilike(f"%{search}%"))
        
        # Get total count
        total = query.count()
        
        # Calculate pagination
        total_pages = math.ceil(total / page_size)
        offset = (page - 1) * page_size
        
        # Get paginated results
        images = query.order_by(Image.created_at.desc()).offset(offset).limit(page_size).all()
        
        return ImageListResponse(
            images=[ImageResponse.from_orm(img) for img in images],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list images: {str(e)}"
        )


@router.get("/{image_id}", response_model=ImageResponse)
def get_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a single image by ID
    
    - **image_id**: ID of the image
    """
    image = db.query(Image).filter(
        and_(
            Image.id == image_id,
            Image.deleted_at.is_(None)
        )
    ).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return ImageResponse.from_orm(image)


@router.delete("/{image_id}", response_model=ImageDeleteResponse)
def delete_image(
    image_id: int,
    hard_delete: bool = Query(False, description="Permanently delete from storage"),
    db: Session = Depends(get_db)
):
    """
    Delete an image (soft delete by default, hard delete optional)
    
    - **image_id**: ID of the image
    - **hard_delete**: If true, permanently deletes from Cloudinary (default: false)
    """
    try:
        image = db.query(Image).filter(
            and_(
                Image.id == image_id,
                Image.deleted_at.is_(None)
            )
        ).first()
        
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        if hard_delete:
            # Delete from Cloudinary
            if image.cloudinary_public_id:
                ImageStorageService.delete_image(image.cloudinary_public_id)
            
            # Delete from database
            db.delete(image)
            message = "Image permanently deleted"
        else:
            # Soft delete
            image.deleted_at = datetime.utcnow()
            message = "Image deleted"
        
        db.commit()
        
        return ImageDeleteResponse(
            success=True,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete image: {str(e)}"
        )


@router.post("/validate/instagram", response_model=InstagramImageValidation)
def validate_instagram_image(
    image_id: int = Query(..., description="Image ID to validate"),
    db: Session = Depends(get_db)
):
    """
    Validate if an image meets Instagram requirements
    
    - **image_id**: ID of the image to validate
    
    Instagram Requirements:
    - Minimum: 320x320 pixels
    - Aspect ratio: 4:5 (portrait) to 1.91:1 (landscape)
    """
    image = db.query(Image).filter(
        and_(
            Image.id == image_id,
            Image.deleted_at.is_(None)
        )
    ).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    validation_result = ImageStorageService.validate_instagram_image(
        width=image.width,
        height=image.height
    )
    
    return InstagramImageValidation(**validation_result)


@router.get("/{image_id}/thumbnail")
def get_image_thumbnail(
    image_id: int,
    width: int = Query(200, ge=50, le=800, description="Thumbnail width"),
    height: int = Query(200, ge=50, le=800, description="Thumbnail height"),
    db: Session = Depends(get_db)
):
    """
    Get thumbnail URL for an image
    
    - **image_id**: ID of the image
    - **width**: Thumbnail width (default: 200, max: 800)
    - **height**: Thumbnail height (default: 200, max: 800)
    """
    image = db.query(Image).filter(
        and_(
            Image.id == image_id,
            Image.deleted_at.is_(None)
        )
    ).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    if not image.cloudinary_public_id:
        raise HTTPException(status_code=400, detail="Image does not have Cloudinary public ID")
    
    thumbnail_url = ImageStorageService.get_thumbnail_url(
        public_id=image.cloudinary_public_id,
        width=width,
        height=height
    )
    
    return {"thumbnail_url": thumbnail_url}


# ============================================
# AI IMAGE GENERATION ENDPOINTS
# ============================================

@router.post("/generate", response_model=AIImageGenerateResponse)
async def generate_image(
    request: AIImageGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate an image using AI through OpenRouter (DALL-E 3 and other models)
    
    - **prompt**: Text description of the image to generate (max 1000 chars)
    - **business_id**: ID of the business
    - **size**: Image size ('1024x1024', '1792x1024', '1024x1792')
    
    Returns job_id for status tracking and the generated image details
    """
    try:
        # Generate image
        result = await AIImageGenerator.generate_image(
            prompt=request.prompt,
            business_id=request.business_id,
            size=request.size
        )
        
        # Create database record
        db_image = Image(
            business_id=request.business_id,
            original_filename=f"ai_generated_{result['job_id'][:8]}.png",
            storage_provider="cloudinary",
            storage_url=result["image_url"],
            cloudinary_public_id=result["cloudinary_public_id"],
            file_size_bytes=0,  # Will be updated if needed
            mime_type="image/png",
            width=result["width"],
            height=result["height"],
            ai_generated=True,
            ai_prompt=request.prompt,
            ai_model=result.get("model", "openai/dall-e-3")
        )
        
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        
        return AIImageGenerateResponse(
            success=True,
            message="Image generated successfully",
            job_id=result["job_id"],
            image=ImageResponse.from_orm(db_image)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate image: {str(e)}"
        )


@router.get("/generate/status/{job_id}")
def get_generation_status(job_id: str):
    """
    Check status of an AI image generation job
    
    - **job_id**: Job ID returned from generate endpoint
    
    Returns current status, progress, and image details if completed
    """
    try:
        status = AIImageGenerator.get_generation_status(job_id)
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get generation status: {str(e)}"
        )


@router.get("/generate/sizes")
def get_available_sizes():
    """
    Get list of available image sizes for AI generation
    
    Returns available sizes with aspect ratios and cost estimates
    """
    return {
        "sizes": AIImageGenerator.get_available_sizes(),
        "note": "Costs shown are per image in USD"
    }


@router.post("/generate/estimate-cost")
def estimate_generation_cost(
    size: str = Query("1024x1024", description="Image size"),
    quality: str = Query("standard", description="Image quality")
):
    """
    Estimate cost for generating an image
    
    - **size**: Image size ('1024x1024', '1792x1024', '1024x1792')
    - **quality**: Image quality ('standard' or 'hd')
    
    Returns cost estimate in USD
    """
    return AIImageGenerator.estimate_cost(size=size, quality=quality)

