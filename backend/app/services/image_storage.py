"""
Image Storage Service using Cloudinary
Handles image upload, deletion, and URL generation
"""
import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Optional, Dict, Any
from fastapi import UploadFile, HTTPException
import os
from app.core.config import settings

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

# Allowed image formats
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

class ImageStorageService:
    """Service for managing image uploads and storage via Cloudinary"""
    
    @staticmethod
    def validate_image(file: UploadFile) -> None:
        """
        Validate image file type and size
        
        Args:
            file: Uploaded file object
            
        Raises:
            HTTPException: If validation fails
        """
        # Check file type
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
            )
        
        # Check file size (if available)
        if hasattr(file, 'size') and file.size:
            if file.size > MAX_FILE_SIZE_BYTES:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB"
                )
    
    @staticmethod
    async def upload_image(
        file: UploadFile,
        business_id: int,
        folder: str = "ai-growth-manager"
    ) -> Dict[str, Any]:
        """
        Upload image to Cloudinary
        
        Args:
            file: Uploaded file object
            business_id: ID of the business
            folder: Cloudinary folder name
            
        Returns:
            Dict containing upload result with URL, public_id, dimensions, etc.
            
        Raises:
            HTTPException: If upload fails
        """
        try:
            # Validate image
            ImageStorageService.validate_image(file)
            
            # Read file contents
            contents = await file.read()
            
            # Upload to Cloudinary with business_id in folder path
            upload_result = cloudinary.uploader.upload(
                contents,
                folder=f"{folder}/business_{business_id}",
                resource_type="image",
                transformation=[
                    {'quality': 'auto:good'},  # Auto quality optimization
                    {'fetch_format': 'auto'}   # Auto format selection (WebP if supported)
                ]
            )
            
            # Reset file pointer for potential reuse
            await file.seek(0)
            
            return {
                "url": upload_result.get("secure_url"),
                "public_id": upload_result.get("public_id"),
                "width": upload_result.get("width"),
                "height": upload_result.get("height"),
                "format": upload_result.get("format"),
                "size": upload_result.get("bytes"),
                "created_at": upload_result.get("created_at")
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload image: {str(e)}"
            )
    
    @staticmethod
    def delete_image(public_id: str) -> Dict[str, Any]:
        """
        Delete image from Cloudinary
        
        Args:
            public_id: Cloudinary public ID of the image
            
        Returns:
            Dict with deletion result
            
        Raises:
            HTTPException: If deletion fails
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            
            if result.get('result') != 'ok':
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to delete image: {result.get('result')}"
                )
            
            return {"status": "deleted", "public_id": public_id}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete image: {str(e)}"
            )
    
    @staticmethod
    def get_thumbnail_url(public_id: str, width: int = 200, height: int = 200) -> str:
        """
        Generate thumbnail URL for an image
        
        Args:
            public_id: Cloudinary public ID
            width: Thumbnail width
            height: Thumbnail height
            
        Returns:
            Thumbnail URL
        """
        return cloudinary.CloudinaryImage(public_id).build_url(
            width=width,
            height=height,
            crop="fill",
            quality="auto:good",
            fetch_format="auto"
        )
    
    @staticmethod
    def get_optimized_url(
        public_id: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        quality: str = "auto:good"
    ) -> str:
        """
        Generate optimized image URL with transformations
        
        Args:
            public_id: Cloudinary public ID
            width: Optional width
            height: Optional height
            quality: Image quality setting
            
        Returns:
            Optimized image URL
        """
        transformations = {
            "quality": quality,
            "fetch_format": "auto"
        }
        
        if width:
            transformations["width"] = width
        if height:
            transformations["height"] = height
        if width or height:
            transformations["crop"] = "limit"  # Don't upscale, only downscale
        
        return cloudinary.CloudinaryImage(public_id).build_url(**transformations)
    
    @staticmethod
    def validate_instagram_image(width: int, height: int) -> Dict[str, Any]:
        """
        Validate image dimensions for Instagram
        
        Instagram requirements:
        - Minimum: 320x320 pixels
        - Aspect ratio: 4:5 (portrait) to 1.91:1 (landscape)
        
        Args:
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            Dict with validation result and messages
        """
        MIN_DIMENSION = 320
        MIN_ASPECT_RATIO = 0.8  # 4:5
        MAX_ASPECT_RATIO = 1.91  # 1.91:1
        
        is_valid = True
        warnings = []
        
        # Check minimum dimensions
        if width < MIN_DIMENSION or height < MIN_DIMENSION:
            is_valid = False
            warnings.append(
                f"Image too small. Minimum dimensions: {MIN_DIMENSION}x{MIN_DIMENSION}px"
            )
        
        # Check aspect ratio
        aspect_ratio = width / height if height > 0 else 0
        if aspect_ratio < MIN_ASPECT_RATIO or aspect_ratio > MAX_ASPECT_RATIO:
            is_valid = False
            warnings.append(
                f"Invalid aspect ratio ({aspect_ratio:.2f}). "
                f"Instagram requires between {MIN_ASPECT_RATIO} (4:5) and {MAX_ASPECT_RATIO} (1.91:1)"
            )
        
        return {
            "is_valid": is_valid,
            "warnings": warnings,
            "dimensions": {"width": width, "height": height},
            "aspect_ratio": aspect_ratio
        }
    
    @staticmethod
    async def upload_from_url(
        image_url: str,
        business_id: int,
        folder: str = "ai-growth-manager"
    ) -> Dict[str, Any]:
        """
        Upload image from URL (useful for AI-generated images)
        
        Args:
            image_url: URL of the image to upload
            business_id: ID of the business
            folder: Cloudinary folder name
            
        Returns:
            Dict containing upload result
        """
        try:
            upload_result = cloudinary.uploader.upload(
                image_url,
                folder=f"{folder}/business_{business_id}/ai-generated",
                resource_type="image",
                transformation=[
                    {'quality': 'auto:good'},
                    {'fetch_format': 'auto'}
                ]
            )
            
            return {
                "url": upload_result.get("secure_url"),
                "public_id": upload_result.get("public_id"),
                "width": upload_result.get("width"),
                "height": upload_result.get("height"),
                "format": upload_result.get("format"),
                "size": upload_result.get("bytes"),
                "created_at": upload_result.get("created_at")
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload image from URL: {str(e)}"
            )
