"""
Twitter Publisher Service

This module implements Twitter (X) publishing functionality using the Twitter API v2.
Supports single tweets and automatic thread creation for content >280 characters.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx
from app.services.publishing.base_publisher import BasePublisher, PublishResult

try:
    import sentry_sdk
except ImportError:
    sentry_sdk = None

logger = logging.getLogger(__name__)


class TwitterPublisher(BasePublisher):
    """
    Twitter publisher implementation using Twitter API v2.
    
    Features:
    - Single tweet posting
    - Automatic thread creation for long content
    - Smart sentence-aware text splitting
    - Comprehensive error handling
    - Rate limit awareness
    """
    
    # Twitter API v2 endpoints
    TWEETS_URL = "https://api.twitter.com/2/tweets"
    USER_URL = "https://api.twitter.com/2/users/me"
    
    # Twitter character limits
    MAX_TWEET_LENGTH = 280
    
    def __init__(self):
        super().__init__(platform="twitter")
    
    def get_character_limit(self) -> int:
        """Get Twitter's character limit."""
        return self.MAX_TWEET_LENGTH
    
    def validate_content(self, content: str, **kwargs) -> tuple[bool, Optional[str]]:
        """
        Validate tweet content.
        
        Args:
            content: The tweet text to validate
            **kwargs: Additional validation parameters
                - allow_threads: If True, allows content >280 chars (default: True)
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not content or not content.strip():
            return False, "Tweet content cannot be empty"
        
        # Check if threads are allowed
        allow_threads = kwargs.get('allow_threads', True)
        
        if not allow_threads and len(content) > self.MAX_TWEET_LENGTH:
            return False, f"Tweet exceeds {self.MAX_TWEET_LENGTH} character limit. Use allow_threads=True for long content."
        
        return True, None
    
    def _split_into_thread(self, content: str, max_length: int = 270) -> List[str]:
        """
        Split long content into thread-friendly chunks.
        
        Uses smart sentence-aware splitting with thread numbering.
        Reserves 10 chars for " (X/Y)" numbering.
        
        Args:
            content: The full content to split
            max_length: Maximum length per tweet (default: 270 to reserve space for numbering)
        
        Returns:
            List of tweet texts with numbering
        """
        if len(content) <= self.MAX_TWEET_LENGTH:
            return [content]
        
        # Split by sentences (. ! ?)
        sentences = []
        current_sentence = ""
        
        for char in content:
            current_sentence += char
            if char in '.!?' and len(current_sentence.strip()) > 0:
                sentences.append(current_sentence.strip())
                current_sentence = ""
        
        # Add remaining text
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        # Group sentences into tweets
        tweets = []
        current_tweet = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed limit, start new tweet
            if len(current_tweet) + len(sentence) + 1 > max_length:
                if current_tweet:
                    tweets.append(current_tweet.strip())
                current_tweet = sentence
            else:
                # Add sentence to current tweet
                if current_tweet:
                    current_tweet += " " + sentence
                else:
                    current_tweet = sentence
        
        # Add final tweet
        if current_tweet:
            tweets.append(current_tweet.strip())
        
        # Add thread numbering (1/N, 2/N, etc.)
        total_tweets = len(tweets)
        if total_tweets > 1:
            numbered_tweets = []
            for i, tweet in enumerate(tweets, 1):
                # Add numbering to beginning of each tweet
                numbered_tweet = f"{i}/{total_tweets} {tweet}"
                
                # If numbering makes it too long, truncate content
                if len(numbered_tweet) > self.MAX_TWEET_LENGTH:
                    available_length = self.MAX_TWEET_LENGTH - len(f"{i}/{total_tweets} ") - 3  # 3 for "..."
                    truncated = tweet[:available_length] + "..."
                    numbered_tweet = f"{i}/{total_tweets} {truncated}"
                
                numbered_tweets.append(numbered_tweet)
            
            return numbered_tweets
        
        return tweets
    
    async def _post_single_tweet(
        self,
        text: str,
        access_token: str,
        reply_to_tweet_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Post a single tweet to Twitter API v2.
        
        Args:
            text: Tweet text (max 280 chars)
            access_token: OAuth 2.0 access token
            reply_to_tweet_id: Optional tweet ID to reply to (for threading)
        
        Returns:
            API response dict with tweet data
        
        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        if sentry_sdk:
            sentry_sdk.add_breadcrumb(
                category="twitter.api",
                message=f"Posting tweet ({len(text)} chars)",
                level="info"
            )
        
        # Build tweet payload
        tweet_data = {
            "text": text
        }
        
        # Add reply reference for threading
        if reply_to_tweet_id:
            tweet_data["reply"] = {
                "in_reply_to_tweet_id": reply_to_tweet_id
            }
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Post tweet
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.TWEETS_URL,
                json=tweet_data,
                headers=headers
            )
            response.raise_for_status()
        
        return response.json()
    
    async def publish(
        self,
        content: str,
        access_token: str,
        **kwargs
    ) -> PublishResult:
        """
        Publish content to Twitter.
        
        Automatically creates threads if content exceeds 280 characters.
        
        Args:
            content: The tweet content
            access_token: Decrypted OAuth 2.0 access token
            **kwargs: Additional parameters
                - allow_threads: Enable thread creation for long content (default: True)
        
        Returns:
            PublishResult with tweet ID and URL
        """
        if sentry_sdk:
            sentry_sdk.add_breadcrumb(
                category="twitter.publish",
                message="Starting Twitter publish",
                level="info"
            )
        
        content_preview = content[:100] + "..." if len(content) > 100 else content
        self.log_publish_attempt(content_preview, platform="twitter")
        
        try:
            # Validate content
            is_valid, error_msg = self.validate_content(content, **kwargs)
            if not is_valid:
                self.log_publish_error(error_msg, content_preview)
                return PublishResult(
                    success=False,
                    platform=self.platform,
                    error=error_msg,
                    published_at=datetime.utcnow()
                )
            
            # Check if we need to create a thread
            allow_threads = kwargs.get('allow_threads', True)
            
            if len(content) <= self.MAX_TWEET_LENGTH:
                # Single tweet
                response = await self._post_single_tweet(content, access_token)
                tweet_data = response.get('data', {})
                tweet_id = tweet_data.get('id')
                
                # Construct Twitter URL
                tweet_url = f"https://twitter.com/i/status/{tweet_id}" if tweet_id else None
                
                result = PublishResult(
                    success=True,
                    platform=self.platform,
                    post_id=tweet_id,
                    url=tweet_url,
                    metadata={
                        "is_thread": False,
                        "character_count": len(content)
                    },
                    published_at=datetime.utcnow()
                )
                
                self.log_publish_success(result)
                return result
            
            else:
                # Create thread
                if not allow_threads:
                    error_msg = f"Content exceeds {self.MAX_TWEET_LENGTH} characters and threads are disabled"
                    self.log_publish_error(error_msg, content_preview)
                    return PublishResult(
                        success=False,
                        platform=self.platform,
                        error=error_msg,
                        published_at=datetime.utcnow()
                    )
                
                # Split into thread
                tweets = self._split_into_thread(content)
                
                logger.info(
                    "Publishing Twitter thread",
                    extra={
                        "event_type": "twitter_thread_start",
                        "tweet_count": len(tweets),
                        "total_chars": len(content)
                    }
                )
                
                # Post tweets sequentially
                tweet_ids = []
                reply_to_id = None
                
                for i, tweet_text in enumerate(tweets):
                    response = await self._post_single_tweet(
                        tweet_text,
                        access_token,
                        reply_to_tweet_id=reply_to_id
                    )
                    
                    tweet_data = response.get('data', {})
                    tweet_id = tweet_data.get('id')
                    tweet_ids.append(tweet_id)
                    
                    # Next tweet replies to this one
                    reply_to_id = tweet_id
                    
                    logger.info(
                        f"Posted tweet {i+1}/{len(tweets)}",
                        extra={
                            "event_type": "twitter_thread_tweet",
                            "tweet_number": i + 1,
                            "tweet_id": tweet_id
                        }
                    )
                
                # First tweet ID is the thread ID
                thread_id = tweet_ids[0] if tweet_ids else None
                thread_url = f"https://twitter.com/i/status/{thread_id}" if thread_id else None
                
                result = PublishResult(
                    success=True,
                    platform=self.platform,
                    post_id=thread_id,
                    url=thread_url,
                    metadata={
                        "is_thread": True,
                        "tweet_count": len(tweets),
                        "tweet_ids": tweet_ids,
                        "total_chars": len(content)
                    },
                    published_at=datetime.utcnow()
                )
                
                self.log_publish_success(result)
                return result
        
        except httpx.HTTPStatusError as e:
            # Extract error details from Twitter API response
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get('detail', error_data.get('title', str(e)))
            except Exception:
                error_detail = str(e)
            
            self.log_publish_error(error_detail, content_preview)
            
            if sentry_sdk:
                sentry_sdk.add_breadcrumb(
                    category="twitter.error",
                    message=f"Twitter API error: {error_detail}",
                    level="error"
                )
            
            return PublishResult(
                success=False,
                platform=self.platform,
                error=f"Twitter API error: {error_detail}",
                metadata={"status_code": e.response.status_code},
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
                published_at=datetime.utcnow()
            )


# Global instance
twitter_publisher = TwitterPublisher()
