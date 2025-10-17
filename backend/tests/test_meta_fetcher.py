"""
Unit tests for Meta (Facebook & Instagram) platform fetcher.

Tests Meta-specific API interactions, response parsing,
and analytics data extraction with comprehensive mocking.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from app.services.platform_fetchers.meta_fetcher import MetaAnalyticsFetcher
from app.services.platform_fetchers.exceptions import (
    PlatformAPIError,
    PostNotFoundError,
)
from tests.fixtures.meta_responses import (
    FACEBOOK_POST_SUCCESS,
    FACEBOOK_INSIGHTS_SUCCESS,
    INSTAGRAM_MEDIA_SUCCESS,
    INSTAGRAM_INSIGHTS_SUCCESS,
    INSTAGRAM_VIDEO_MEDIA_SUCCESS,
    INSTAGRAM_VIDEO_INSIGHTS_SUCCESS,
    FACEBOOK_POST_NOT_FOUND,
    FACEBOOK_MINIMAL_POST,
    INSTAGRAM_MINIMAL_MEDIA,
    FACEBOOK_HIGH_ENGAGEMENT_POST,
    INSTAGRAM_HIGH_ENGAGEMENT_MEDIA,
)


class TestMetaFetcher:
    """Test suite for MetaAnalyticsFetcher class."""

    @pytest.fixture
    def fetcher(self):
        """Create MetaAnalyticsFetcher instance for testing."""
        return MetaAnalyticsFetcher(
            access_token="test_meta_token",
            page_id="123456789",
            instagram_account_id="987654321",
            max_retries=3,
            backoff_factor=2.0,
            timeout=30,
        )

    @patch("requests.Session.request")
    def test_fetch_facebook_post_analytics_success(self, mock_request, fetcher):
        """Test successful fetching of Facebook post analytics."""
        # Mock both API calls (post data and insights)
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = FACEBOOK_POST_SUCCESS
        
        mock_insights_response = Mock()
        mock_insights_response.status_code = 200
        mock_insights_response.json.return_value = FACEBOOK_INSIGHTS_SUCCESS
        
        mock_request.side_effect = [mock_post_response, mock_insights_response]

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="123456789_987654321",  # Contains underscore = Facebook
        )

        # Verify API calls
        assert mock_request.call_count == 2
        
        # Verify parsed analytics data
        assert result["likes_count"] == 300  # reactions
        assert result["comments_count"] == 50
        assert result["shares_count"] == 20
        assert result["impressions"] == 8000
        assert result["reach"] == 6500
        assert isinstance(result["engagement_rate"], float)
        assert result["platform"] == "facebook"

    @patch("requests.Session.request")
    def test_fetch_instagram_post_analytics_success(self, mock_request, fetcher):
        """Test successful fetching of Instagram post analytics."""
        # Mock both API calls (media data and insights)
        mock_media_response = Mock()
        mock_media_response.status_code = 200
        mock_media_response.json.return_value = INSTAGRAM_MEDIA_SUCCESS
        
        mock_insights_response = Mock()
        mock_insights_response.status_code = 200
        mock_insights_response.json.return_value = INSTAGRAM_INSIGHTS_SUCCESS
        
        mock_request.side_effect = [mock_media_response, mock_insights_response]

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="17841234567890",  # Numeric only = Instagram
        )

        # Verify API calls
        assert mock_request.call_count == 2
        
        # Verify parsed analytics data
        assert result["likes_count"] == 450
        assert result["comments_count"] == 35
        assert result["impressions"] == 9500
        assert result["reach"] == 8200
        assert isinstance(result["engagement_rate"], float)
        assert result["platform"] == "instagram"

    @patch("requests.Session.request")
    def test_platform_detection_facebook(self, mock_request, fetcher):
        """Test automatic detection of Facebook posts by ID format."""
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = FACEBOOK_POST_SUCCESS
        
        mock_insights_response = Mock()
        mock_insights_response.status_code = 200
        mock_insights_response.json.return_value = FACEBOOK_INSIGHTS_SUCCESS
        
        mock_request.side_effect = [mock_post_response, mock_insights_response]

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="page123_post456",  # Contains underscore
        )

        assert result["platform"] == "facebook"

    @patch("requests.Session.request")
    def test_platform_detection_instagram(self, mock_request, fetcher):
        """Test automatic detection of Instagram posts by ID format."""
        mock_media_response = Mock()
        mock_media_response.status_code = 200
        mock_media_response.json.return_value = INSTAGRAM_MEDIA_SUCCESS
        
        mock_insights_response = Mock()
        mock_insights_response.status_code = 200
        mock_insights_response.json.return_value = INSTAGRAM_INSIGHTS_SUCCESS
        
        mock_request.side_effect = [mock_media_response, mock_insights_response]

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="17841234567890",  # Numeric only
        )

        assert result["platform"] == "instagram"

    @patch("requests.Session.request")
    def test_facebook_post_not_found(self, mock_request, fetcher):
        """Test handling of Facebook post not found error."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = FACEBOOK_POST_NOT_FOUND
        mock_request.return_value = mock_response

        with pytest.raises(PostNotFoundError):
            fetcher.fetch_post_analytics(
                post_id="internal123",
                platform_post_id="invalid_id",
            )

    @patch("requests.Session.request")
    def test_facebook_minimal_post(self, mock_request, fetcher):
        """Test handling of Facebook post with minimal data."""
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = FACEBOOK_MINIMAL_POST
        
        mock_insights_response = Mock()
        mock_insights_response.status_code = 200
        mock_insights_response.json.return_value = {"data": []}  # No insights
        
        mock_request.side_effect = [mock_post_response, mock_insights_response]

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="123_456",
        )

        # Should handle minimal data gracefully with defaults
        assert result["likes_count"] == 10
        assert result["comments_count"] == 2
        assert result["shares_count"] == 0
        assert result["impressions"] == 0  # No insights
        assert result["reach"] == 0

    @patch("requests.Session.request")
    def test_instagram_minimal_media(self, mock_request, fetcher):
        """Test handling of Instagram media with minimal data."""
        mock_media_response = Mock()
        mock_media_response.status_code = 200
        mock_media_response.json.return_value = INSTAGRAM_MINIMAL_MEDIA
        
        mock_insights_response = Mock()
        mock_insights_response.status_code = 200
        mock_insights_response.json.return_value = {"data": []}
        
        mock_request.side_effect = [mock_media_response, mock_insights_response]

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="17841234567890",
        )

        # Should handle minimal data gracefully
        assert result["likes_count"] == 15  # Fixed to match fixture
        assert result["comments_count"] == 3
        assert result["impressions"] == 0
        assert result["reach"] == 0

    @patch("requests.Session.request")
    def test_facebook_high_engagement_post(self, mock_request, fetcher):
        """Test analytics for high-engagement Facebook post."""
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = FACEBOOK_HIGH_ENGAGEMENT_POST
        
        mock_insights_response = Mock()
        mock_insights_response.status_code = 200
        mock_insights_response.json.return_value = {
            "data": [
                {"name": "post_impressions", "values": [{"value": 500000}]},
                {"name": "post_impressions_unique", "values": [{"value": 350000}]},
                {"name": "post_engaged_users", "values": [{"value": 52000}]},
            ]
        }
        
        mock_request.side_effect = [mock_post_response, mock_insights_response]

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="viral_123",
        )

        # Verify high engagement metrics
        assert result["likes_count"] == 50000
        assert result["comments_count"] == 5000
        assert result["shares_count"] == 2000
        assert result["impressions"] == 500000
        assert result["engagement_rate"] > 10.0  # Should be high

    @patch("requests.Session.request")
    def test_instagram_high_engagement_media(self, mock_request, fetcher):
        """Test analytics for high-engagement Instagram post."""
        mock_media_response = Mock()
        mock_media_response.status_code = 200
        mock_media_response.json.return_value = INSTAGRAM_HIGH_ENGAGEMENT_MEDIA
        
        mock_insights_response = Mock()
        mock_insights_response.status_code = 200
        mock_insights_response.json.return_value = {
            "data": [
                {"name": "impressions", "values": [{"value": 2000000}]},
                {"name": "reach", "values": [{"value": 1500000}]},
                {"name": "engagement", "values": [{"value": 105000}]},
            ]
        }
        
        mock_request.side_effect = [mock_media_response, mock_insights_response]

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="17841234567890",
        )

        # Verify high engagement metrics
        assert result["likes_count"] == 100000
        assert result["comments_count"] == 5000
        assert result["impressions"] == 2000000
        assert result["reach"] == 1500000

    @patch("requests.Session.request")
    def test_instagram_video_post(self, mock_request, fetcher):
        """Test handling of Instagram video post with video metrics."""
        mock_media_response = Mock()
        mock_media_response.status_code = 200
        mock_media_response.json.return_value = INSTAGRAM_VIDEO_MEDIA_SUCCESS
        
        mock_insights_response = Mock()
        mock_insights_response.status_code = 200
        mock_insights_response.json.return_value = INSTAGRAM_VIDEO_INSIGHTS_SUCCESS
        
        mock_request.side_effect = [mock_media_response, mock_insights_response]

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="17841234567890",
        )

        # Verify video metrics
        assert result["video_views"] == 15000
        # Note: media_type might not be in standardized response
        assert result["likes_count"] == 800  # Video can have likes

    @patch("requests.Session.request")
    def test_api_url_construction_facebook(self, mock_request, fetcher):
        """Test correct API URL construction for Facebook endpoints."""
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = FACEBOOK_POST_SUCCESS
        
        mock_insights_response = Mock()
        mock_insights_response.status_code = 200
        mock_insights_response.json.return_value = FACEBOOK_INSIGHTS_SUCCESS
        
        mock_request.side_effect = [mock_post_response, mock_insights_response]

        fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="123_456",
        )

        # Verify API endpoint URLs
        first_call_args = mock_request.call_args_list[0][1]
        assert "graph.facebook.com" in first_call_args["url"]
        assert "/123_456" in first_call_args["url"]

    @patch("requests.Session.request")
    def test_api_url_construction_instagram(self, mock_request, fetcher):
        """Test correct API URL construction for Instagram endpoints."""
        mock_media_response = Mock()
        mock_media_response.status_code = 200
        mock_media_response.json.return_value = INSTAGRAM_MEDIA_SUCCESS
        
        mock_insights_response = Mock()
        mock_insights_response.status_code = 200
        mock_insights_response.json.return_value = INSTAGRAM_INSIGHTS_SUCCESS
        
        mock_request.side_effect = [mock_media_response, mock_insights_response]

        fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="17841234567890",
        )

        # Verify API endpoint URLs
        first_call_args = mock_request.call_args_list[0][1]
        assert "graph.facebook.com" in first_call_args["url"]
        assert "/17841234567890" in first_call_args["url"]

    @patch("requests.Session.request")
    def test_authorization_header(self, mock_request, fetcher):
        """Test correct Authorization header is included in requests."""
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = FACEBOOK_POST_SUCCESS
        mock_request.return_value = mock_post_response

        try:
            fetcher.fetch_post_analytics(
                post_id="internal123",
                platform_post_id="123_456",
            )
        except:
            pass  # May fail on second call

        # Verify Authorization header in first call
        call_args = mock_request.call_args_list[0][1]
        assert "Authorization" in call_args["headers"]
        assert call_args["headers"]["Authorization"] == "Bearer test_meta_token"

    @patch("requests.Session.request")
    def test_custom_timeout(self, mock_request):
        """Test custom timeout configuration."""
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = FACEBOOK_POST_SUCCESS
        
        mock_insights_response = Mock()
        mock_insights_response.status_code = 200
        mock_insights_response.json.return_value = FACEBOOK_INSIGHTS_SUCCESS
        
        mock_request.side_effect = [mock_post_response, mock_insights_response]

        # Create fetcher with custom timeout
        custom_fetcher = MetaAnalyticsFetcher(
            access_token="test_token",
            page_id="123",
            timeout=60
        )
        custom_fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="123_456",
        )

        # Verify timeout parameter
        call_args = mock_request.call_args_list[0][1]
        assert call_args["timeout"] == 60

    def test_missing_platform_post_id(self, fetcher):
        """Test error when platform_post_id is missing."""
        with pytest.raises(PlatformAPIError) as exc_info:
            fetcher.fetch_post_analytics(
                post_id="internal123",
                platform_post_id=None,
            )
        
        assert "required" in str(exc_info.value).lower()

    @patch("requests.Session.request")
    def test_metadata_in_response_facebook(self, mock_request, fetcher):
        """Test that metadata fields are included in Facebook response."""
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = FACEBOOK_POST_SUCCESS
        
        mock_insights_response = Mock()
        mock_insights_response.status_code = 200
        mock_insights_response.json.return_value = FACEBOOK_INSIGHTS_SUCCESS
        
        mock_request.side_effect = [mock_post_response, mock_insights_response]

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="123_456",
        )

        # Verify metadata fields
        assert "platform" in result
        assert result["platform"] == "facebook"
        assert "platform_post_id" in result
        assert result["platform_post_id"] == "123_456"
        assert "fetched_at" in result
        assert isinstance(result["fetched_at"], datetime)

    @patch("requests.Session.request")
    def test_metadata_in_response_instagram(self, mock_request, fetcher):
        """Test that metadata fields are included in Instagram response."""
        mock_media_response = Mock()
        mock_media_response.status_code = 200
        mock_media_response.json.return_value = INSTAGRAM_MEDIA_SUCCESS
        
        mock_insights_response = Mock()
        mock_insights_response.status_code = 200
        mock_insights_response.json.return_value = INSTAGRAM_INSIGHTS_SUCCESS
        
        mock_request.side_effect = [mock_media_response, mock_insights_response]

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="17841234567890",
        )

        # Verify metadata fields
        assert "platform" in result
        assert result["platform"] == "instagram"
        assert "platform_post_id" in result
        assert result["platform_post_id"] == "17841234567890"
        assert "fetched_at" in result
        assert isinstance(result["fetched_at"], datetime)
