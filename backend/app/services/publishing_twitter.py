"""
Twitter Publishing Service

Handles posting content to Twitter/X using the Twitter API v2.
Supports single tweets and multi-tweet threads with smart content splitting.

Documentation: https://developer.twitter.com/en/docs/twitter-api/tweets/manage-tweets/api-reference/post-tweets
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
import httpx
import re
from app.core.config import settings
from app.core.encryption import decrypt_token
from app.models.social_account import SocialAccount


class TwitterPublishingService:
    """Service for publishing content to Twitter/X."""
    
    # Twitter API endpoints
    TWEETS_URL = "https://api.twitter.com/2/tweets"
    
    # Content limits
    MAX_TWEET_LENGTH = 280  # Standard Twitter account limit
    MAX_TWEET_LENGTH_PREMIUM = 4000  # Twitter Blue/Premium limit
    MAX_THREAD_TWEETS = 25  # Maximum tweets in a thread
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def post_to_twitter(
        self,
        account: SocialAccount,
        content_text: str,
        use_premium_limit: bool = False
    ) -> Dict[str, Any]:
        """
        Post content to Twitter.
        
        Automatically detects if content should be a single tweet or thread.
        If content exceeds character limit, splits into thread.
        
        Args:
            account: SocialAccount with Twitter credentials
            content_text: Text content for the post
            use_premium_limit: Whether to use premium 4000-char limit (default: False)
        
        Returns:
            Dict with:
                - platform_post_id: ID of first tweet
                - platform_post_url: URL to first tweet
                - thread_tweet_ids: List of all tweet IDs (for threads)
                - published_at: Publication timestamp
        
        Raises:
            TwitterAPIError: If posting fails
            TokenExpiredError: If access token is expired
        """
        max_length = self.MAX_TWEET_LENGTH_PREMIUM if use_premium_limit else self.MAX_TWEET_LENGTH
        
        # Decrypt access token
        try:
            access_token = decrypt_token(account.access_token)
        except Exception as e:
            raise TokenExpiredError("Failed to decrypt access token") from e
        
        # Check if we need to create a thread
        if len(content_text) <= max_length:
            # Single tweet
            result = await self._post_single_tweet(access_token, content_text)
            tweet_id = result["id"]
            tweet_url = self._build_tweet_url(account.platform_username, tweet_id)
            
            return {
                "platform_post_id": tweet_id,
                "platform_post_url": tweet_url,
                "thread_tweet_ids": [tweet_id],
                "published_at": datetime.utcnow()
            }
        else:
            # Thread (multiple tweets)
            result = await self._post_thread(access_token, content_text, max_length, account.platform_username)
            return result
    
    async def _post_single_tweet(
        self,
        access_token: str,
        text: str,
        reply_to_tweet_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Post a single tweet.
        
        Args:
            access_token: Twitter access token
            text: Tweet text (max 280 chars)
            reply_to_tweet_id: Optional tweet ID to reply to (for threads)
        
        Returns:
            API response with tweet data
        
        Raises:
            TwitterAPIError: If posting fails
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload: Dict[str, Any] = {
            "text": text
        }
        
        # Add reply info for thread continuation
        if reply_to_tweet_id:
            payload["reply"] = {
                "in_reply_to_tweet_id": reply_to_tweet_id
            }
        
        try:
            response = await self.client.post(
                self.TWEETS_URL,
                json=payload,
                headers=headers
            )
            
            # Handle different response codes
            if response.status_code == 201:
                # Success!
                data = response.json()
                return data.get("data", data)
            
            elif response.status_code == 401:
                raise TokenExpiredError("Twitter access token expired or invalid")
            
            elif response.status_code == 429:
                # Rate limit - extract retry-after header
                retry_after = response.headers.get("x-rate-limit-reset")
                raise RateLimitError(
                    f"Twitter rate limit exceeded. Reset at: {retry_after}"
                )
            
            elif response.status_code == 403:
                error_data = response.json() if response.text else {}
                detail = error_data.get("detail", "Forbidden")
                raise PermissionError(f"Twitter API permission error: {detail}")
            
            elif response.status_code == 400:
                # Bad request - could be duplicate tweet
                error_data = response.json() if response.text else {}
                if "duplicate" in str(error_data).lower():
                    raise DuplicateTweetError("This tweet appears to be a duplicate")
                raise TwitterAPIError(f"Invalid request: {error_data}")
            
            else:
                # Other error
                error_data = response.json() if response.text else {}
                raise TwitterAPIError(
                    f"Twitter API error ({response.status_code}): {error_data}"
                )
        
        except httpx.TimeoutException:
            raise TwitterAPIError("Request to Twitter API timed out")
        
        except httpx.RequestError as e:
            raise TwitterAPIError(f"Network error while posting to Twitter: {str(e)}")
    
    async def _post_thread(
        self,
        access_token: str,
        content_text: str,
        max_length: int,
        username: str
    ) -> Dict[str, Any]:
        """
        Post a multi-tweet thread.
        
        Splits content into multiple tweets and posts them as a thread
        (each tweet replies to the previous one).
        
        Args:
            access_token: Twitter access token
            content_text: Full content to split into thread
            max_length: Maximum characters per tweet
            username: Twitter username for building URLs
        
        Returns:
            Dict with first tweet ID, URL, and list of all tweet IDs
        """
        # Split content into tweets
        tweet_texts = self._split_into_tweets(content_text, max_length)
        
        if len(tweet_texts) > self.MAX_THREAD_TWEETS:
            raise TwitterAPIError(
                f"Content too long. Maximum {self.MAX_THREAD_TWEETS} tweets per thread."
            )
        
        tweet_ids = []
        previous_tweet_id = None
        
        # Post each tweet in sequence
        for i, tweet_text in enumerate(tweet_texts):
            try:
                result = await self._post_single_tweet(
                    access_token,
                    tweet_text,
                    reply_to_tweet_id=previous_tweet_id
                )
                tweet_id = result["id"]
                tweet_ids.append(tweet_id)
                previous_tweet_id = tweet_id
                
            except Exception as e:
                # If thread fails mid-way, return what we posted
                if tweet_ids:
                    first_tweet_url = self._build_tweet_url(username, tweet_ids[0])
                    raise PartialThreadError(
                        f"Thread posting failed at tweet {i+1}/{len(tweet_texts)}. "
                        f"Posted {len(tweet_ids)} tweets.",
                        tweet_ids=tweet_ids,
                        first_tweet_url=first_tweet_url
                    ) from e
                else:
                    raise
        
        # Build URL to first tweet
        first_tweet_url = self._build_tweet_url(username, tweet_ids[0])
        
        return {
            "platform_post_id": tweet_ids[0],  # First tweet ID
            "platform_post_url": first_tweet_url,
            "thread_tweet_ids": tweet_ids,
            "published_at": datetime.utcnow()
        }
    
    def _split_into_tweets(self, content: str, max_length: int) -> List[str]:
        """
        Split content into tweet-sized chunks with smart sentence breaking.
        
        Algorithm:
        1. Extract and remove hashtags
        2. Split content into sentences
        3. Group sentences into tweets (respecting max_length)
        4. Add thread indicators (1/N, 2/N, etc.)
        5. Add hashtags to last tweet
        
        Args:
            content: Full content text
            max_length: Maximum characters per tweet
        
        Returns:
            List of tweet texts with thread indicators
        """
        # Extract hashtags (they'll go in the last tweet)
        hashtags = self._extract_hashtags(content)
        content_without_hashtags = self._remove_hashtags(content)
        
        # Split into sentences
        sentences = self._split_sentences(content_without_hashtags)
        
        tweets = []
        current_tweet = ""
        
        # Reserve space for thread indicator (e.g., " (10/25)" = 8 chars)
        thread_indicator_space = 10
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if adding this sentence would exceed limit
            test_tweet = current_tweet + (" " if current_tweet else "") + sentence
            
            if len(test_tweet) + thread_indicator_space <= max_length:
                # Fits in current tweet
                current_tweet = test_tweet
            else:
                # Doesn't fit - save current tweet and start new one
                if current_tweet:
                    tweets.append(current_tweet)
                
                # Check if single sentence is too long
                if len(sentence) + thread_indicator_space > max_length:
                    # Split long sentence by words
                    words = sentence.split()
                    current_tweet = ""
                    for word in words:
                        test_tweet = current_tweet + (" " if current_tweet else "") + word
                        if len(test_tweet) + thread_indicator_space <= max_length:
                            current_tweet = test_tweet
                        else:
                            if current_tweet:
                                tweets.append(current_tweet)
                            current_tweet = word
                else:
                    current_tweet = sentence
        
        # Add final tweet
        if current_tweet:
            tweets.append(current_tweet)
        
        # Add hashtags to last tweet if they fit
        if hashtags and tweets:
            last_tweet = tweets[-1]
            hashtags_text = "\n\n" + hashtags
            if len(last_tweet + hashtags_text) + thread_indicator_space <= max_length:
                tweets[-1] = last_tweet + hashtags_text
            else:
                # Hashtags don't fit - add as separate tweet
                tweets.append(hashtags)
        
        # Add thread indicators (1/N, 2/N, etc.)
        total = len(tweets)
        if total > 1:
            tweets = [f"{tweet} ({i+1}/{total})" for i, tweet in enumerate(tweets)]
        
        return tweets
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Simple sentence splitting by '.', '!', '?'
        Preserves sentence-ending punctuation.
        """
        # Split on sentence-ending punctuation followed by space or newline
        pattern = r'(?<=[.!?])\s+'
        sentences = re.split(pattern, text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _extract_hashtags(self, text: str) -> str:
        """Extract all hashtags from text."""
        hashtags = re.findall(r'#\w+', text)
        return " ".join(hashtags) if hashtags else ""
    
    def _remove_hashtags(self, text: str) -> str:
        """Remove all hashtags from text."""
        return re.sub(r'#\w+\s*', '', text).strip()
    
    def _build_tweet_url(self, username: str, tweet_id: str) -> str:
        """
        Build URL to a tweet.
        
        Format: https://twitter.com/{username}/status/{tweet_id}
        or: https://x.com/{username}/status/{tweet_id}
        """
        # Remove @ if present
        username = username.lstrip('@')
        return f"https://twitter.com/{username}/status/{tweet_id}"
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Custom exceptions
class TwitterAPIError(Exception):
    """Base exception for Twitter API errors."""
    pass


class TokenExpiredError(TwitterAPIError):
    """Raised when Twitter access token is expired or invalid."""
    pass


class RateLimitError(TwitterAPIError):
    """Raised when Twitter rate limit is exceeded."""
    pass


class DuplicateTweetError(TwitterAPIError):
    """Raised when attempting to post a duplicate tweet."""
    pass


class PartialThreadError(TwitterAPIError):
    """Raised when thread posting fails mid-way."""
    
    def __init__(self, message: str, tweet_ids: List[str], first_tweet_url: str):
        super().__init__(message)
        self.tweet_ids = tweet_ids
        self.first_tweet_url = first_tweet_url
