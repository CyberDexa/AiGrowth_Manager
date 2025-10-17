"""
AI Image Generation Service using OpenRouter
Generates images from text prompts and saves them to Cloudinary
Supports multiple image generation models through OpenRouter
"""
import httpx
from typing import Dict, Any, Optional
from fastapi import HTTPException
import uuid
from datetime import datetime
import json

from app.core.config import settings
from app.services.image_storage import ImageStorageService

# In-memory job tracking (replace with Redis in production)
generation_jobs: Dict[str, Dict[str, Any]] = {}


class AIImageGenerator:
    """Service for generating images using AI through OpenRouter"""
    
    @staticmethod
    def validate_openrouter_configured() -> None:
        """Check if OpenRouter API key is configured"""
        if not settings.OPENROUTER_API_KEY or settings.OPENROUTER_API_KEY == "":
            raise HTTPException(
                status_code=503,
                detail="OpenRouter API key not configured. Please add OPENROUTER_API_KEY to .env"
            )
    
    @staticmethod
    async def generate_image(
        prompt: str,
        business_id: int,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid"
    ) -> Dict[str, Any]:
        """
        Generate image using OpenRouter (supports multiple image models)
        
        Args:
            prompt: Text description of the image
            business_id: ID of the business
            size: Image size ('1024x1024', '1792x1024', '1024x1792')
            quality: Image quality ('standard' or 'hd')
            style: Image style ('vivid' or 'natural')
            
        Returns:
            Dict with job_id and image details
            
        Raises:
            HTTPException: If generation fails
        """
        try:
            # Validate OpenRouter is configured
            AIImageGenerator.validate_openrouter_configured()
            
            # Create job ID
            job_id = str(uuid.uuid4())
            
            # Initialize job status
            generation_jobs[job_id] = {
                "status": "processing",
                "progress": 0,
                "prompt": prompt,
                "business_id": business_id,
                "created_at": datetime.utcnow().isoformat(),
                "image_url": None,
                "error": None
            }
            
            # Generate image using OpenRouter
            # OpenRouter supports image generation through chat/completions with modalities
            try:
                headers = {
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://ai-growth-manager.com",
                    "X-Title": "AI Growth Manager"
                }
                
                # OpenRouter supports various image generation models
                # Using Google Gemini 2.5 Flash Image (supports image generation)
                model = "google/gemini-2.5-flash-image"
                
                # Build the prompt with size and quality specifications
                enhanced_prompt = f"{prompt}"
                if quality == "hd":
                    enhanced_prompt += " (high quality, detailed, 4k)"
                if style == "vivid":
                    enhanced_prompt += " (vibrant colors, vivid)"
                elif style == "natural":
                    enhanced_prompt += " (natural, realistic)"
                
                payload = {
                    "model": model,
                    "messages": [
                        {
                            "role": "user",
                            "content": enhanced_prompt
                        }
                    ],
                    "modalities": ["image", "text"]
                }
                
                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    response.raise_for_status()
                    result = response.json()
                
                # Update job progress
                generation_jobs[job_id]["progress"] = 50
                
                # Extract image URL from response
                # OpenRouter returns images in choices[0].message.images
                if "choices" in result and len(result["choices"]) > 0:
                    message = result["choices"][0].get("message", {})
                    images = message.get("images", [])
                    
                    if images and len(images) > 0:
                        # Get the base64 data URL
                        image_data = images[0].get("image_url", {}).get("url", "")
                        if not image_data:
                            raise ValueError("No image URL in response")
                        
                        # Extract text response if available
                        revised_prompt = message.get("content", prompt)
                    else:
                        raise ValueError("No images in response")
                else:
                    raise ValueError("No choices in response")
                
                # Upload to Cloudinary (for permanent storage)
                # Handle base64 data URL from OpenRouter
                upload_result = await ImageStorageService.upload_from_url(
                    image_url=image_data,
                    business_id=business_id
                )
                
                # Update job status
                generation_jobs[job_id].update({
                    "status": "completed",
                    "progress": 100,
                    "image_url": upload_result["url"],
                    "cloudinary_public_id": upload_result["public_id"],
                    "width": upload_result["width"],
                    "height": upload_result["height"],
                    "revised_prompt": revised_prompt,
                    "original_openrouter_response": image_data[:100] + "...",  # Store truncated base64
                    "completed_at": datetime.utcnow().isoformat(),
                    "model": model
                })
                
                return {
                    "job_id": job_id,
                    "status": "completed",
                    "image_url": upload_result["url"],
                    "cloudinary_public_id": upload_result["public_id"],
                    "width": upload_result["width"],
                    "height": upload_result["height"],
                    "revised_prompt": revised_prompt,
                    "model": model
                }
                
            except httpx.HTTPStatusError as e:
                error_detail = f"OpenRouter API error: {e.response.status_code}"
                try:
                    error_data = e.response.json()
                    error_detail += f" - {error_data.get('error', {}).get('message', str(e))}"
                except:
                    error_detail += f" - {str(e)}"
                
                # Update job with error
                generation_jobs[job_id].update({
                    "status": "failed",
                    "progress": 0,
                    "error": error_detail,
                    "failed_at": datetime.utcnow().isoformat()
                })
                
                raise HTTPException(
                    status_code=500,
                    detail=f"Image generation failed: {error_detail}"
                )
            
            except Exception as e:
                # Update job with error
                generation_jobs[job_id].update({
                    "status": "failed",
                    "progress": 0,
                    "error": str(e),
                    "failed_at": datetime.utcnow().isoformat()
                })
                
                raise HTTPException(
                    status_code=500,
                    detail=f"Image generation failed: {str(e)}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start image generation: {str(e)}"
            )
    
    @staticmethod
    def get_generation_status(job_id: str) -> Dict[str, Any]:
        """
        Get status of an image generation job
        
        Args:
            job_id: Job ID returned from generate_image
            
        Returns:
            Dict with job status and progress
            
        Raises:
            HTTPException: If job not found
        """
        job = generation_jobs.get(job_id)
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Generation job '{job_id}' not found"
            )
        
        return {
            "job_id": job_id,
            "status": job["status"],
            "progress": job.get("progress", 0),
            "prompt": job.get("prompt"),
            "image_url": job.get("image_url"),
            "cloudinary_public_id": job.get("cloudinary_public_id"),
            "revised_prompt": job.get("revised_prompt"),
            "error": job.get("error"),
            "created_at": job.get("created_at"),
            "completed_at": job.get("completed_at"),
            "width": job.get("width"),
            "height": job.get("height")
        }
    
    @staticmethod
    def cleanup_old_jobs(max_age_hours: int = 24) -> int:
        """
        Clean up old completed/failed jobs
        
        Args:
            max_age_hours: Maximum age in hours for jobs to keep
            
        Returns:
            Number of jobs cleaned up
        """
        current_time = datetime.utcnow()
        cleaned_count = 0
        
        jobs_to_delete = []
        for job_id, job in generation_jobs.items():
            created_at = datetime.fromisoformat(job.get("created_at", current_time.isoformat()))
            age_hours = (current_time - created_at).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                jobs_to_delete.append(job_id)
        
        for job_id in jobs_to_delete:
            del generation_jobs[job_id]
            cleaned_count += 1
        
        return cleaned_count
    
    @staticmethod
    def estimate_cost(size: str = "1024x1024", quality: str = "standard") -> Dict[str, Any]:
        """
        Estimate cost for image generation through OpenRouter
        
        Google Gemini 2.5 Flash Image Pricing (through OpenRouter):
        - Output images: $0.03 per 1000 images
        - Input tokens: $0.30 per 1M tokens (for prompt processing)
        - Very cost-effective compared to DALL-E 3
        
        Args:
            size: Image size (aspect ratio can be controlled via API)
            quality: Image quality ('standard' or 'hd')
            
        Returns:
            Dict with cost estimate
        """
        # Gemini 2.5 Flash Image pricing
        cost_per_image = 0.00003  # $0.03 per 1000 images
        prompt_cost_estimate = 0.0001  # Rough estimate for prompt tokens
        
        total_cost = cost_per_image + prompt_cost_estimate
        
        return {
            "size": size,
            "quality": quality,
            "cost_per_image": total_cost,
            "image_cost": cost_per_image,
            "prompt_cost_estimate": prompt_cost_estimate,
            "currency": "USD",
            "model": "google/gemini-2.5-flash-image",
            "provider": "OpenRouter",
            "note": "Very cost-effective: ~$0.03 per 1000 images. Costs include image generation + prompt processing"
        }
    
    @staticmethod
    def get_available_sizes() -> list[Dict[str, Any]]:
        """
        Get list of available image sizes
        
        Note: Gemini 2.5 Flash Image supports aspect ratio control via API parameters
        
        Returns:
            List of available sizes with details
        """
        return [
            {
                "size": "1024x1024",
                "aspect_ratio": "1:1",
                "description": "Square format (Instagram, Twitter)",
                "cost": 0.00013
            },
            {
                "size": "1792x1024",
                "aspect_ratio": "16:9",
                "description": "Landscape format (Twitter header, LinkedIn)",
                "cost": 0.00013
            },
            {
                "size": "1024x1792",
                "aspect_ratio": "9:16",
                "description": "Portrait format (Instagram Stories)",
                "cost": 0.00013
            }
        ]
