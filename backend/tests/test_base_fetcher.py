"""Unit tests for BasePlatformFetcher."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from requests.exceptions import Timeout, RequestException
import time

from app.services.platform_fetchers.base_fetcher import BasePlatformFetcher
from app.services.platform_fetchers.exceptions import (
    PlatformAPIError,
    RateLimitError
)


# Create concrete implementation for testing abstract class
class TestFetcher(BasePlatformFetcher):
    """Concrete implementation of BasePlatformFetcher for testing."""
    
    def fetch_post_analytics(self, post_id, platform_post_id=None):
        """Test implementation."""
        return self._make_request(
            method="GET",
            url="https://api.test.com/posts",
            params={"id": platform_post_id}
        )


class TestBasePlatformFetcher:
    """Test suite for BasePlatformFetcher."""
    
    def test_initialization(self):
        """Test fetcher initialization with default parameters."""
        fetcher = TestFetcher(access_token="test_token")
        
        assert fetcher.access_token == "test_token"
        assert fetcher.max_retries == 3
        assert fetcher.backoff_factor == 2.0
        assert fetcher.timeout == 30
        assert fetcher.session is not None
    
    def test_initialization_custom_params(self):
        """Test fetcher initialization with custom parameters."""
        fetcher = TestFetcher(
            access_token="custom_token",
            max_retries=5,
            backoff_factor=3.0,
            timeout=60
        )
        
        assert fetcher.access_token == "custom_token"
        assert fetcher.max_retries == 5
        assert fetcher.backoff_factor == 3.0
        assert fetcher.timeout == 60
    
    @patch('requests.Session.request')
    def test_make_request_success(self, mock_request):
        """Test successful API request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test_data"}
        mock_request.return_value = mock_response
        
        fetcher = TestFetcher(access_token="test_token")
        result = fetcher._make_request(
            method="GET",
            url="https://api.test.com/endpoint"
        )
        
        assert result == {"data": "test_data"}
        assert mock_request.call_count == 1
        
        # Verify Authorization header was added
        call_kwargs = mock_request.call_args[1]
        assert call_kwargs["headers"]["Authorization"] == "Bearer test_token"
    
    @patch('requests.Session.request')
    def test_make_request_with_params(self, mock_request):
        """Test API request with query parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_request.return_value = mock_response
        
        fetcher = TestFetcher(access_token="test_token")
        result = fetcher._make_request(
            method="GET",
            url="https://api.test.com/endpoint",
            params={"key1": "value1", "key2": "value2"}
        )
        
        assert result == {"result": "success"}
        call_kwargs = mock_request.call_args[1]
        assert call_kwargs["params"] == {"key1": "value1", "key2": "value2"}
    
    @patch('requests.Session.request')
    def test_make_request_with_json_body(self, mock_request):
        """Test API request with JSON body."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"created": True}
        mock_request.return_value = mock_response
        
        fetcher = TestFetcher(access_token="test_token")
        result = fetcher._make_request(
            method="POST",
            url="https://api.test.com/create",
            json_data={"name": "test", "value": 123}
        )
        
        assert result == {"created": True}
        call_kwargs = mock_request.call_args[1]
        assert call_kwargs["json"] == {"name": "test", "value": 123}
    
    @patch('requests.Session.request')
    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_rate_limit_with_retry_after_header(self, mock_sleep, mock_request):
        """Test rate limit handling with Retry-After header."""
        # First request: rate limited
        rate_limit_response = Mock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {"Retry-After": "60"}
        
        # Second request: success
        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = {"data": "success"}
        
        mock_request.side_effect = [rate_limit_response, success_response]
        
        fetcher = TestFetcher(access_token="test_token")
        result = fetcher._make_request(
            method="GET",
            url="https://api.test.com/endpoint",
            retry_on_rate_limit=True
        )
        
        assert result == {"data": "success"}
        assert mock_request.call_count == 2
        mock_sleep.assert_called_once_with(60.0)
    
    @patch('requests.Session.request')
    def test_rate_limit_no_retry(self, mock_request):
        """Test rate limit raises error when retry disabled."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_request.return_value = mock_response
        
        fetcher = TestFetcher(access_token="test_token")
        
        with pytest.raises(RateLimitError) as exc_info:
            fetcher._make_request(
                method="GET",
                url="https://api.test.com/endpoint",
                retry_on_rate_limit=False
            )
        
        assert exc_info.value.retry_after == "60"
    
    @patch('requests.Session.request')
    @patch('time.sleep')
    def test_retry_on_timeout(self, mock_sleep, mock_request):
        """Test retry logic on timeout."""
        # First two requests: timeout
        # Third request: success
        mock_request.side_effect = [
            Timeout("Request timeout"),
            Timeout("Request timeout"),
            Mock(status_code=200, json=lambda: {"data": "success"})
        ]
        
        fetcher = TestFetcher(access_token="test_token", max_retries=3)
        result = fetcher._make_request(
            method="GET",
            url="https://api.test.com/endpoint"
        )
        
        assert result == {"data": "success"}
        assert mock_request.call_count == 3
        assert mock_sleep.call_count == 2  # Called after first two timeouts
    
    @patch('requests.Session.request')
    @patch('time.sleep')
    def test_max_retries_exceeded(self, mock_sleep, mock_request):
        """Test that exception is raised after max retries exceeded."""
        mock_request.side_effect = Timeout("Request timeout")
        
        fetcher = TestFetcher(access_token="test_token", max_retries=2)
        
        with pytest.raises(PlatformAPIError) as exc_info:
            fetcher._make_request(
                method="GET",
                url="https://api.test.com/endpoint"
            )
        
        assert "timed out" in str(exc_info.value).lower()
        assert mock_request.call_count == 3  # Initial + 2 retries
    
    @patch('requests.Session.request')
    def test_request_exception(self, mock_request):
        """Test handling of request exceptions."""
        mock_request.side_effect = RequestException("Connection error")
        
        fetcher = TestFetcher(access_token="test_token")
        
        with pytest.raises(PlatformAPIError) as exc_info:
            fetcher._make_request(
                method="GET",
                url="https://api.test.com/endpoint"
            )
        
        assert "Connection error" in str(exc_info.value)
    
    def test_handle_rate_limit_with_retry_after(self):
        """Test rate limit wait time calculation with Retry-After header."""
        fetcher = TestFetcher(access_token="test_token")
        
        mock_response = Mock()
        mock_response.headers = {"Retry-After": "120"}
        
        wait_time = fetcher._handle_rate_limit(mock_response, retry_count=0)
        
        assert wait_time == 120.0
    
    @patch('time.time')
    def test_handle_rate_limit_with_reset_header(self, mock_time):
        """Test rate limit wait time calculation with X-RateLimit-Reset header."""
        current_time = 1696156800  # Mock current time
        reset_time = current_time + 300  # Reset in 5 minutes
        
        mock_time.return_value = current_time
        
        fetcher = TestFetcher(access_token="test_token")
        
        mock_response = Mock()
        mock_response.headers = {"X-RateLimit-Reset": str(reset_time)}
        
        wait_time = fetcher._handle_rate_limit(mock_response, retry_count=0)
        
        assert wait_time == 300.0
    
    def test_handle_rate_limit_exponential_backoff(self):
        """Test exponential backoff when no rate limit headers present."""
        fetcher = TestFetcher(access_token="test_token", backoff_factor=2.0)
        
        mock_response = Mock()
        mock_response.headers = {}
        
        wait_time_0 = fetcher._handle_rate_limit(mock_response, retry_count=0)
        wait_time_1 = fetcher._handle_rate_limit(mock_response, retry_count=1)
        wait_time_2 = fetcher._handle_rate_limit(mock_response, retry_count=2)
        
        assert wait_time_0 == 1.0  # 2.0^0
        assert wait_time_1 == 2.0  # 2.0^1
        assert wait_time_2 == 4.0  # 2.0^2
    
    def test_parse_analytics_response(self):
        """Test parsing platform-specific response to standardized format."""
        fetcher = TestFetcher(access_token="test_token")
        
        raw_data = {
            "engagement": {
                "likes": 100,
                "comments": 20,
                "shares": 10
            },
            "reach": {
                "impressions": 5000,
                "unique": 4000
            }
        }
        
        field_mapping = {
            "likes_count": "engagement.likes",
            "comments_count": "engagement.comments",
            "shares_count": "engagement.shares",
            "impressions": "reach.impressions",
            "reach": "reach.unique"
        }
        
        result = fetcher._parse_analytics_response(raw_data, field_mapping)
        
        assert result["likes_count"] == 100
        assert result["comments_count"] == 20
        assert result["shares_count"] == 10
        assert result["impressions"] == 5000
        assert result["reach"] == 4000
    
    def test_parse_analytics_response_missing_fields(self):
        """Test parsing with missing fields defaults to 0."""
        fetcher = TestFetcher(access_token="test_token")
        
        raw_data = {
            "engagement": {
                "likes": 50
            }
        }
        
        field_mapping = {
            "likes_count": "engagement.likes",
            "comments_count": "engagement.comments",  # Missing
            "shares_count": "missing.field"  # Missing
        }
        
        result = fetcher._parse_analytics_response(raw_data, field_mapping)
        
        assert result["likes_count"] == 50
        assert result["comments_count"] == 0
        assert result["shares_count"] == 0
    
    def test_calculate_engagement_rate_success(self):
        """Test engagement rate calculation."""
        fetcher = TestFetcher(access_token="test_token")
        
        engagement_rate = fetcher._calculate_engagement_rate(
            likes=100,
            comments=20,
            shares=10,
            impressions=5000
        )
        
        # (100 + 20 + 10) / 5000 * 100 = 2.6%
        assert engagement_rate == 2.6
    
    def test_calculate_engagement_rate_zero_impressions(self):
        """Test engagement rate returns 0 when impressions is 0."""
        fetcher = TestFetcher(access_token="test_token")
        
        engagement_rate = fetcher._calculate_engagement_rate(
            likes=100,
            comments=20,
            shares=10,
            impressions=0
        )
        
        assert engagement_rate == 0.0
    
    def test_calculate_engagement_rate_high_engagement(self):
        """Test engagement rate with high engagement."""
        fetcher = TestFetcher(access_token="test_token")
        
        engagement_rate = fetcher._calculate_engagement_rate(
            likes=5000,
            comments=800,
            shares=300,
            impressions=10000
        )
        
        # (5000 + 800 + 300) / 10000 * 100 = 61%
        assert engagement_rate == 61.0
