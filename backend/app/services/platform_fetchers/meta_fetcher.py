"""Meta (Facebook & Instagram) analytics fetcher."""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from .base_fetcher import BasePlatformFetcher
from .exceptions import PlatformAPIError, PostNotFoundError

logger = logging.getLogger(__name__)


class MetaAnalyticsFetcher(BasePlatformFetcher):
    """
    Fetches analytics data from Meta (Facebook & Instagram) Graph API.
    
    Meta Graph API Endpoints:
    - Facebook Page Post: /{post-id}?fields=insights,reactions,comments,shares
    - Instagram Media: /{media-id}?fields=insights,like_count,comments_count
    - Facebook Page Insights: /{page-id}/insights
    - Instagram Account Insights: /{instagram-account-id}/insights
    
    Rate Limits:
    - 200 requests per hour per user (default)
    - 4800 requests per hour per app (default)
    
    Note: Requires appropriate permissions (pages_read_engagement, instagram_basic, instagram_manage_insights)
    """
    
    BASE_URL = "https://graph.facebook.com"
    API_VERSION = "v18.0"
    
    def __init__(
        self,
        access_token: str,
        page_id: Optional[str] = None,
        instagram_account_id: Optional[str] = None,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        timeout: int = 30
    ):
        """
        Initialize Meta fetcher.
        
        Args:
            access_token: Meta OAuth access token
            page_id: Facebook Page ID
            instagram_account_id: Instagram Business Account ID
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor
            timeout: Request timeout in seconds
        """
        super().__init__(access_token, max_retries, backoff_factor, timeout)
        self.page_id = page_id
        self.instagram_account_id = instagram_account_id
    
    def fetch_post_analytics(
        self,
        post_id: str,
        platform_post_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch analytics for a Meta post (Facebook or Instagram).
        
        This method automatically detects the platform based on the post ID format.
        
        Args:
            post_id: Internal post ID
            platform_post_id: Meta post ID (Facebook: {page-id}_{post-id}, Instagram: {media-id})
            
        Returns:
            Standardized analytics dictionary
            
        Raises:
            PostNotFoundError: If post not found
            PlatformAPIError: If API request fails
        """
        if not platform_post_id:
            raise PlatformAPIError(
                "Meta post ID is required",
                platform="facebook"
            )
        
        # Detect if it's Facebook or Instagram based on ID format
        # Facebook post IDs contain underscore: {page_id}_{post_id}
        # Instagram media IDs are numeric
        if "_" in platform_post_id:
            return self.fetch_facebook_analytics(post_id, platform_post_id)
        else:
            return self.fetch_instagram_analytics(post_id, platform_post_id)
    
    def fetch_facebook_analytics(
        self,
        post_id: str,
        facebook_post_id: str
    ) -> Dict[str, Any]:
        """
        Fetch analytics for a Facebook post.
        
        Args:
            post_id: Internal post ID
            facebook_post_id: Facebook post ID (format: {page_id}_{post_id})
            
        Returns:
            Standardized analytics dictionary
        """
        logger.info(f"Fetching Facebook analytics for post {facebook_post_id}")
        
        try:
            # Fetch post data with metrics
            post_data = self._fetch_facebook_post_data(facebook_post_id)
            
            # Fetch post insights (impressions, reach, etc.)
            insights = self._fetch_facebook_post_insights(facebook_post_id)
            
            # Parse and standardize the data
            analytics = self._parse_facebook_analytics(post_data, insights)
            
            # Add metadata
            analytics["fetched_at"] = datetime.utcnow()
            analytics["platform"] = "facebook"
            analytics["platform_post_id"] = facebook_post_id
            
            logger.info(f"Successfully fetched Facebook analytics for post {facebook_post_id}")
            return analytics
            
        except PostNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch Facebook analytics: {e}")
            raise PlatformAPIError(
                f"Failed to fetch Facebook analytics: {str(e)}",
                platform="facebook"
            )
    
    def fetch_instagram_analytics(
        self,
        post_id: str,
        instagram_media_id: str
    ) -> Dict[str, Any]:
        """
        Fetch analytics for an Instagram post.
        
        Args:
            post_id: Internal post ID
            instagram_media_id: Instagram media ID
            
        Returns:
            Standardized analytics dictionary
        """
        logger.info(f"Fetching Instagram analytics for media {instagram_media_id}")
        
        try:
            # Fetch media data with metrics
            media_data = self._fetch_instagram_media_data(instagram_media_id)
            
            # Fetch media insights
            insights = self._fetch_instagram_media_insights(instagram_media_id)
            
            # Parse and standardize the data
            analytics = self._parse_instagram_analytics(media_data, insights)
            
            # Add metadata
            analytics["fetched_at"] = datetime.utcnow()
            analytics["platform"] = "instagram"
            analytics["platform_post_id"] = instagram_media_id
            
            logger.info(f"Successfully fetched Instagram analytics for media {instagram_media_id}")
            return analytics
            
        except PostNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch Instagram analytics: {e}")
            raise PlatformAPIError(
                f"Failed to fetch Instagram analytics: {str(e)}",
                platform="instagram"
            )
    
    def _fetch_facebook_post_data(self, post_id: str) -> Dict[str, Any]:
        """Fetch Facebook post data."""
        url = f"{self.BASE_URL}/{self.API_VERSION}/{post_id}"
        
        params = {
            "fields": "reactions.summary(total_count),comments.summary(total_count),shares,created_time,message,permalink_url"
        }
        
        try:
            response = self._make_request(
                method="GET",
                url=url,
                params=params
            )
            
            if "error" in response:
                raise PostNotFoundError(
                    f"Facebook post {post_id} not found",
                    post_id=post_id,
                    platform="facebook"
                )
            
            return response
            
        except PostNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch Facebook post data: {e}")
            raise PlatformAPIError(
                f"Failed to fetch Facebook post data: {str(e)}",
                platform="facebook"
            )
    
    def _fetch_facebook_post_insights(self, post_id: str) -> Dict[str, Any]:
        """Fetch Facebook post insights (impressions, reach, clicks)."""
        url = f"{self.BASE_URL}/{self.API_VERSION}/{post_id}/insights"
        
        # Request specific metrics
        params = {
            "metric": "post_impressions,post_impressions_unique,post_engaged_users,post_clicks,post_video_views"
        }
        
        try:
            response = self._make_request(
                method="GET",
                url=url,
                params=params
            )
            
            # Convert insights array to dictionary
            insights_dict = {}
            for insight in response.get("data", []):
                metric_name = insight.get("name")
                metric_value = insight.get("values", [{}])[0].get("value", 0)
                insights_dict[metric_name] = metric_value
            
            return insights_dict
            
        except Exception as e:
            logger.warning(f"Failed to fetch Facebook post insights (non-critical): {e}")
            return {}
    
    def _fetch_instagram_media_data(self, media_id: str) -> Dict[str, Any]:
        """Fetch Instagram media data."""
        url = f"{self.BASE_URL}/{self.API_VERSION}/{media_id}"
        
        params = {
            "fields": "id,media_type,media_url,permalink,timestamp,like_count,comments_count,caption"
        }
        
        try:
            response = self._make_request(
                method="GET",
                url=url,
                params=params
            )
            
            if "error" in response:
                raise PostNotFoundError(
                    f"Instagram media {media_id} not found",
                    post_id=media_id,
                    platform="instagram"
                )
            
            return response
            
        except PostNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch Instagram media data: {e}")
            raise PlatformAPIError(
                f"Failed to fetch Instagram media data: {str(e)}",
                platform="instagram"
            )
    
    def _fetch_instagram_media_insights(self, media_id: str) -> Dict[str, Any]:
        """Fetch Instagram media insights."""
        url = f"{self.BASE_URL}/{self.API_VERSION}/{media_id}/insights"
        
        # Different metrics for different media types
        # For posts: impressions, reach, engagement, saved
        # For videos: impressions, reach, video_views
        # For stories: impressions, reach, exits, replies
        params = {
            "metric": "impressions,reach,engagement,saved,video_views"
        }
        
        try:
            response = self._make_request(
                method="GET",
                url=url,
                params=params
            )
            
            # Convert insights array to dictionary
            insights_dict = {}
            for insight in response.get("data", []):
                metric_name = insight.get("name")
                metric_value = insight.get("values", [{}])[0].get("value", 0)
                insights_dict[metric_name] = metric_value
            
            return insights_dict
            
        except Exception as e:
            logger.warning(f"Failed to fetch Instagram media insights (non-critical): {e}")
            return {}
    
    def _parse_facebook_analytics(
        self,
        post_data: Dict[str, Any],
        insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse Facebook data into standardized format."""
        # Extract engagement metrics
        reactions = post_data.get("reactions", {}).get("summary", {}).get("total_count", 0) or 0
        comments = post_data.get("comments", {}).get("summary", {}).get("total_count", 0) or 0
        shares = post_data.get("shares", {}).get("count", 0) or 0
        
        # Extract insights
        impressions = insights.get("post_impressions", 0) or 0
        reach = insights.get("post_impressions_unique", 0) or 0
        engaged_users = insights.get("post_engaged_users", 0) or 0
        clicks = insights.get("post_clicks", 0) or 0
        video_views = insights.get("post_video_views", 0) or 0
        
        # Calculate engagement rate
        engagement_rate = self._calculate_engagement_rate(
            likes=reactions,
            comments=comments,
            shares=shares,
            impressions=impressions
        )
        
        # Calculate CTR
        click_through_rate = 0.0
        if impressions > 0:
            click_through_rate = round((clicks / impressions) * 100, 2)
        
        return {
            "likes_count": reactions,
            "comments_count": comments,
            "shares_count": shares,
            "reactions_count": reactions,
            "impressions": impressions,
            "reach": reach,
            "clicks": clicks,
            "engagement_rate": engagement_rate,
            "click_through_rate": click_through_rate,
            "video_views": video_views,
            "video_watch_time": 0,  # Not available in basic API
            # Facebook-specific
            "engaged_users": engaged_users,
            # Default Twitter/LinkedIn metrics (not applicable)
            "retweets_count": 0,
            "quote_tweets_count": 0,
        }
    
    def _parse_instagram_analytics(
        self,
        media_data: Dict[str, Any],
        insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse Instagram data into standardized format."""
        # Extract engagement metrics
        likes = media_data.get("like_count", 0) or 0
        comments = media_data.get("comments_count", 0) or 0
        
        # Extract insights
        impressions = insights.get("impressions", 0) or 0
        reach = insights.get("reach", 0) or 0
        engagement = insights.get("engagement", 0) or 0
        saved = insights.get("saved", 0) or 0
        video_views = insights.get("video_views", 0) or 0
        
        # Instagram shares are not directly available in API
        shares = 0
        
        # Calculate engagement rate
        engagement_rate = self._calculate_engagement_rate(
            likes=likes,
            comments=comments,
            shares=shares,
            impressions=impressions
        )
        
        return {
            "likes_count": likes,
            "comments_count": comments,
            "shares_count": shares,
            "reactions_count": likes,
            "impressions": impressions,
            "reach": reach,
            "clicks": 0,  # Not available in basic API
            "engagement_rate": engagement_rate,
            "click_through_rate": 0.0,
            "video_views": video_views,
            "video_watch_time": 0,  # Not available in basic API
            # Instagram-specific
            "saved_count": saved,
            "total_engagement": engagement,
            # Default Twitter/LinkedIn metrics (not applicable)
            "retweets_count": 0,
            "quote_tweets_count": 0,
        }
    
    def fetch_page_insights(
        self,
        metric_names: Optional[List[str]] = None,
        period: str = "day"
    ) -> Dict[str, Any]:
        """
        Fetch Facebook Page-level insights.
        
        Args:
            metric_names: List of metrics to fetch (default: engagement metrics)
            period: Time period (day, week, days_28)
            
        Returns:
            Page insights dictionary
        """
        if not self.page_id:
            raise PlatformAPIError(
                "Page ID is required for page insights",
                platform="facebook"
            )
        
        if metric_names is None:
            metric_names = [
                "page_impressions",
                "page_impressions_unique",
                "page_post_engagements",
                "page_fans",
                "page_fan_adds",
                "page_fan_removes"
            ]
        
        url = f"{self.BASE_URL}/{self.API_VERSION}/{self.page_id}/insights"
        
        params = {
            "metric": ",".join(metric_names),
            "period": period
        }
        
        try:
            response = self._make_request(
                method="GET",
                url=url,
                params=params
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to fetch page insights: {e}")
            raise PlatformAPIError(
                f"Failed to fetch page insights: {str(e)}",
                platform="facebook"
            )
