"""Base class for platform analytics fetchers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import logging
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class BasePlatformFetcher(ABC):
    """
    Abstract base class for platform analytics fetchers.
    
    All platform-specific fetchers should inherit from this class and implement
    the fetch_post_analytics() method.
    """
    
    def __init__(
        self, 
        access_token: str,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        timeout: int = 30
    ):
        """
        Initialize the fetcher.
        
        Args:
            access_token: OAuth access token for the platform
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor for retries
            timeout: Request timeout in seconds
        """
        self.access_token = access_token
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    @abstractmethod
    def fetch_post_analytics(
        self, 
        post_id: str,
        platform_post_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch analytics data for a specific post.
        
        Args:
            post_id: Internal post ID
            platform_post_id: Platform-specific post ID
            
        Returns:
            Dictionary containing analytics data with standardized keys:
            - likes_count: Number of likes/reactions
            - comments_count: Number of comments
            - shares_count: Number of shares/retweets
            - impressions: Number of impressions/views
            - reach: Number of unique users reached
            - clicks: Number of clicks
            - engagement_rate: Calculated engagement rate
            - fetched_at: Timestamp when data was fetched
            
        Raises:
            PlatformAPIError: If the API request fails
            RateLimitError: If rate limit is exceeded
        """
        pass
    
    def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        retry_on_rate_limit: bool = True
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with retry logic and error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers
            params: Query parameters
            json_data: JSON body data
            retry_on_rate_limit: Whether to retry on rate limit errors
            
        Returns:
            JSON response data
            
        Raises:
            PlatformAPIError: If the request fails
            RateLimitError: If rate limit is exceeded and retries exhausted
        """
        if headers is None:
            headers = {}
            
        # Add authorization header
        headers["Authorization"] = f"Bearer {self.access_token}"
        
        retry_count = 0
        
        while retry_count <= self.max_retries:
            try:
                logger.info(f"Making {method} request to {url} (attempt {retry_count + 1})")
                
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    timeout=self.timeout
                )
                
                # Check for rate limiting
                if response.status_code == 429:
                    if retry_on_rate_limit:
                        retry_after = self._handle_rate_limit(response, retry_count)
                        logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                        time.sleep(retry_after)
                        retry_count += 1
                        continue
                    else:
                        from .exceptions import RateLimitError
                        raise RateLimitError(
                            "Rate limit exceeded",
                            retry_after=response.headers.get("Retry-After")
                        )
                
                # Check for other errors
                response.raise_for_status()
                
                # Return JSON data
                return response.json()
                
            except requests.exceptions.Timeout:
                logger.error(f"Request timeout (attempt {retry_count + 1})")
                retry_count += 1
                if retry_count > self.max_retries:
                    from .exceptions import PlatformAPIError
                    raise PlatformAPIError(
                        f"Request timed out after {self.max_retries} retries"
                    )
                time.sleep(self.backoff_factor ** retry_count)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                from .exceptions import PlatformAPIError
                raise PlatformAPIError(f"Request failed: {e}")
        
        from .exceptions import PlatformAPIError
        raise PlatformAPIError(f"Request failed after {self.max_retries} retries")
    
    def _handle_rate_limit(
        self, 
        response: requests.Response, 
        retry_count: int
    ) -> float:
        """
        Calculate wait time for rate limit handling.
        
        Args:
            response: Response object with rate limit headers
            retry_count: Current retry attempt number
            
        Returns:
            Number of seconds to wait before retry
        """
        # Check for Retry-After header (standard)
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                pass
        
        # Check for X-RateLimit-Reset header (common pattern)
        rate_limit_reset = response.headers.get("X-RateLimit-Reset")
        if rate_limit_reset:
            try:
                reset_time = int(rate_limit_reset)
                wait_time = max(0, reset_time - int(time.time()))
                return float(wait_time)
            except ValueError:
                pass
        
        # Fall back to exponential backoff
        return self.backoff_factor ** retry_count
    
    def _parse_analytics_response(
        self, 
        raw_data: Dict[str, Any],
        field_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Parse platform-specific analytics response into standardized format.
        
        Args:
            raw_data: Raw API response data
            field_mapping: Mapping of standard field names to platform-specific field paths
                          e.g., {"likes_count": "engagement.likeCount"}
                          
        Returns:
            Standardized analytics dictionary
        """
        analytics = {}
        
        for standard_field, platform_field in field_mapping.items():
            # Support nested field paths (e.g., "engagement.likeCount")
            value = raw_data
            for key in platform_field.split("."):
                value = value.get(key, 0) if isinstance(value, dict) else 0
            analytics[standard_field] = value or 0
        
        return analytics
    
    def _calculate_engagement_rate(
        self,
        likes: int,
        comments: int,
        shares: int,
        impressions: int
    ) -> float:
        """
        Calculate engagement rate.
        
        Args:
            likes: Number of likes
            comments: Number of comments
            shares: Number of shares
            impressions: Number of impressions
            
        Returns:
            Engagement rate as percentage (0-100)
        """
        if impressions == 0:
            return 0.0
            
        total_engagement = likes + comments + shares
        engagement_rate = (total_engagement / impressions) * 100
        
        return round(engagement_rate, 2)
