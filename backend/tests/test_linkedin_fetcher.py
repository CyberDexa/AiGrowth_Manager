"""
Unit tests for LinkedIn platform fetcher.

Tests LinkedIn-specific API interactions, response parsing,
and analytics data extraction with comprehensive mocking.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from app.services.platform_fetchers.linkedin_fetcher import LinkedInAnalyticsFetcher
from app.services.platform_fetchers.exceptions import (
    PlatformAPIError,
    RateLimitError,
    AuthenticationError,
    PostNotFoundError,
)
from tests.fixtures.linkedin_responses import (
    LINKEDIN_SHARE_STATISTICS_SUCCESS,
    LINKEDIN_POST_DETAILS_SUCCESS,
    LINKEDIN_SHARE_NOT_FOUND,
    LINKEDIN_UNAUTHORIZED,
    LINKEDIN_RATE_LIMIT_EXCEEDED,
    LINKEDIN_EMPTY_RESPONSE,
    LINKEDIN_MINIMAL_RESPONSE,
    LINKEDIN_HIGH_ENGAGEMENT_RESPONSE,
)


class TestLinkedInFetcher:
    """Test suite for LinkedInAnalyticsFetcher class."""

    @pytest.fixture
    def fetcher(self):
        """Create LinkedInAnalyticsFetcher instance for testing."""
        return LinkedInAnalyticsFetcher(
            access_token="test_linkedin_token",
            organization_id="urn:li:organization:123456",
            max_retries=3,
            backoff_factor=2.0,
            timeout=30,
        )

    @patch("requests.Session.request")
    def test_fetch_post_analytics_success(self, mock_request, fetcher):
        """Test successful fetching of post analytics from LinkedIn."""
        # Mock both API calls (share statistics and post details)
        mock_share_response = Mock()
        mock_share_response.status_code = 200
        mock_share_response.json.return_value = LINKEDIN_SHARE_STATISTICS_SUCCESS
        
        mock_details_response = Mock()
        mock_details_response.status_code = 200
        mock_details_response.json.return_value = LINKEDIN_POST_DETAILS_SUCCESS
        
        mock_request.side_effect = [mock_share_response, mock_details_response]

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="urn:li:share:123456789",
        )

        # Verify API was called twice (share stats + post details)
        assert mock_request.call_count == 2
        
        # Verify first call is for share statistics
        first_call_args = mock_request.call_args_list[0][1]
        assert "organizationalEntityShareStatistics" in first_call_args["url"]
        
        # Verify parsed analytics data
        assert result["likes_count"] == 150
        assert result["comments_count"] == 25
        assert result["shares_count"] == 12
        assert result["impressions"] == 5500
        assert result["clicks"] == 80
        assert isinstance(result["engagement_rate"], float)
        assert result["engagement_rate"] > 0
        assert result["platform"] == "linkedin"

    @patch("requests.Session.request")
    def test_parse_linkedin_analytics(self, mock_request, fetcher):
        """Test parsing LinkedIn analytics response into standardized format."""
        mock_share_response = Mock()
        mock_share_response.status_code = 200
        mock_share_response.json.return_value = LINKEDIN_SHARE_STATISTICS_SUCCESS
        
        mock_details_response = Mock()
        mock_details_response.status_code = 200
        mock_details_response.json.return_value = LINKEDIN_POST_DETAILS_SUCCESS
        
        mock_request.side_effect = [mock_share_response, mock_details_response]

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="urn:li:share:123456789",
        )

        # Verify all required fields are present and correct type
        assert isinstance(result["likes_count"], int)
        assert isinstance(result["comments_count"], int)
        assert isinstance(result["shares_count"], int)
        assert isinstance(result["impressions"], int)
        assert isinstance(result["engagement_rate"], float)
        assert isinstance(result["clicks"], int)

        # Verify engagement rate calculation
        # (150 + 25 + 12) / 5500 * 100 = 3.4%
        expected_rate = (150 + 25 + 12) / 5500 * 100
        assert result["engagement_rate"] == pytest.approx(expected_rate, abs=0.01)

    @patch("requests.Session.request")
    def test_post_not_found_error(self, mock_request, fetcher):
        """Test handling of empty response (post not found)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = LINKEDIN_EMPTY_RESPONSE
        mock_request.return_value = mock_response

        with pytest.raises(PostNotFoundError) as exc_info:
            fetcher.fetch_post_analytics(
                post_id="internal123",
                platform_post_id="urn:li:share:invalid",
            )

        assert "not found" in str(exc_info.value).lower()

    @patch("requests.Session.request")
    def test_minimal_response_handling(self, mock_request, fetcher):
        """Test handling of minimal response with only required fields."""
        mock_share_response = Mock()
        mock_share_response.status_code = 200
        mock_share_response.json.return_value = LINKEDIN_MINIMAL_RESPONSE
        
        mock_details_response = Mock()
        mock_details_response.status_code = 200
        mock_details_response.json.return_value = {}
        
        mock_request.side_effect = [mock_share_response, mock_details_response]

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="urn:li:share:123456789",
        )

        # Should handle minimal data gracefully
        assert result["likes_count"] == 10
        assert result["comments_count"] == 2
        assert result["shares_count"] == 1
        assert result["impressions"] == 500  # Fixed to match fixture

    @patch("requests.Session.request")
    def test_high_engagement_post(self, mock_request, fetcher):
        """Test analytics for high-engagement viral post."""
        mock_share_response = Mock()
        mock_share_response.status_code = 200
        mock_share_response.json.return_value = LINKEDIN_HIGH_ENGAGEMENT_RESPONSE
        
        mock_details_response = Mock()
        mock_details_response.status_code = 200
        mock_details_response.json.return_value = {}
        
        mock_request.side_effect = [mock_share_response, mock_details_response]

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="urn:li:share:viral123",
        )

        # Verify high engagement metrics
        assert result["likes_count"] == 5000
        assert result["comments_count"] == 800
        assert result["shares_count"] == 300  # Fixed to match fixture
        assert result["impressions"] == 250000
        assert result["clicks"] == 15000

        # Verify high engagement rate
        total_engagements = 5000 + 800 + 300
        expected_rate = (total_engagements / 250000) * 100
        assert result["engagement_rate"] == pytest.approx(expected_rate, abs=0.01)
        assert result["engagement_rate"] > 2.0  # Should be high

    @patch("requests.Session.request")
    def test_api_url_construction(self, mock_request, fetcher):
        """Test correct API URL construction for LinkedIn endpoints."""
        mock_share_response = Mock()
        mock_share_response.status_code = 200
        mock_share_response.json.return_value = LINKEDIN_SHARE_STATISTICS_SUCCESS
        
        mock_details_response = Mock()
        mock_details_response.status_code = 200
        mock_details_response.json.return_value = LINKEDIN_POST_DETAILS_SUCCESS
        
        mock_request.side_effect = [mock_share_response, mock_details_response]

        fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="urn:li:share:123456789",
        )

        # Verify API endpoint URLs
        first_call_args = mock_request.call_args_list[0][1]
        assert "api.linkedin.com" in first_call_args["url"]
        assert "organizationalEntityShareStatistics" in first_call_args["url"]
        
        second_call_args = mock_request.call_args_list[1][1]
        assert "api.linkedin.com" in second_call_args["url"]
        assert "/ugcPosts/" in second_call_args["url"]

    @patch("requests.Session.request")
    def test_authorization_header(self, mock_request, fetcher):
        """Test correct Authorization header is included in requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = LINKEDIN_SHARE_STATISTICS_SUCCESS
        mock_request.return_value = mock_response

        try:
            fetcher.fetch_post_analytics(
                post_id="internal123",
                platform_post_id="urn:li:share:123456789",
            )
        except:
            pass  # May fail on second call, but we only care about first

        # Verify Authorization header in first call
        call_args = mock_request.call_args_list[0][1]
        assert "Authorization" in call_args["headers"]
        assert call_args["headers"]["Authorization"] == "Bearer test_linkedin_token"

    @patch("requests.Session.request")
    def test_custom_timeout(self, mock_request):
        """Test custom timeout configuration."""
        mock_share_response = Mock()
        mock_share_response.status_code = 200
        mock_share_response.json.return_value = LINKEDIN_SHARE_STATISTICS_SUCCESS
        
        mock_details_response = Mock()
        mock_details_response.status_code = 200
        mock_details_response.json.return_value = {}
        
        mock_request.side_effect = [mock_share_response, mock_details_response]

        # Create fetcher with custom timeout
        custom_fetcher = LinkedInAnalyticsFetcher(
            access_token="test_token",
            organization_id="urn:li:organization:123",
            timeout=60
        )
        custom_fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="urn:li:share:123456789",
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
    def test_metadata_in_response(self, mock_request, fetcher):
        """Test that metadata fields are included in response."""
        mock_share_response = Mock()
        mock_share_response.status_code = 200
        mock_share_response.json.return_value = LINKEDIN_SHARE_STATISTICS_SUCCESS
        
        mock_details_response = Mock()
        mock_details_response.status_code = 200
        mock_details_response.json.return_value = {}
        
        mock_request.side_effect = [mock_share_response, mock_details_response]

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="urn:li:share:123456789",
        )

        # Verify metadata fields
        assert "platform" in result
        assert result["platform"] == "linkedin"
        assert "platform_post_id" in result
        assert result["platform_post_id"] == "urn:li:share:123456789"
        assert "fetched_at" in result
        assert isinstance(result["fetched_at"], datetime)

