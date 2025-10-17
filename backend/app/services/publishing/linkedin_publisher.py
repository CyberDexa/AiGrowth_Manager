"""
LinkedIn Publisher Service
Handles publishing posts to LinkedIn using UGC Posts API v2
"""
import httpx
from typing import Dict, Any, Optional
from datetime import datetime

from app.services.publishing.base_publisher import BasePublisher, PublishResult
from app.core.sentry_config import add_breadcrumb


class LinkedInPublisher(BasePublisher):
    """
    Publisher for LinkedIn platform using UGC Posts API v2
    
    Documentation: https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin
    """
    
    # LinkedIn API endpoints
    UGC_POSTS_URL = "https://api.linkedin.com/v2/ugcPosts"
    PROFILE_URL = "https://api.linkedin.com/v2/me"
    
    # Character limits
    MAX_TEXT_LENGTH = 3000
    MAX_TITLE_LENGTH = 200
    
    def __init__(self):
        super().__init__(platform="linkedin")
    
    def get_character_limit(self) -> int:
        """LinkedIn allows up to 3000 characters"""
        return self.MAX_TEXT_LENGTH
    
    def validate_content(self, content: str, **kwargs) -> tuple[bool, Optional[str]]:
        """
        Validate content for LinkedIn
        
        Args:
            content: Post text content
            **kwargs: Additional parameters (organization_id, etc.)
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not content or not content.strip():
            return False, "Content cannot be empty"
        
        if len(content) > self.MAX_TEXT_LENGTH:
            return False, f"Content exceeds {self.MAX_TEXT_LENGTH} character limit"
        
        return True, None
    
    async def get_user_urn(self, access_token: str) -> str:
        """
        Get the user's URN (profile identifier)
        
        Args:
            access_token: LinkedIn access token
        
        Returns:
            User URN in format "urn:li:person:XXXXX"
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.PROFILE_URL, headers=headers)
            response.raise_for_status()
            profile = response.json()
            
            # Return URN from profile
            return f"urn:li:person:{profile['id']}"
    
    async def publish(
        self,
        content: str,
        access_token: str,
        **kwargs
    ) -> PublishResult:
        """
        Publish a post to LinkedIn
        
        Args:
            content: Text content to publish
            access_token: LinkedIn access token (decrypted)
            **kwargs: Additional parameters
                - organization_id: Optional organization URN for company posts
                - visibility: Post visibility ('PUBLIC', 'CONNECTIONS')
        
        Returns:
            PublishResult with success status and post details
        """
        # Add Sentry breadcrumb
        add_breadcrumb(
            category='publishing',
            message='Starting LinkedIn publish',
            level='info',
            data={'content_length': len(content)}
        )
        
        # Validate content
        is_valid, error_msg = self.validate_content(content, **kwargs)
        if not is_valid:
            self.logger.warning(f"Content validation failed: {error_msg}")
            return PublishResult(
                success=False,
                platform=self.platform,
                error=error_msg
            )
        
        try:
            self.log_publish_attempt(content, **kwargs)
            
            # Get author URN (user or organization)
            author_urn = kwargs.get('organization_id')
            if not author_urn:
                author_urn = await self.get_user_urn(access_token)
            
            # Build UGC post payload
            post_data = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": kwargs.get('visibility', 'PUBLIC')
                }
            }
            
            # Make API request
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.UGC_POSTS_URL,
                    json=post_data,
                    headers=headers
                )
                
                response.raise_for_status()
                result_data = response.json()
                
                # Extract post ID from response
                post_id = result_data.get('id', '')
                
                # Construct post URL
                # LinkedIn post URLs: https://www.linkedin.com/feed/update/{urn}
                post_url = None
                if post_id:
                    # Convert URN to URL-safe format
                    post_url = f"https://www.linkedin.com/feed/update/{post_id}"
                
                result = PublishResult(
                    success=True,
                    platform=self.platform,
                    post_id=post_id,
                    url=post_url,
                    metadata={
                        'author': author_urn,
                        'visibility': kwargs.get('visibility', 'PUBLIC'),
                        'character_count': len(content)
                    }
                )
                
                self.log_publish_success(result)
                
                add_breadcrumb(
                    category='publishing',
                    message='LinkedIn publish successful',
                    level='info',
                    data={'post_id': post_id}
                )
                
                return result
        
        except httpx.HTTPStatusError as e:
            error_msg = f"LinkedIn API error: {e.response.status_code}"
            
            # Try to extract error details from response
            try:
                error_data = e.response.json()
                if 'message' in error_data:
                    error_msg = f"{error_msg} - {error_data['message']}"
            except:
                pass
            
            self.log_publish_error(e, content)
            
            add_breadcrumb(
                category='publishing',
                message='LinkedIn publish failed',
                level='error',
                data={'error': error_msg, 'status_code': e.response.status_code}
            )
            
            return PublishResult(
                success=False,
                platform=self.platform,
                error=error_msg
            )
        
        except Exception as e:
            error_msg = f"Failed to publish to LinkedIn: {str(e)}"
            self.log_publish_error(e, content)
            
            add_breadcrumb(
                category='publishing',
                message='LinkedIn publish exception',
                level='error',
                data={'error': str(e)}
            )
            
            return PublishResult(
                success=False,
                platform=self.platform,
                error=error_msg
            )


# Global instance
linkedin_publisher = LinkedInPublisher()
