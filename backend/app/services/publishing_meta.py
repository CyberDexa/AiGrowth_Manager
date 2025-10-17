"""
Meta (Facebook/Instagram) Publishing Service

This module handles content publishing to Facebook Pages and Instagram Business accounts.

Publishing Flows:

Facebook:
- Direct publishing via POST /{page-id}/feed
- Character limit: 63,206 (no threading needed!)
- Instant posting
- Image optional

Instagram:
- Two-step publishing process:
  1. Create media container: POST /{ig-user-id}/media
  2. Publish container: POST /{ig-user-id}/media_publish
- Character limit: 2,200 characters
- Image REQUIRED
- 15-30 second delay between steps
"""

from typing import Dict, Any, Optional
import httpx
import asyncio
import logging

logger = logging.getLogger(__name__)


class MetaPublishingService:
    """Service for publishing content to Facebook and Instagram"""
    
    # API Configuration
    GRAPH_API_BASE = "https://graph.facebook.com/v18.0"
    
    # Character Limits
    FACEBOOK_MAX_CHARS = 63206  # Facebook has very high limit
    INSTAGRAM_MAX_CHARS = 2200  # Instagram has 2,200 char limit
    
    # Instagram Publishing Delays
    INSTAGRAM_CONTAINER_DELAY = 20  # Wait 20 seconds between create and publish
    
    def __init__(self):
        """Initialize Meta publishing service"""
        pass
    
    async def post_to_facebook(
        self,
        page_id: str,
        page_access_token: str,
        content: str,
        image_url: Optional[str] = None,
        link: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Publish a post to a Facebook Page
        
        Args:
            page_id: Facebook Page ID
            page_access_token: Page access token
            content: Post text content (max 63,206 chars)
            image_url: Optional image URL to attach
            link: Optional link to attach
            
        Returns:
            Dict containing:
            - id: Post ID (format: {page-id}_{post-id})
            - success: Boolean indicating success
            
        Raises:
            ValueError: If content exceeds character limit
            httpx.HTTPError: If API request fails
        """
        # Validate content length
        if len(content) > self.FACEBOOK_MAX_CHARS:
            raise ValueError(
                f"Content exceeds Facebook limit of {self.FACEBOOK_MAX_CHARS} characters"
            )
        
        url = f"{self.GRAPH_API_BASE}/{page_id}/feed"
        
        # Build payload
        payload = {
            "message": content,
            "access_token": page_access_token
        }
        
        # Add optional fields
        if image_url:
            # For images, use /photos endpoint instead
            return await self._post_facebook_photo(
                page_id=page_id,
                page_access_token=page_access_token,
                content=content,
                image_url=image_url
            )
        
        if link:
            payload["link"] = link
        
        # Make API request
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload)
            response.raise_for_status()
            
            data = response.json()
            post_id = data.get("id")
            
            logger.info(f"Successfully posted to Facebook Page {page_id}: {post_id}")
            
            return {
                "id": post_id,
                "success": True,
                "platform": "facebook",
                "url": f"https://www.facebook.com/{post_id}"
            }
    
    async def _post_facebook_photo(
        self,
        page_id: str,
        page_access_token: str,
        content: str,
        image_url: str
    ) -> Dict[str, Any]:
        """
        Post a photo to Facebook Page
        
        Args:
            page_id: Facebook Page ID
            page_access_token: Page access token
            content: Photo caption
            image_url: URL of image to post
            
        Returns:
            Dict with post details
        """
        url = f"{self.GRAPH_API_BASE}/{page_id}/photos"
        
        payload = {
            "url": image_url,
            "caption": content,
            "access_token": page_access_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload)
            response.raise_for_status()
            
            data = response.json()
            post_id = data.get("id")
            
            logger.info(f"Successfully posted photo to Facebook Page {page_id}: {post_id}")
            
            return {
                "id": post_id,
                "success": True,
                "platform": "facebook",
                "url": f"https://www.facebook.com/photo.php?fbid={post_id}"
            }
    
    async def post_to_instagram(
        self,
        instagram_account_id: str,
        page_access_token: str,
        content: str,
        image_url: str
    ) -> Dict[str, Any]:
        """
        Publish a post to Instagram Business account (two-step process)
        
        Step 1: Create media container
        Step 2: Publish media container (after delay)
        
        Args:
            instagram_account_id: Instagram Business account ID
            page_access_token: Page access token
            content: Post caption (max 2,200 chars)
            image_url: Image URL (REQUIRED - Instagram requires images)
            
        Returns:
            Dict containing:
            - id: Post ID
            - success: Boolean indicating success
            - container_id: Media container ID
            
        Raises:
            ValueError: If content exceeds character limit or image_url missing
            httpx.HTTPError: If API request fails
        """
        # Validate content length
        if len(content) > self.INSTAGRAM_MAX_CHARS:
            raise ValueError(
                f"Content exceeds Instagram limit of {self.INSTAGRAM_MAX_CHARS} characters"
            )
        
        if not image_url:
            raise ValueError("Instagram posts require an image URL")
        
        # Step 1: Create media container
        container_id = await self._create_instagram_container(
            instagram_account_id=instagram_account_id,
            page_access_token=page_access_token,
            content=content,
            image_url=image_url
        )
        
        # Step 2: Wait for container to be ready
        logger.info(f"Waiting {self.INSTAGRAM_CONTAINER_DELAY} seconds for container to be ready...")
        await asyncio.sleep(self.INSTAGRAM_CONTAINER_DELAY)
        
        # Step 3: Publish the container
        post_id = await self._publish_instagram_container(
            instagram_account_id=instagram_account_id,
            page_access_token=page_access_token,
            container_id=container_id
        )
        
        logger.info(f"Successfully posted to Instagram: {post_id}")
        
        return {
            "id": post_id,
            "success": True,
            "platform": "instagram",
            "container_id": container_id,
            "url": f"https://www.instagram.com/p/{self._get_instagram_shortcode(post_id)}"
        }
    
    async def _create_instagram_container(
        self,
        instagram_account_id: str,
        page_access_token: str,
        content: str,
        image_url: str
    ) -> str:
        """
        Create Instagram media container (Step 1)
        
        Args:
            instagram_account_id: Instagram Business account ID
            page_access_token: Page access token
            content: Post caption
            image_url: Image URL
            
        Returns:
            Container ID (used in publish step)
        """
        url = f"{self.GRAPH_API_BASE}/{instagram_account_id}/media"
        
        payload = {
            "image_url": image_url,
            "caption": content,
            "access_token": page_access_token
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, data=payload)
            response.raise_for_status()
            
            data = response.json()
            container_id = data.get("id")
            
            logger.info(f"Created Instagram container: {container_id}")
            return container_id
    
    async def _publish_instagram_container(
        self,
        instagram_account_id: str,
        page_access_token: str,
        container_id: str
    ) -> str:
        """
        Publish Instagram media container (Step 2)
        
        Args:
            instagram_account_id: Instagram Business account ID
            page_access_token: Page access token
            container_id: Container ID from creation step
            
        Returns:
            Published post ID
        """
        url = f"{self.GRAPH_API_BASE}/{instagram_account_id}/media_publish"
        
        payload = {
            "creation_id": container_id,
            "access_token": page_access_token
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, data=payload)
            response.raise_for_status()
            
            data = response.json()
            post_id = data.get("id")
            
            logger.info(f"Published Instagram container {container_id} as post {post_id}")
            return post_id
    
    def _get_instagram_shortcode(self, post_id: str) -> str:
        """
        Convert Instagram post ID to shortcode for URL
        
        Note: This is a simplified version. In production, you would
        need to fetch the post details to get the actual shortcode.
        
        Args:
            post_id: Instagram post ID
            
        Returns:
            Shortcode for Instagram URL
        """
        # For now, just return the post_id
        # In production, fetch: /{media-id}?fields=shortcode
        return post_id
    
    async def get_post_insights(
        self,
        post_id: str,
        access_token: str,
        platform: str = "facebook"
    ) -> Dict[str, Any]:
        """
        Get insights/analytics for a published post
        
        Args:
            post_id: Post ID
            access_token: Access token
            platform: "facebook" or "instagram"
            
        Returns:
            Dict with post insights (impressions, reach, engagement)
        """
        if platform == "facebook":
            url = f"{self.GRAPH_API_BASE}/{post_id}/insights"
            params = {
                "metric": "post_impressions,post_engaged_users",
                "access_token": access_token
            }
        else:  # instagram
            url = f"{self.GRAPH_API_BASE}/{post_id}/insights"
            params = {
                "metric": "impressions,reach,engagement",
                "access_token": access_token
            }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            insights = data.get("data", [])
            
            # Parse insights into readable format
            result = {}
            for insight in insights:
                metric_name = insight.get("name")
                values = insight.get("values", [])
                if values:
                    result[metric_name] = values[0].get("value", 0)
            
            logger.info(f"Retrieved {platform} post insights: {result}")
            return result
    
    async def delete_post(
        self,
        post_id: str,
        access_token: str
    ) -> bool:
        """
        Delete a published post
        
        Args:
            post_id: Post ID to delete
            access_token: Access token (Page or User)
            
        Returns:
            True if successful
        """
        url = f"{self.GRAPH_API_BASE}/{post_id}"
        params = {
            "access_token": access_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            success = data.get("success", False)
            
            if success:
                logger.info(f"Successfully deleted post: {post_id}")
            
            return success
    
    def validate_content_length(self, content: str, platform: str) -> tuple[bool, str]:
        """
        Validate if content length is within platform limits
        
        Args:
            content: Post content
            platform: "facebook" or "instagram"
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        char_count = len(content)
        
        if platform == "facebook":
            if char_count > self.FACEBOOK_MAX_CHARS:
                return False, f"Content exceeds Facebook limit of {self.FACEBOOK_MAX_CHARS} characters"
        elif platform == "instagram":
            if char_count > self.INSTAGRAM_MAX_CHARS:
                return False, f"Content exceeds Instagram limit of {self.INSTAGRAM_MAX_CHARS} characters"
        
        return True, ""
    
    def get_platform_limits(self) -> Dict[str, int]:
        """
        Get character limits for all platforms
        
        Returns:
            Dict with platform character limits
        """
        return {
            "facebook": self.FACEBOOK_MAX_CHARS,
            "instagram": self.INSTAGRAM_MAX_CHARS
        }


# Helper function for service initialization
def create_meta_publishing_service() -> MetaPublishingService:
    """
    Create and configure Meta publishing service
    
    Returns:
        Configured MetaPublishingService instance
    """
    return MetaPublishingService()
