"""
Base Publisher Abstract Class
Defines common interface for all social media publishers
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class PublishResult:
    """Result of a publishing operation"""
    
    def __init__(
        self,
        success: bool,
        platform: str,
        post_id: Optional[str] = None,
        url: Optional[str] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.platform = platform
        self.post_id = post_id
        self.url = url
        self.error = error
        self.metadata = metadata or {}
        self.published_at = datetime.utcnow() if success else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "platform": self.platform,
            "post_id": self.post_id,
            "url": self.url,
            "error": self.error,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "metadata": self.metadata
        }


class BasePublisher(ABC):
    """
    Abstract base class for social media publishers
    
    All platform-specific publishers inherit from this class
    and implement the publish() method
    """
    
    def __init__(self, platform: str):
        self.platform = platform
        self.logger = get_logger(f"{__name__}.{platform}")
        self.max_retries = 3
        self.retry_delay = 5  # seconds
    
    @abstractmethod
    async def publish(
        self,
        content: str,
        access_token: str,
        **kwargs
    ) -> PublishResult:
        """
        Publish content to the platform
        
        Args:
            content: Text content to publish
            access_token: Decrypted OAuth access token
            **kwargs: Platform-specific parameters
        
        Returns:
            PublishResult with success status and details
        """
        pass
    
    @abstractmethod
    def validate_content(self, content: str, **kwargs) -> tuple[bool, Optional[str]]:
        """
        Validate content before publishing
        
        Args:
            content: Content to validate
            **kwargs: Platform-specific parameters
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass
    
    def get_character_limit(self) -> int:
        """Get platform character limit"""
        return 0
    
    def truncate_content(self, content: str, limit: int) -> str:
        """Truncate content to character limit"""
        if len(content) <= limit:
            return content
        
        # Try to truncate at last complete word
        truncated = content[:limit - 3]
        last_space = truncated.rfind(' ')
        
        if last_space > 0:
            truncated = truncated[:last_space]
        
        return truncated + '...'
    
    def log_publish_attempt(self, content_preview: str, **kwargs):
        """Log publishing attempt"""
        self.logger.info(
            f"Attempting to publish to {self.platform}",
            extra={
                'event_type': 'publish_attempt',
                'platform': self.platform,
                'content_preview': content_preview[:50] + '...' if len(content_preview) > 50 else content_preview,
                **kwargs
            }
        )
    
    def log_publish_success(self, result: PublishResult):
        """Log successful publish"""
        self.logger.info(
            f"Successfully published to {self.platform}",
            extra={
                'event_type': 'publish_success',
                'platform': self.platform,
                'post_id': result.post_id,
                'url': result.url
            }
        )
    
    def log_publish_error(self, error: Exception, content_preview: str):
        """Log publishing error"""
        self.logger.error(
            f"Failed to publish to {self.platform}: {str(error)}",
            extra={
                'event_type': 'publish_error',
                'platform': self.platform,
                'error': str(error),
                'content_preview': content_preview[:50]
            },
            exc_info=True
        )
