"""
LinkedIn Publishing Service

Handles posting content to LinkedIn using the UGC Posts API v2.
Documentation: https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import httpx
from app.core.config import settings
from app.core.encryption import decrypt_token
from app.models.social_account import SocialAccount


class LinkedInPublishingService:
    """Service for publishing content to LinkedIn."""
    
    # LinkedIn API endpoints
    UGC_POSTS_URL = "https://api.linkedin.com/v2/ugcPosts"
    
    # Content limits
    MAX_TEXT_LENGTH = 3000
    MAX_HASHTAGS = 30
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def post_to_linkedin(
        self,
        account: SocialAccount,
        content_text: str,
        content_images: Optional[list] = None,
        content_links: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Post content to LinkedIn.
        
        Args:
            account: SocialAccount with LinkedIn credentials
            content_text: Text content for the post (max 3000 chars)
            content_images: Optional list of image URLs (not implemented yet)
            content_links: Optional list of links (automatically detected by LinkedIn)
        
        Returns:
            Dict with platform_post_id and platform_post_url
        
        Raises:
            LinkedInAPIError: If posting fails
            TokenExpiredError: If access token is expired
        """
        # Validate content length
        if len(content_text) > self.MAX_TEXT_LENGTH:
            raise ValueError(f"Content exceeds maximum length of {self.MAX_TEXT_LENGTH} characters")
        
        # Decrypt access token
        try:
            access_token = decrypt_token(account.access_token)
        except Exception as e:
            raise TokenExpiredError("Failed to decrypt access token") from e
        
        # Build request payload (text-only for MVP)
        payload = self._build_ugc_post_payload(
            person_id=account.platform_user_id,
            content_text=content_text
        )
        
        # Make API request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        try:
            response = await self.client.post(
                self.UGC_POSTS_URL,
                json=payload,
                headers=headers
            )
            
            # Handle different response codes
            if response.status_code == 201:
                # Success!
                data = response.json()
                return self._parse_success_response(data)
            
            elif response.status_code == 401:
                raise TokenExpiredError("LinkedIn access token expired or invalid")
            
            elif response.status_code == 429:
                raise RateLimitError("LinkedIn rate limit exceeded. Please try again later.")
            
            elif response.status_code == 403:
                raise PermissionError("Insufficient permissions. Check LinkedIn app scopes.")
            
            else:
                # Other error
                error_data = response.json() if response.text else {}
                raise LinkedInAPIError(
                    f"LinkedIn API error ({response.status_code}): {error_data.get('message', 'Unknown error')}"
                )
        
        except httpx.TimeoutException:
            raise LinkedInAPIError("Request to LinkedIn API timed out")
        
        except httpx.RequestError as e:
            raise LinkedInAPIError(f"Network error while posting to LinkedIn: {str(e)}")
    
    def _build_ugc_post_payload(self, person_id: str, content_text: str) -> Dict[str, Any]:
        """
        Build LinkedIn UGC Post API payload.
        
        LinkedIn expects:
        - author: URN of the person posting
        - lifecycleState: PUBLISHED
        - specificContent: Share content with text
        - visibility: Who can see the post
        """
        return {
            "author": f"urn:li:person:{person_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content_text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
    
    def _parse_success_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse LinkedIn API success response.
        
        Response format:
        {
            "id": "urn:li:share:1234567890",
            "created": {...},
            "lastModified": {...}
        }
        """
        post_id = data.get("id", "")  # e.g., "urn:li:share:1234567890"
        
        # Extract numeric ID from URN
        # urn:li:share:1234567890 -> 1234567890
        numeric_id = post_id.split(":")[-1] if ":" in post_id else post_id
        
        # Build post URL
        # LinkedIn post URLs: https://www.linkedin.com/feed/update/{URN}
        post_url = f"https://www.linkedin.com/feed/update/{post_id}" if post_id else None
        
        return {
            "platform_post_id": post_id,
            "platform_post_url": post_url,
            "published_at": datetime.utcnow()
        }
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Custom exceptions
class LinkedInAPIError(Exception):
    """Base exception for LinkedIn API errors."""
    pass


class TokenExpiredError(LinkedInAPIError):
    """Raised when LinkedIn access token is expired or invalid."""
    pass


class RateLimitError(LinkedInAPIError):
    """Raised when LinkedIn rate limit is exceeded."""
    pass
