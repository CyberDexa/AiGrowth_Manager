"""LinkedIn analytics fetcher."""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

from .base_fetcher import BasePlatformFetcher
from .exceptions import PlatformAPIError, PostNotFoundError

logger = logging.getLogger(__name__)


class LinkedInAnalyticsFetcher(BasePlatformFetcher):
    """
    Fetches analytics data from LinkedIn API.
    
    LinkedIn API Endpoints:
    - Share Statistics: /v2/organizationalEntityShareStatistics
    - Post Details: /v2/ugcPosts/{post-id}
    - Engagement Stats: /v2/socialActions/{share-urn}
    
    Rate Limits:
    - 100 requests per day for free tier
    - 500 requests per day for partner tier
    """
    
    BASE_URL = "https://api.linkedin.com"
    API_VERSION = "v2"
    
    def __init__(
        self,
        access_token: str,
        organization_id: Optional[str] = None,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        timeout: int = 30
    ):
        """
        Initialize LinkedIn fetcher.
        
        Args:
            access_token: LinkedIn OAuth 2.0 access token
            organization_id: LinkedIn organization/company ID
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor
            timeout: Request timeout in seconds
        """
        super().__init__(access_token, max_retries, backoff_factor, timeout)
        self.organization_id = organization_id
        
    def fetch_post_analytics(
        self,
        post_id: str,
        platform_post_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch analytics for a LinkedIn post.
        
        Args:
            post_id: Internal post ID
            platform_post_id: LinkedIn post URN (e.g., "urn:li:share:123456")
            
        Returns:
            Standardized analytics dictionary
            
        Raises:
            PostNotFoundError: If post not found
            PlatformAPIError: If API request fails
        """
        if not platform_post_id:
            raise PlatformAPIError(
                "LinkedIn post ID is required",
                platform="linkedin"
            )
        
        logger.info(f"Fetching LinkedIn analytics for post {platform_post_id}")
        
        try:
            # Fetch share statistics
            share_stats = self._fetch_share_statistics(platform_post_id)
            
            # Fetch post details for additional metrics
            post_details = self._fetch_post_details(platform_post_id)
            
            # Parse and standardize the data
            analytics = self._parse_linkedin_analytics(share_stats, post_details)
            
            # Add metadata
            analytics["fetched_at"] = datetime.utcnow()
            analytics["platform"] = "linkedin"
            analytics["platform_post_id"] = platform_post_id
            
            logger.info(f"Successfully fetched LinkedIn analytics for post {platform_post_id}")
            return analytics
            
        except PostNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch LinkedIn analytics: {e}")
            raise PlatformAPIError(
                f"Failed to fetch LinkedIn analytics: {str(e)}",
                platform="linkedin"
            )
    
    def _fetch_share_statistics(self, share_urn: str) -> Dict[str, Any]:
        """
        Fetch share statistics from LinkedIn API.
        
        Args:
            share_urn: LinkedIn share URN
            
        Returns:
            Share statistics data
        """
        url = f"{self.BASE_URL}/{self.API_VERSION}/organizationalEntityShareStatistics"
        
        params = {
            "q": "organizationalEntity",
            "organizationalEntity": self.organization_id or "urn:li:organization:0",
            "shares": [share_urn]
        }
        
        headers = {
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202401"
        }
        
        try:
            response = self._make_request(
                method="GET",
                url=url,
                headers=headers,
                params=params
            )
            
            # Check if we got results
            if not response.get("elements"):
                raise PostNotFoundError(
                    f"LinkedIn post {share_urn} not found",
                    post_id=share_urn,
                    platform="linkedin"
                )
            
            return response["elements"][0]
            
        except PostNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch share statistics: {e}")
            raise PlatformAPIError(
                f"Failed to fetch share statistics: {str(e)}",
                platform="linkedin"
            )
    
    def _fetch_post_details(self, share_urn: str) -> Dict[str, Any]:
        """
        Fetch post details from LinkedIn API.
        
        Args:
            share_urn: LinkedIn share URN
            
        Returns:
            Post details data
        """
        # Extract post ID from URN (e.g., "urn:li:share:123456" -> "123456")
        post_id = share_urn.split(":")[-1]
        
        url = f"{self.BASE_URL}/{self.API_VERSION}/ugcPosts/{post_id}"
        
        headers = {
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202401"
        }
        
        try:
            response = self._make_request(
                method="GET",
                url=url,
                headers=headers
            )
            
            return response
            
        except Exception as e:
            logger.warning(f"Failed to fetch post details (non-critical): {e}")
            return {}
    
    def _parse_linkedin_analytics(
        self,
        share_stats: Dict[str, Any],
        post_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse LinkedIn API response into standardized format.
        
        Args:
            share_stats: Share statistics from API
            post_details: Post details from API
            
        Returns:
            Standardized analytics dictionary
        """
        # LinkedIn uses nested "totalShareStatistics" object
        total_stats = share_stats.get("totalShareStatistics", {})
        
        # Extract metrics
        likes = total_stats.get("likeCount", 0) or 0
        comments = total_stats.get("commentCount", 0) or 0
        shares = total_stats.get("shareCount", 0) or 0
        impressions = total_stats.get("impressionCount", 0) or 0
        clicks = total_stats.get("clickCount", 0) or 0
        
        # LinkedIn also provides engagement metrics
        engagement = total_stats.get("engagement", 0) or 0
        unique_impressions = total_stats.get("uniqueImpressionsCount", 0) or 0
        
        # Calculate engagement rate
        engagement_rate = self._calculate_engagement_rate(
            likes=likes,
            comments=comments,
            shares=shares,
            impressions=impressions
        )
        
        # Calculate CTR
        click_through_rate = 0.0
        if impressions > 0:
            click_through_rate = round((clicks / impressions) * 100, 2)
        
        return {
            "likes_count": likes,
            "comments_count": comments,
            "shares_count": shares,
            "reactions_count": likes,  # LinkedIn uses likes as reactions
            "impressions": impressions,
            "reach": unique_impressions or impressions,  # Use unique impressions if available
            "clicks": clicks,
            "engagement_rate": engagement_rate,
            "click_through_rate": click_through_rate,
            # LinkedIn-specific metrics
            "total_engagement": engagement,
            # Video metrics (if available)
            "video_views": post_details.get("videoViews", 0) or 0,
            "video_watch_time": 0,  # LinkedIn doesn't provide this in basic API
            # Default Twitter metrics (not applicable)
            "retweets_count": 0,
            "quote_tweets_count": 0,
        }
    
    def fetch_organization_analytics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch organization-level analytics.
        
        Args:
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            
        Returns:
            Organization analytics summary
        """
        if not self.organization_id:
            raise PlatformAPIError(
                "Organization ID is required for organization analytics",
                platform="linkedin"
            )
        
        url = f"{self.BASE_URL}/{self.API_VERSION}/organizationalEntityFollowerStatistics"
        
        params = {
            "q": "organizationalEntity",
            "organizationalEntity": self.organization_id
        }
        
        if start_date:
            params["timeIntervals.timeGranularityType"] = "DAY"
            params["timeIntervals.timeRange.start"] = start_date
            
        if end_date:
            params["timeIntervals.timeRange.end"] = end_date
        
        headers = {
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202401"
        }
        
        try:
            response = self._make_request(
                method="GET",
                url=url,
                headers=headers,
                params=params
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to fetch organization analytics: {e}")
            raise PlatformAPIError(
                f"Failed to fetch organization analytics: {str(e)}",
                platform="linkedin"
            )
