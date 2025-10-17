"""
Meta (Facebook/Instagram) Publisher Service

This module implements publishing functionality for Meta platforms
(Facebook Pages and Instagram Business/Creator accounts) using the Graph API.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
import httpx
from app.services.publishing.base_publisher import BasePublisher, PublishResult

try:
    import sentry_sdk
except ImportError:
    sentry_sdk = None

logger = logging.getLogger(__name__)


class MetaPublisher(BasePublisher):
    """
    Meta (Facebook/Instagram) publisher implementation using Graph API.
    
    Features:
    - Facebook Page posts
    - Instagram posts (feed and stories)
    - Image and video support
    - Link previews
    - Comprehensive error handling
    """
    
    # Meta Graph API endpoints (v18.0)
    GRAPH_API_VERSION = "v18.0"
    GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
    
    # Character limits
    MAX_FACEBOOK_POST_LENGTH = 63206  # Facebook allows very long posts
    MAX_INSTAGRAM_CAPTION_LENGTH = 2200
    
    def __init__(self):
        super().__init__(platform="meta")
    
    def get_character_limit(self, platform_type: str = "facebook") -> int:
        """Get character limit based on platform type."""
        if platform_type == "instagram":
            return self.MAX_INSTAGRAM_CAPTION_LENGTH
        return self.MAX_FACEBOOK_POST_LENGTH
    
    def validate_content(self, content: str, **kwargs) -> tuple[bool, Optional[str]]:
        """
        Validate post content for Meta platforms.
        
        Args:
            content: The post content to validate
            **kwargs: Additional validation parameters
                - platform_type: 'facebook' or 'instagram'
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not content or not content.strip():
            return False, "Post content cannot be empty"
        
        platform_type = kwargs.get('platform_type', 'facebook')
        
        if platform_type == 'instagram' and len(content) > self.MAX_INSTAGRAM_CAPTION_LENGTH:
            return False, f"Instagram caption exceeds {self.MAX_INSTAGRAM_CAPTION_LENGTH} character limit"
        
        if platform_type == 'facebook' and len(content) > self.MAX_FACEBOOK_POST_LENGTH:
            return False, f"Facebook post exceeds {self.MAX_FACEBOOK_POST_LENGTH} character limit"
        
        return True, None
    
    async def _publish_facebook_page(
        self,
        content: str,
        page_id: str,
        access_token: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Publish a post to a Facebook Page.
        
        Args:
            content: Post message
            page_id: Facebook Page ID
            access_token: Page access token
            **kwargs: Additional parameters
                - link: URL to share
                - published: Whether to publish immediately (default: True)
        
        Returns:
            API response with post ID
        
        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        if sentry_sdk:
            sentry_sdk.add_breadcrumb(
                category="meta.api",
                message=f"Publishing to Facebook Page {page_id}",
                level="info"
            )
        
        # Build post data
        post_data = {
            "message": content,
            "access_token": access_token
        }
        
        # Add optional link
        if 'link' in kwargs:
            post_data['link'] = kwargs['link']
        
        # Published status (default: True)
        post_data['published'] = kwargs.get('published', True)
        
        # Post to Facebook Page feed
        url = f"{self.GRAPH_API_BASE}/{page_id}/feed"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, data=post_data)
            response.raise_for_status()
        
        return response.json()
    
    async def _publish_instagram(
        self,
        content: str,
        instagram_account_id: str,
        access_token: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Publish a post to Instagram Business/Creator account.
        
        Instagram publishing is a 2-step process:
        1. Create a media container
        2. Publish the container
        
        Args:
            content: Post caption
            instagram_account_id: Instagram Business Account ID
            access_token: Access token with instagram_content_publish permission
            **kwargs: Additional parameters
                - image_url: URL of image to post (required for feed posts)
                - media_type: 'IMAGE' or 'VIDEO' (default: IMAGE)
        
        Returns:
            API response with post ID
        
        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        if sentry_sdk:
            sentry_sdk.add_breadcrumb(
                category="meta.api",
                message=f"Publishing to Instagram account {instagram_account_id}",
                level="info"
            )
        
        image_url = kwargs.get('image_url')
        if not image_url:
            raise ValueError("image_url is required for Instagram posts")
        
        # Step 1: Create media container
        media_type = kwargs.get('media_type', 'IMAGE')
        
        container_data = {
            "access_token": access_token,
            "caption": content
        }
        
        if media_type == 'IMAGE':
            container_data['image_url'] = image_url
        elif media_type == 'VIDEO':
            container_data['video_url'] = image_url
            container_data['media_type'] = 'VIDEO'
        
        container_url = f"{self.GRAPH_API_BASE}/{instagram_account_id}/media"
        
        async with httpx.AsyncClient(timeout=60.0) as client:  # Longer timeout for media processing
            # Create container
            container_response = await client.post(container_url, data=container_data)
            container_response.raise_for_status()
            container_id = container_response.json().get('id')
            
            if not container_id:
                raise ValueError("Failed to create Instagram media container")
            
            logger.info(
                "Instagram media container created",
                extra={
                    "event_type": "instagram_container_created",
                    "container_id": container_id
                }
            )
            
            # Step 2: Publish container
            publish_data = {
                "creation_id": container_id,
                "access_token": access_token
            }
            
            publish_url = f"{self.GRAPH_API_BASE}/{instagram_account_id}/media_publish"
            
            publish_response = await client.post(publish_url, data=publish_data)
            publish_response.raise_for_status()
            
            return publish_response.json()
    
    async def publish(
        self,
        content: str,
        access_token: str,
        **kwargs
    ) -> PublishResult:
        """
        Publish content to Meta platforms (Facebook or Instagram).
        
        Args:
            content: The post content
            access_token: Decrypted OAuth access token
            **kwargs: Platform-specific parameters
                - platform_type: 'facebook' or 'instagram' (required)
                - page_id: Facebook Page ID (required for Facebook)
                - instagram_account_id: Instagram Business Account ID (required for Instagram)
                - image_url: Image URL (required for Instagram)
                - link: URL to share (optional for Facebook)
        
        Returns:
            PublishResult with post ID and URL
        """
        if sentry_sdk:
            sentry_sdk.add_breadcrumb(
                category="meta.publish",
                message="Starting Meta publish",
                level="info"
            )
        
        content_preview = content[:100] + "..." if len(content) > 100 else content
        platform_type = kwargs.get('platform_type', 'facebook')
        
        self.log_publish_attempt(
            content_preview,
            platform=f"meta_{platform_type}",
            **kwargs
        )
        
        try:
            # Validate content
            is_valid, error_msg = self.validate_content(content, platform_type=platform_type)
            if not is_valid:
                self.log_publish_error(error_msg, content_preview)
                return PublishResult(
                    success=False,
                    platform=self.platform,
                    error=error_msg,
                    published_at=datetime.utcnow()
                )
            
            # Route to appropriate platform
            if platform_type == 'facebook':
                page_id = kwargs.get('page_id')
                if not page_id:
                    error_msg = "page_id is required for Facebook publishing"
                    self.log_publish_error(error_msg, content_preview)
                    return PublishResult(
                        success=False,
                        platform=self.platform,
                        error=error_msg,
                        published_at=datetime.utcnow()
                    )
                
                response = await self._publish_facebook_page(
                    content,
                    page_id,
                    access_token,
                    **kwargs
                )
                
                post_id = response.get('id')
                post_url = f"https://www.facebook.com/{post_id}" if post_id else None
                
                result = PublishResult(
                    success=True,
                    platform=self.platform,
                    post_id=post_id,
                    url=post_url,
                    metadata={
                        "platform_type": "facebook",
                        "page_id": page_id,
                        "character_count": len(content)
                    },
                    published_at=datetime.utcnow()
                )
                
                self.log_publish_success(result)
                return result
            
            elif platform_type == 'instagram':
                instagram_account_id = kwargs.get('instagram_account_id')
                if not instagram_account_id:
                    error_msg = "instagram_account_id is required for Instagram publishing"
                    self.log_publish_error(error_msg, content_preview)
                    return PublishResult(
                        success=False,
                        platform=self.platform,
                        error=error_msg,
                        published_at=datetime.utcnow()
                    )
                
                response = await self._publish_instagram(
                    content,
                    instagram_account_id,
                    access_token,
                    **kwargs
                )
                
                post_id = response.get('id')
                post_url = f"https://www.instagram.com/p/{post_id}" if post_id else None
                
                result = PublishResult(
                    success=True,
                    platform=self.platform,
                    post_id=post_id,
                    url=post_url,
                    metadata={
                        "platform_type": "instagram",
                        "instagram_account_id": instagram_account_id,
                        "caption_length": len(content),
                        "has_image": 'image_url' in kwargs
                    },
                    published_at=datetime.utcnow()
                )
                
                self.log_publish_success(result)
                return result
            
            else:
                error_msg = f"Unsupported platform_type: {platform_type}. Use 'facebook' or 'instagram'."
                self.log_publish_error(error_msg, content_preview)
                return PublishResult(
                    success=False,
                    platform=self.platform,
                    error=error_msg,
                    published_at=datetime.utcnow()
                )
        
        except httpx.HTTPStatusError as e:
            # Extract error details from Meta API response
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                if 'error' in error_data:
                    error_detail = error_data['error'].get('message', str(e))
                else:
                    error_detail = str(e)
            except Exception:
                error_detail = str(e)
            
            self.log_publish_error(error_detail, content_preview)
            
            if sentry_sdk:
                sentry_sdk.add_breadcrumb(
                    category="meta.error",
                    message=f"Meta API error: {error_detail}",
                    level="error"
                )
            
            return PublishResult(
                success=False,
                platform=self.platform,
                error=f"Meta API error: {error_detail}",
                metadata={
                    "status_code": e.response.status_code,
                    "platform_type": platform_type
                },
                published_at=datetime.utcnow()
            )
        
        except ValueError as e:
            # Handle validation errors
            error_msg = str(e)
            self.log_publish_error(error_msg, content_preview)
            
            return PublishResult(
                success=False,
                platform=self.platform,
                error=error_msg,
                metadata={"platform_type": platform_type},
                published_at=datetime.utcnow()
            )
        
        except Exception as e:
            self.log_publish_error(str(e), content_preview)
            
            if sentry_sdk:
                sentry_sdk.capture_exception(e)
            
            return PublishResult(
                success=False,
                platform=self.platform,
                error=f"Unexpected error: {str(e)}",
                metadata={"platform_type": platform_type},
                published_at=datetime.utcnow()
            )


# Global instance
meta_publisher = MetaPublisher()
