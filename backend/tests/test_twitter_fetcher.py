"""
Unit tests for Twitter/X platform fetcher.

Tests Twitter-specific API interactions, response parsing,
and analytics data extraction with comprehensive mocking.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from app.services.platform_fetchers.twitter_fetcher import TwitterAnalyticsFetcher
from app.services.platform_fetchers.exceptions import (
    PlatformAPIError,
    PostNotFoundError,
)
from tests.fixtures.twitter_responses import (
    TWITTER_TWEET_SUCCESS,
    TWITTER_MULTIPLE_TWEETS_SUCCESS,
    TWITTER_USER_METRICS_SUCCESS,
    TWITTER_TWEET_NOT_FOUND,
    TWITTER_MINIMAL_RESPONSE,
    TWITTER_HIGH_ENGAGEMENT_RESPONSE,
    TWITTER_VIDEO_TWEET_SUCCESS,
)


class TestTwitterFetcher:
    """Test suite for TwitterAnalyticsFetcher class."""

    @pytest.fixture
    def fetcher(self):
        """Create TwitterAnalyticsFetcher instance for testing."""
        return TwitterAnalyticsFetcher(
            access_token="test_twitter_token",
            max_retries=3,
            backoff_factor=2.0,
            timeout=30,
        )

    @patch("requests.Session.request")
    def test_fetch_post_analytics_success(self, mock_request, fetcher):
        """Test successful fetching of post analytics from Twitter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = TWITTER_TWEET_SUCCESS
        mock_request.return_value = mock_response

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="1234567890",
        )

        # Verify API call
        assert mock_request.call_count == 1
        call_args = mock_request.call_args[1]
        assert "/tweets/1234567890" in call_args["url"]
        assert call_args["headers"]["Authorization"] == "Bearer test_twitter_token"

        # Verify parsed analytics data
        assert result["likes_count"] == 200
        assert result["retweets_count"] == 45
        assert result["comments_count"] == 30  # reply_count
        assert result["quote_tweets_count"] == 8  # Fixed to match fixture
        assert result["impressions"] == 12000
        assert result["clicks"] == 175  # url_clicks (150) + profile_clicks (25)
        assert isinstance(result["engagement_rate"], float)
        assert result["engagement_rate"] > 0
        assert result["platform"] == "twitter"

    @patch("requests.Session.request")
    def test_parse_twitter_analytics(self, mock_request, fetcher):
        """Test parsing Twitter analytics response into standardized format."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = TWITTER_TWEET_SUCCESS
        mock_request.return_value = mock_response

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="1234567890",
        )

        # Verify all required fields are present and correct type
        assert isinstance(result["likes_count"], int)
        assert isinstance(result["retweets_count"], int)
        assert isinstance(result["comments_count"], int)
        assert isinstance(result["quote_tweets_count"], int)
        assert isinstance(result["impressions"], int)
        assert isinstance(result["engagement_rate"], float)
        assert isinstance(result["clicks"], int)

        # Verify engagement rate calculation
        # (200 likes + 30 replies + (45 retweets + 8 quotes)) / 12000 * 100
        total_engagement = 200 + 30 + 45 + 8
        expected_rate = (total_engagement / 12000) * 100
        assert result["engagement_rate"] == pytest.approx(expected_rate, abs=0.01)

    @patch("requests.Session.request")
    def test_public_and_non_public_metrics(self, mock_request, fetcher):
        """Test handling of both public and non-public metrics."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = TWITTER_TWEET_SUCCESS
        mock_request.return_value = mock_response

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="1234567890",
        )

        # Public metrics (always available)
        assert result["likes_count"] == 200
        assert result["retweets_count"] == 45
        assert result["comments_count"] == 30
        assert result["quote_tweets_count"] == 8  # Fixed to match fixture

        # Non-public metrics (requires ownership)
        assert result["impressions"] == 12000
        assert result["url_clicks"] == 150
        assert result["profile_clicks"] == 25

    @patch("requests.Session.request")
    def test_post_not_found_error(self, mock_request, fetcher):
        """Test handling of post not found error."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = TWITTER_TWEET_NOT_FOUND
        mock_request.return_value = mock_response

        with pytest.raises(PostNotFoundError) as exc_info:
            fetcher.fetch_post_analytics(
                post_id="internal123",
                platform_post_id="invalid_id",
            )

        assert "not found" in str(exc_info.value).lower()

    @patch("requests.Session.request")
    def test_minimal_response_handling(self, mock_request, fetcher):
        """Test handling of minimal response with only public metrics."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = TWITTER_MINIMAL_RESPONSE
        mock_request.return_value = mock_response

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="1234567890",
        )

        # Should handle minimal data gracefully
        assert result["likes_count"] == 5  # Fixed to match fixture
        assert result["retweets_count"] == 2
        assert result["comments_count"] == 1
        assert result["quote_tweets_count"] == 0
        # Non-public metrics should be 0 when not available
        assert result["impressions"] == 0
        assert result["url_clicks"] == 0
        assert result["profile_clicks"] == 0

    @patch("requests.Session.request")
    def test_high_engagement_tweet(self, mock_request, fetcher):
        """Test analytics for high-engagement viral tweet."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = TWITTER_HIGH_ENGAGEMENT_RESPONSE
        mock_request.return_value = mock_response

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="viral123",
        )

        # Verify high engagement metrics
        assert result["likes_count"] == 50000
        assert result["retweets_count"] == 10000  # Fixed to match fixture
        assert result["comments_count"] == 2000  # reply_count
        assert result["quote_tweets_count"] == 500
        assert result["impressions"] == 5000000

        # Verify high engagement rate
        total_engagement = 50000 + 2000 + 10000 + 500
        expected_rate = (total_engagement / 5000000) * 100
        assert result["engagement_rate"] == pytest.approx(expected_rate, abs=0.01)
        assert result["engagement_rate"] > 1.0  # Should be high

    @patch("requests.Session.request")
    def test_video_tweet_metrics(self, mock_request, fetcher):
        """Test handling of video tweet with view counts."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = TWITTER_VIDEO_TWEET_SUCCESS
        mock_request.return_value = mock_response

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="video123",
        )

        # Verify standard metrics
        assert result["likes_count"] == 500  # Fixed to match fixture
        assert result["retweets_count"] == 100
        # Note: Video views are not in standard response, would need media lookup
        assert result["video_views"] == 0  # Not available in basic tweet lookup

    @patch("requests.Session.request")
    def test_api_url_construction(self, mock_request, fetcher):
        """Test correct API URL construction for Twitter endpoints."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = TWITTER_TWEET_SUCCESS
        mock_request.return_value = mock_response

        fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="1234567890",
        )

        # Verify API endpoint URL
        call_args = mock_request.call_args[1]
        assert "api.twitter.com" in call_args["url"]
        assert "/2/tweets/1234567890" in call_args["url"]
        assert "tweet.fields" in call_args["params"]

    @patch("requests.Session.request")
    def test_authorization_header(self, mock_request, fetcher):
        """Test correct Authorization header is included in requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = TWITTER_TWEET_SUCCESS
        mock_request.return_value = mock_response

        fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="1234567890",
        )

        # Verify Authorization header
        call_args = mock_request.call_args[1]
        assert "Authorization" in call_args["headers"]
        assert call_args["headers"]["Authorization"] == "Bearer test_twitter_token"

    @patch("requests.Session.request")
    def test_custom_timeout(self, mock_request):
        """Test custom timeout configuration."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = TWITTER_TWEET_SUCCESS
        mock_request.return_value = mock_response

        # Create fetcher with custom timeout
        custom_fetcher = TwitterAnalyticsFetcher(
            access_token="test_token",
            timeout=60
        )
        custom_fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="1234567890",
        )

        # Verify timeout parameter
        call_args = mock_request.call_args[1]
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
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = TWITTER_TWEET_SUCCESS
        mock_request.return_value = mock_response

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="1234567890",
        )

        # Verify metadata fields
        assert "platform" in result
        assert result["platform"] == "twitter"
        assert "platform_post_id" in result
        assert result["platform_post_id"] == "1234567890"
        assert "platform_post_url" in result
        assert "twitter.com/i/web/status/1234567890" in result["platform_post_url"]
        assert "fetched_at" in result
        assert isinstance(result["fetched_at"], datetime)

    @patch("requests.Session.request")
    def test_multiple_tweets_fetch(self, mock_request, fetcher):
        """Test fetching multiple tweets in a single request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = TWITTER_MULTIPLE_TWEETS_SUCCESS
        mock_request.return_value = mock_response

        result = fetcher.fetch_multiple_tweets(
            tweet_ids=["1234567890", "0987654321"]
        )

        # Verify API call
        call_args = mock_request.call_args[1]
        assert "/2/tweets" in call_args["url"]
        assert "ids" in call_args["params"]
        assert "1234567890,0987654321" in call_args["params"]["ids"]

        # Verify result structure
        assert isinstance(result, dict)
        assert len(result) == 2

    @patch("requests.Session.request")
    def test_click_through_rate_calculation(self, mock_request, fetcher):
        """Test CTR calculation from Twitter metrics."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = TWITTER_TWEET_SUCCESS
        mock_request.return_value = mock_response

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="1234567890",
        )

        # CTR = (url_clicks + profile_clicks) / impressions * 100
        # (150 + 25) / 12000 * 100 = 1.46%
        expected_ctr = ((150 + 25) / 12000) * 100
        assert result["click_through_rate"] == pytest.approx(expected_ctr, abs=0.01)

    @patch("requests.Session.request")
    def test_bookmarks_count(self, mock_request, fetcher):
        """Test Twitter-specific bookmarks metric."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = TWITTER_TWEET_SUCCESS
        mock_request.return_value = mock_response

        result = fetcher.fetch_post_analytics(
            post_id="internal123",
            platform_post_id="1234567890",
        )

        # Twitter provides bookmark count in public metrics
        assert "bookmarks_count" in result
        assert result["bookmarks_count"] == 15  # Fixed to match fixture
