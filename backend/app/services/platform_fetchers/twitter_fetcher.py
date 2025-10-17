"""Twitter/X analytics fetcher."""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

from .base_fetcher import BasePlatformFetcher
from .exceptions import PlatformAPIError, PostNotFoundError

logger = logging.getLogger(__name__)


class TwitterAnalyticsFetcher(BasePlatformFetcher):
    """
    Fetches analytics data from Twitter/X API v2.
    
    Twitter API Endpoints:
    - Tweet Lookup: /2/tweets/{id}
    - Tweet Metrics: /2/tweets?ids={ids}&tweet.fields=public_metrics,non_public_metrics,organic_metrics
    
    Rate Limits:
    - 300 requests per 15 minutes (user context)
    - 900 requests per 15 minutes (app context)
    
    Note: Requires Twitter API v2 Essential access or higher
    """
    
    BASE_URL = "https://api.twitter.com"
    API_VERSION = "2"
    
    def __init__(
        self,
        access_token: str,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        timeout: int = 30
    ):
        """
        Initialize Twitter fetcher.
        
        Args:
            access_token: Twitter OAuth 2.0 Bearer token
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor
            timeout: Request timeout in seconds
        """
        super().__init__(access_token, max_retries, backoff_factor, timeout)
    
    def fetch_post_analytics(
        self,
        post_id: str,
        platform_post_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch analytics for a Twitter post (tweet).
        
        Args:
            post_id: Internal post ID
            platform_post_id: Twitter tweet ID
            
        Returns:
            Standardized analytics dictionary
            
        Raises:
            PostNotFoundError: If tweet not found
            PlatformAPIError: If API request fails
        """
        if not platform_post_id:
            raise PlatformAPIError(
                "Twitter tweet ID is required",
                platform="twitter"
            )
        
        logger.info(f"Fetching Twitter analytics for tweet {platform_post_id}")
        
        try:
            # Fetch tweet with metrics
            tweet_data = self._fetch_tweet_metrics(platform_post_id)
            
            # Parse and standardize the data
            analytics = self._parse_twitter_analytics(tweet_data)
            
            # Add metadata
            analytics["fetched_at"] = datetime.utcnow()
            analytics["platform"] = "twitter"
            analytics["platform_post_id"] = platform_post_id
            analytics["platform_post_url"] = f"https://twitter.com/i/web/status/{platform_post_id}"
            
            logger.info(f"Successfully fetched Twitter analytics for tweet {platform_post_id}")
            return analytics
            
        except PostNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch Twitter analytics: {e}")
            raise PlatformAPIError(
                f"Failed to fetch Twitter analytics: {str(e)}",
                platform="twitter"
            )
    
    def _fetch_tweet_metrics(self, tweet_id: str) -> Dict[str, Any]:
        """
        Fetch tweet with all available metrics.
        
        Args:
            tweet_id: Twitter tweet ID
            
        Returns:
            Tweet data with metrics
        """
        url = f"{self.BASE_URL}/{self.API_VERSION}/tweets/{tweet_id}"
        
        # Request all available metric fields
        params = {
            "tweet.fields": "public_metrics,non_public_metrics,organic_metrics,created_at",
            "expansions": "author_id",
            "user.fields": "username"
        }
        
        try:
            response = self._make_request(
                method="GET",
                url=url,
                params=params
            )
            
            # Check if tweet was found
            if "data" not in response:
                raise PostNotFoundError(
                    f"Twitter tweet {tweet_id} not found",
                    post_id=tweet_id,
                    platform="twitter"
                )
            
            return response["data"]
            
        except PostNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch tweet metrics: {e}")
            raise PlatformAPIError(
                f"Failed to fetch tweet metrics: {str(e)}",
                platform="twitter"
            )
    
    def _parse_twitter_analytics(self, tweet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Twitter API response into standardized format.
        
        Args:
            tweet_data: Tweet data from API
            
        Returns:
            Standardized analytics dictionary
        """
        # Twitter provides metrics in different categories:
        # - public_metrics: Available to all users (likes, retweets, replies, quotes)
        # - non_public_metrics: Only for tweet owner (impressions, URL clicks, user profile clicks)
        # - organic_metrics: Organic (non-promoted) metrics
        
        public_metrics = tweet_data.get("public_metrics", {})
        non_public_metrics = tweet_data.get("non_public_metrics", {})
        organic_metrics = tweet_data.get("organic_metrics", {})
        
        # Extract public metrics (always available)
        likes = public_metrics.get("like_count", 0) or 0
        retweets = public_metrics.get("retweet_count", 0) or 0
        replies = public_metrics.get("reply_count", 0) or 0
        quotes = public_metrics.get("quote_count", 0) or 0
        bookmarks = public_metrics.get("bookmark_count", 0) or 0
        
        # Extract non-public metrics (requires ownership)
        impressions = non_public_metrics.get("impression_count", 0) or 0
        url_clicks = non_public_metrics.get("url_link_clicks", 0) or 0
        profile_clicks = non_public_metrics.get("user_profile_clicks", 0) or 0
        
        # If non-public metrics not available, try organic metrics
        if impressions == 0:
            impressions = organic_metrics.get("impression_count", 0) or 0
        
        if url_clicks == 0:
            url_clicks = organic_metrics.get("url_link_clicks", 0) or 0
        
        # Total clicks
        total_clicks = url_clicks + profile_clicks
        
        # Calculate engagement rate
        engagement_rate = self._calculate_engagement_rate(
            likes=likes,
            comments=replies,
            shares=retweets + quotes,
            impressions=impressions
        )
        
        # Calculate CTR
        click_through_rate = 0.0
        if impressions > 0:
            click_through_rate = round((total_clicks / impressions) * 100, 2)
        
        return {
            "likes_count": likes,
            "comments_count": replies,
            "shares_count": retweets,
            "reactions_count": likes,  # Twitter uses likes as reactions
            "retweets_count": retweets,
            "quote_tweets_count": quotes,
            "impressions": impressions,
            "reach": impressions,  # Twitter uses impressions as reach
            "clicks": total_clicks,
            "engagement_rate": engagement_rate,
            "click_through_rate": click_through_rate,
            # Twitter-specific metrics
            "bookmarks_count": bookmarks,
            "url_clicks": url_clicks,
            "profile_clicks": profile_clicks,
            # Video metrics (not available in basic response)
            "video_views": 0,
            "video_watch_time": 0,
        }
    
    def fetch_multiple_tweets(
        self,
        tweet_ids: list[str],
        max_results: int = 100
    ) -> Dict[str, Dict[str, Any]]:
        """
        Fetch analytics for multiple tweets in a single request.
        
        Args:
            tweet_ids: List of Twitter tweet IDs
            max_results: Maximum number of results (max 100 per request)
            
        Returns:
            Dictionary mapping tweet IDs to analytics data
        """
        if not tweet_ids:
            return {}
        
        # Twitter allows max 100 IDs per request
        tweet_ids = tweet_ids[:min(len(tweet_ids), max_results)]
        
        url = f"{self.BASE_URL}/{self.API_VERSION}/tweets"
        
        params = {
            "ids": ",".join(tweet_ids),
            "tweet.fields": "public_metrics,non_public_metrics,organic_metrics,created_at",
        }
        
        try:
            response = self._make_request(
                method="GET",
                url=url,
                params=params
            )
            
            # Parse each tweet
            results = {}
            for tweet in response.get("data", []):
                tweet_id = tweet.get("id")
                if tweet_id:
                    analytics = self._parse_twitter_analytics(tweet)
                    analytics["fetched_at"] = datetime.utcnow()
                    analytics["platform"] = "twitter"
                    analytics["platform_post_id"] = tweet_id
                    analytics["platform_post_url"] = f"https://twitter.com/i/web/status/{tweet_id}"
                    results[tweet_id] = analytics
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to fetch multiple tweets: {e}")
            raise PlatformAPIError(
                f"Failed to fetch multiple tweets: {str(e)}",
                platform="twitter"
            )
    
    def fetch_user_metrics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch metrics for the authenticated user or a specific user.
        
        Args:
            user_id: Twitter user ID (optional, defaults to authenticated user)
            
        Returns:
            User metrics including followers, following, tweet count
        """
        if user_id:
            url = f"{self.BASE_URL}/{self.API_VERSION}/users/{user_id}"
        else:
            url = f"{self.BASE_URL}/{self.API_VERSION}/users/me"
        
        params = {
            "user.fields": "public_metrics,created_at"
        }
        
        try:
            response = self._make_request(
                method="GET",
                url=url,
                params=params
            )
            
            user_data = response.get("data", {})
            public_metrics = user_data.get("public_metrics", {})
            
            return {
                "user_id": user_data.get("id"),
                "username": user_data.get("username"),
                "followers_count": public_metrics.get("followers_count", 0),
                "following_count": public_metrics.get("following_count", 0),
                "tweet_count": public_metrics.get("tweet_count", 0),
                "listed_count": public_metrics.get("listed_count", 0),
                "created_at": user_data.get("created_at"),
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch user metrics: {e}")
            raise PlatformAPIError(
                f"Failed to fetch user metrics: {str(e)}",
                platform="twitter"
            )
