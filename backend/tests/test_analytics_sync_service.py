"""Integration tests for AnalyticsSyncService."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.platform_fetchers.analytics_sync_service import AnalyticsSyncService
from app.services.platform_fetchers.exceptions import (
    PlatformAPIError,
    RateLimitError,
    AuthenticationError,
    PostNotFoundError
)
from app.models.published_post import PublishedPost
from app.models.post_analytics import PostAnalytics
from app.models.social_account import SocialAccount

# Import mock responses
from tests.fixtures.linkedin_responses import LINKEDIN_SHARE_STATISTICS_SUCCESS
from tests.fixtures.twitter_responses import TWITTER_TWEET_SUCCESS
from tests.fixtures.meta_responses import (
    FACEBOOK_POST_SUCCESS,
    FACEBOOK_INSIGHTS_SUCCESS,
    INSTAGRAM_MEDIA_SUCCESS,
    INSTAGRAM_INSIGHTS_SUCCESS
)


@pytest.mark.integration
class TestAnalyticsSyncService:
    """Integration tests for AnalyticsSyncService."""
    
    def test_initialization(self, test_db: Session):
        """Test service initialization."""
        service = AnalyticsSyncService(test_db)
        
        assert service.db == test_db
        assert isinstance(service.fetchers, dict)
        assert len(service.fetchers) == 0
    
    @patch('app.services.platform_fetchers.analytics_sync_service.LinkedInAnalyticsFetcher')
    def test_initialize_fetchers_linkedin(
        self,
        mock_linkedin_class,
        test_db: Session,
        test_business,
        test_social_account_linkedin
    ):
        """Test initializing LinkedIn fetcher."""
        service = AnalyticsSyncService(test_db)
        service._initialize_fetchers(test_business.id)
        
        # Verify LinkedIn fetcher was created
        mock_linkedin_class.assert_called_once_with(
            access_token=test_social_account_linkedin.access_token,
            organization_id=test_social_account_linkedin.page_id
        )
        assert "linkedin" in service.fetchers
    
    @patch('app.services.platform_fetchers.analytics_sync_service.TwitterAnalyticsFetcher')
    def test_initialize_fetchers_twitter(
        self,
        mock_twitter_class,
        test_db: Session,
        test_business,
        test_social_account_twitter
    ):
        """Test initializing Twitter fetcher."""
        service = AnalyticsSyncService(test_db)
        service._initialize_fetchers(test_business.id)
        
        # Verify Twitter fetcher was created
        mock_twitter_class.assert_called_once_with(
            access_token=test_social_account_twitter.access_token
        )
        assert "twitter" in service.fetchers
    
    @patch('app.services.platform_fetchers.analytics_sync_service.MetaAnalyticsFetcher')
    def test_initialize_fetchers_facebook(
        self,
        mock_meta_class,
        test_db: Session,
        test_business,
        test_social_account_facebook
    ):
        """Test initializing Meta fetcher for Facebook."""
        service = AnalyticsSyncService(test_db)
        service._initialize_fetchers(test_business.id)
        
        # Verify Meta fetcher was created
        mock_meta_class.assert_called_once_with(
            access_token=test_social_account_facebook.access_token,
            page_id=test_social_account_facebook.page_id,
            instagram_account_id=test_social_account_facebook.instagram_account_id
        )
        assert "facebook" in service.fetchers
    
    @patch('app.services.platform_fetchers.analytics_sync_service.MetaAnalyticsFetcher')
    def test_initialize_fetchers_instagram(
        self,
        mock_meta_class,
        test_db: Session,
        test_business,
        test_social_account_facebook
    ):
        """Test initializing Meta fetcher for Instagram (uses same account)."""
        # Add Instagram account
        instagram_account = SocialAccount(
            business_id=test_business.id,
            platform="instagram",
            account_name="test_instagram",
            access_token="instagram_token_123",
            refresh_token="instagram_refresh_123",
            page_id="instagram_page_456",
            instagram_account_id="instagram_account_789",
            is_active=True
        )
        test_db.add(instagram_account)
        test_db.commit()
        
        service = AnalyticsSyncService(test_db)
        service._initialize_fetchers(test_business.id)
        
        # Verify Meta fetcher was created for Instagram
        assert mock_meta_class.call_count >= 1
        assert "instagram" in service.fetchers
    
    @patch('app.services.platform_fetchers.analytics_sync_service.LinkedInAnalyticsFetcher')
    def test_sync_single_post_linkedin_success(
        self,
        mock_linkedin_class,
        test_db: Session,
        test_business,
        test_social_account_linkedin,
        test_published_posts
    ):
        """Test syncing a single LinkedIn post successfully."""
        # Get LinkedIn post
        linkedin_post = next(p for p in test_published_posts if p.platform == "linkedin")
        
        # Mock fetcher
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_post_analytics.return_value = {
            "platform": "linkedin",
            "platform_post_id": linkedin_post.platform_post_id,
            "likes_count": 150,
            "comments_count": 25,
            "shares_count": 12,
            "impressions": 5500,
            "reach": 4800,
            "engagement_rate": 3.4,
            "fetched_at": datetime.utcnow()
        }
        mock_linkedin_class.return_value = mock_fetcher
        
        # Sync post
        service = AnalyticsSyncService(test_db)
        result = service.sync_single_post(linkedin_post.id)
        
        # Verify result
        assert result["success"] is True
        assert result["post_id"] == linkedin_post.id
        assert result["platform"] == "linkedin"
        assert result["analytics"]["likes_count"] == 150
        assert result["analytics"]["comments_count"] == 25
        assert result["analytics"]["shares_count"] == 12
        assert "analytics_id" in result
        
        # Verify database record was created
        analytics = test_db.query(PostAnalytics).filter(
            PostAnalytics.published_post_id == linkedin_post.id
        ).first()
        assert analytics is not None
        assert analytics.likes_count == 150
        assert analytics.comments_count == 25
        assert analytics.shares_count == 12
        assert analytics.impressions == 5500
        
        # Verify post was updated
        test_db.refresh(linkedin_post)
        assert linkedin_post.likes_count == 150
        assert linkedin_post.comments_count == 25
        assert linkedin_post.shares_count == 12
        assert linkedin_post.last_metrics_sync is not None
    
    @patch('app.services.platform_fetchers.analytics_sync_service.TwitterAnalyticsFetcher')
    def test_sync_single_post_twitter_success(
        self,
        mock_twitter_class,
        test_db: Session,
        test_business,
        test_social_account_twitter,
        test_published_posts
    ):
        """Test syncing a single Twitter post successfully."""
        # Get Twitter post
        twitter_post = next(p for p in test_published_posts if p.platform == "twitter")
        
        # Mock fetcher
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_post_analytics.return_value = {
            "platform": "twitter",
            "platform_post_id": twitter_post.platform_post_id,
            "likes_count": 200,
            "comments_count": 30,
            "retweets_count": 45,
            "quote_tweets_count": 8,
            "impressions": 12000,
            "clicks": 175,
            "engagement_rate": 2.36,
            "click_through_rate": 1.46,
            "fetched_at": datetime.utcnow()
        }
        mock_twitter_class.return_value = mock_fetcher
        
        # Sync post
        service = AnalyticsSyncService(test_db)
        result = service.sync_single_post(twitter_post.id)
        
        # Verify result
        assert result["success"] is True
        assert result["post_id"] == twitter_post.id
        assert result["platform"] == "twitter"
        assert result["analytics"]["likes_count"] == 200
        assert result["analytics"]["retweets_count"] == 45
        assert result["analytics"]["quote_tweets_count"] == 8
        
        # Verify database record
        analytics = test_db.query(PostAnalytics).filter(
            PostAnalytics.published_post_id == twitter_post.id
        ).first()
        assert analytics is not None
        assert analytics.likes_count == 200
        assert analytics.retweets_count == 45
        assert analytics.impressions == 12000
    
    @patch('app.services.platform_fetchers.analytics_sync_service.MetaAnalyticsFetcher')
    def test_sync_single_post_facebook_success(
        self,
        mock_meta_class,
        test_db: Session,
        test_business,
        test_social_account_facebook,
        test_published_posts
    ):
        """Test syncing a single Facebook post successfully."""
        # Get Facebook post
        facebook_post = next(p for p in test_published_posts if p.platform == "facebook")
        
        # Mock fetcher
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_post_analytics.return_value = {
            "platform": "facebook",
            "platform_post_id": facebook_post.platform_post_id,
            "reactions_count": 300,
            "comments_count": 50,
            "shares_count": 20,
            "impressions": 8000,
            "reach": 6500,
            "clicks": 120,
            "engagement_rate": 4.63,
            "fetched_at": datetime.utcnow()
        }
        mock_meta_class.return_value = mock_fetcher
        
        # Sync post
        service = AnalyticsSyncService(test_db)
        result = service.sync_single_post(facebook_post.id)
        
        # Verify result
        assert result["success"] is True
        assert result["post_id"] == facebook_post.id
        assert result["platform"] == "facebook"
        assert result["analytics"]["reactions_count"] == 300
        assert result["analytics"]["comments_count"] == 50
        assert result["analytics"]["shares_count"] == 20
        
        # Verify database record
        analytics = test_db.query(PostAnalytics).filter(
            PostAnalytics.published_post_id == facebook_post.id
        ).first()
        assert analytics is not None
        assert analytics.reactions_count == 300
        assert analytics.impressions == 8000
    
    @patch('app.services.platform_fetchers.analytics_sync_service.MetaAnalyticsFetcher')
    def test_sync_single_post_instagram_success(
        self,
        mock_meta_class,
        test_db: Session,
        test_business,
        test_published_posts
    ):
        """Test syncing a single Instagram post successfully."""
        # Add Instagram social account
        instagram_account = SocialAccount(
            business_id=test_business.id,
            platform="instagram",
            account_name="test_instagram",
            access_token="instagram_token_123",
            page_id="instagram_page_456",
            instagram_account_id="instagram_account_789",
            is_active=True
        )
        test_db.add(instagram_account)
        
        # Add Instagram post
        instagram_post = PublishedPost(
            business_id=test_business.id,
            platform="instagram",
            platform_post_id="987654321",
            content="Test Instagram post",
            status="published",
            scheduled_time=datetime.utcnow(),
            published_at=datetime.utcnow()
        )
        test_db.add(instagram_post)
        test_db.commit()
        
        # Mock fetcher
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_post_analytics.return_value = {
            "platform": "instagram",
            "platform_post_id": instagram_post.platform_post_id,
            "likes_count": 450,
            "comments_count": 35,
            "impressions": 9500,
            "reach": 8200,
            "engagement_rate": 5.11,
            "fetched_at": datetime.utcnow()
        }
        mock_meta_class.return_value = mock_fetcher
        
        # Sync post
        service = AnalyticsSyncService(test_db)
        result = service.sync_single_post(instagram_post.id)
        
        # Verify result
        assert result["success"] is True
        assert result["post_id"] == instagram_post.id
        assert result["platform"] == "instagram"
        assert result["analytics"]["likes_count"] == 450
        assert result["analytics"]["comments_count"] == 35
        
        # Verify database record
        analytics = test_db.query(PostAnalytics).filter(
            PostAnalytics.published_post_id == instagram_post.id
        ).first()
        assert analytics is not None
        assert analytics.likes_count == 450
        assert analytics.impressions == 9500
    
    def test_sync_single_post_not_found(self, test_db: Session):
        """Test syncing a non-existent post raises error."""
        service = AnalyticsSyncService(test_db)
        
        with pytest.raises(ValueError, match="Post 99999 not found"):
            service.sync_single_post(99999)
    
    @patch('app.services.platform_fetchers.analytics_sync_service.LinkedInAnalyticsFetcher')
    def test_sync_single_post_not_published(
        self,
        mock_linkedin_class,
        test_db: Session,
        test_business,
        test_social_account_linkedin
    ):
        """Test syncing a draft post raises error."""
        # Create draft post
        draft_post = PublishedPost(
            business_id=test_business.id,
            platform="linkedin",
            platform_post_id="draft_123",
            content="Draft post",
            status="draft",
            scheduled_time=datetime.utcnow()
        )
        test_db.add(draft_post)
        test_db.commit()
        
        service = AnalyticsSyncService(test_db)
        
        with pytest.raises(ValueError, match="is not published"):
            service.sync_single_post(draft_post.id)
    
    @patch('app.services.platform_fetchers.analytics_sync_service.LinkedInAnalyticsFetcher')
    def test_sync_single_post_with_error(
        self,
        mock_linkedin_class,
        test_db: Session,
        test_business,
        test_social_account_linkedin,
        test_published_posts
    ):
        """Test syncing a post that encounters an error."""
        linkedin_post = next(p for p in test_published_posts if p.platform == "linkedin")
        
        # Mock fetcher to raise error
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_post_analytics.side_effect = PlatformAPIError(
            "API request failed",
            platform="linkedin"
        )
        mock_linkedin_class.return_value = mock_fetcher
        
        # Sync post
        service = AnalyticsSyncService(test_db)
        result = service.sync_single_post(linkedin_post.id)
        
        # Verify error result
        assert result["success"] is False
        assert result["post_id"] == linkedin_post.id
        assert result["platform"] == "linkedin"
        assert "error" in result
        assert "API request failed" in result["error"]
    
    @patch('app.services.platform_fetchers.analytics_sync_service.LinkedInAnalyticsFetcher')
    @patch('app.services.platform_fetchers.analytics_sync_service.TwitterAnalyticsFetcher')
    @patch('app.services.platform_fetchers.analytics_sync_service.MetaAnalyticsFetcher')
    def test_sync_business_analytics_all_platforms(
        self,
        mock_meta_class,
        mock_twitter_class,
        mock_linkedin_class,
        test_db: Session,
        test_business,
        test_social_account_linkedin,
        test_social_account_twitter,
        test_social_account_facebook,
        test_published_posts
    ):
        """Test syncing analytics for all platforms."""
        # Mock fetchers
        mock_linkedin_fetcher = MagicMock()
        mock_linkedin_fetcher.fetch_post_analytics.return_value = {
            "platform": "linkedin",
            "likes_count": 100,
            "comments_count": 10,
            "shares_count": 5,
            "impressions": 1000,
            "engagement_rate": 11.5,
            "fetched_at": datetime.utcnow()
        }
        mock_linkedin_class.return_value = mock_linkedin_fetcher
        
        mock_twitter_fetcher = MagicMock()
        mock_twitter_fetcher.fetch_post_analytics.return_value = {
            "platform": "twitter",
            "likes_count": 200,
            "comments_count": 20,
            "retweets_count": 30,
            "impressions": 5000,
            "engagement_rate": 5.0,
            "fetched_at": datetime.utcnow()
        }
        mock_twitter_class.return_value = mock_twitter_fetcher
        
        mock_meta_fetcher = MagicMock()
        mock_meta_fetcher.fetch_post_analytics.return_value = {
            "platform": "facebook",
            "reactions_count": 150,
            "comments_count": 15,
            "shares_count": 10,
            "impressions": 3000,
            "engagement_rate": 5.83,
            "fetched_at": datetime.utcnow()
        }
        mock_meta_class.return_value = mock_meta_fetcher
        
        # Sync all posts
        service = AnalyticsSyncService(test_db)
        result = service.sync_business_analytics(test_business.id)
        
        # Verify results
        assert result["total_posts"] == 5  # From fixture
        assert result["synced"] == 5
        assert result["failed"] == 0
        assert result["rate_limited"] == 0
        assert len(result["errors"]) == 0
        
        # Verify by platform
        assert "linkedin" in result["by_platform"]
        assert result["by_platform"]["linkedin"]["synced"] >= 1
        assert "twitter" in result["by_platform"]
        assert result["by_platform"]["twitter"]["synced"] >= 1
        assert "facebook" in result["by_platform"]
        assert result["by_platform"]["facebook"]["synced"] >= 1
        
        # Verify database records
        analytics_count = test_db.query(PostAnalytics).filter(
            PostAnalytics.business_id == test_business.id
        ).count()
        assert analytics_count == 5
    
    @patch('app.services.platform_fetchers.analytics_sync_service.LinkedInAnalyticsFetcher')
    def test_sync_business_analytics_single_platform(
        self,
        mock_linkedin_class,
        test_db: Session,
        test_business,
        test_social_account_linkedin,
        test_published_posts
    ):
        """Test syncing analytics for a single platform."""
        # Mock LinkedIn fetcher
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_post_analytics.return_value = {
            "platform": "linkedin",
            "likes_count": 100,
            "comments_count": 10,
            "shares_count": 5,
            "impressions": 1000,
            "engagement_rate": 11.5,
            "fetched_at": datetime.utcnow()
        }
        mock_linkedin_class.return_value = mock_fetcher
        
        # Sync only LinkedIn posts
        service = AnalyticsSyncService(test_db)
        result = service.sync_business_analytics(
            test_business.id,
            platforms=["linkedin"]
        )
        
        # Verify only LinkedIn posts were synced
        linkedin_posts = [p for p in test_published_posts if p.platform == "linkedin"]
        assert result["total_posts"] == len(linkedin_posts)
        assert result["synced"] == len(linkedin_posts)
        assert "linkedin" in result["by_platform"]
        assert "twitter" not in result["by_platform"]
        assert "facebook" not in result["by_platform"]
    
    @patch('app.services.platform_fetchers.analytics_sync_service.LinkedInAnalyticsFetcher')
    def test_sync_business_analytics_with_limit(
        self,
        mock_linkedin_class,
        test_db: Session,
        test_business,
        test_social_account_linkedin,
        test_published_posts
    ):
        """Test syncing analytics with a limit."""
        # Mock LinkedIn fetcher
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_post_analytics.return_value = {
            "platform": "linkedin",
            "likes_count": 100,
            "comments_count": 10,
            "shares_count": 5,
            "impressions": 1000,
            "engagement_rate": 11.5,
            "fetched_at": datetime.utcnow()
        }
        mock_linkedin_class.return_value = mock_fetcher
        
        # Sync with limit
        service = AnalyticsSyncService(test_db)
        result = service.sync_business_analytics(
            test_business.id,
            limit=2
        )
        
        # Verify only 2 posts were synced
        assert result["total_posts"] == 2
        assert result["synced"] == 2
    
    @patch('app.services.platform_fetchers.analytics_sync_service.LinkedInAnalyticsFetcher')
    def test_sync_business_analytics_with_rate_limit(
        self,
        mock_linkedin_class,
        test_db: Session,
        test_business,
        test_social_account_linkedin,
        test_published_posts
    ):
        """Test syncing analytics with rate limit error."""
        # Get LinkedIn posts
        linkedin_posts = [p for p in test_published_posts if p.platform == "linkedin"]
        
        # Mock fetcher to raise rate limit on second post
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_post_analytics.side_effect = [
            {
                "platform": "linkedin",
                "likes_count": 100,
                "comments_count": 10,
                "shares_count": 5,
                "impressions": 1000,
                "engagement_rate": 11.5,
                "fetched_at": datetime.utcnow()
            },
            RateLimitError(
                "Rate limit exceeded",
                platform="linkedin",
                retry_after=3600
            )
        ]
        mock_linkedin_class.return_value = mock_fetcher
        
        # Sync posts
        service = AnalyticsSyncService(test_db)
        result = service.sync_business_analytics(
            test_business.id,
            platforms=["linkedin"],
            limit=2
        )
        
        # Verify results
        assert result["total_posts"] == 2
        assert result["synced"] == 1
        assert result["rate_limited"] == 1
        assert result["failed"] == 0
        assert len(result["errors"]) == 1
        assert "Rate limited" in result["errors"][0]
        
        # Verify fetcher was removed after rate limit
        assert "linkedin" not in service.fetchers
    
    @patch('app.services.platform_fetchers.analytics_sync_service.LinkedInAnalyticsFetcher')
    def test_sync_business_analytics_with_authentication_error(
        self,
        mock_linkedin_class,
        test_db: Session,
        test_business,
        test_social_account_linkedin,
        test_published_posts
    ):
        """Test syncing analytics with authentication error."""
        # Mock fetcher to raise authentication error
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_post_analytics.side_effect = AuthenticationError(
            "Invalid access token",
            platform="linkedin"
        )
        mock_linkedin_class.return_value = mock_fetcher
        
        # Sync posts
        service = AnalyticsSyncService(test_db)
        result = service.sync_business_analytics(
            test_business.id,
            platforms=["linkedin"],
            limit=1
        )
        
        # Verify results
        assert result["total_posts"] == 1
        assert result["synced"] == 0
        assert result["failed"] == 1
        assert len(result["errors"]) == 1
        assert "Failed to sync" in result["errors"][0]
    
    @patch('app.services.platform_fetchers.analytics_sync_service.LinkedInAnalyticsFetcher')
    def test_sync_business_analytics_mixed_results(
        self,
        mock_linkedin_class,
        test_db: Session,
        test_business,
        test_social_account_linkedin,
        test_published_posts
    ):
        """Test syncing analytics with mixed success/failure results."""
        linkedin_posts = [p for p in test_published_posts if p.platform == "linkedin"]
        
        # Mock fetcher with mixed results
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_post_analytics.side_effect = [
            {
                "platform": "linkedin",
                "likes_count": 100,
                "comments_count": 10,
                "shares_count": 5,
                "impressions": 1000,
                "engagement_rate": 11.5,
                "fetched_at": datetime.utcnow()
            },
            PostNotFoundError(
                "Post not found",
                platform="linkedin",
                post_id="not_found_123"
            ),
            {
                "platform": "linkedin",
                "likes_count": 200,
                "comments_count": 20,
                "shares_count": 10,
                "impressions": 2000,
                "engagement_rate": 11.5,
                "fetched_at": datetime.utcnow()
            }
        ]
        mock_linkedin_class.return_value = mock_fetcher
        
        # Sync posts
        service = AnalyticsSyncService(test_db)
        result = service.sync_business_analytics(
            test_business.id,
            platforms=["linkedin"]
        )
        
        # Verify results
        assert result["total_posts"] == len(linkedin_posts)
        assert result["synced"] == len(linkedin_posts) - 1  # One failed
        assert result["failed"] == 1
        assert len(result["errors"]) == 1
    
    def test_get_sync_status_no_syncs(
        self,
        test_db: Session,
        test_business,
        test_published_posts
    ):
        """Test getting sync status with no synced posts."""
        service = AnalyticsSyncService(test_db)
        status = service.get_sync_status(test_business.id)
        
        assert status["total_posts"] == 5
        assert status["synced_posts"] == 0
        assert status["unsynced_posts"] == 5
        assert status["last_sync_at"] is None
        assert status["sync_percentage"] == 0
    
    @patch('app.services.platform_fetchers.analytics_sync_service.LinkedInAnalyticsFetcher')
    def test_get_sync_status_with_syncs(
        self,
        mock_linkedin_class,
        test_db: Session,
        test_business,
        test_social_account_linkedin,
        test_published_posts
    ):
        """Test getting sync status after syncing posts."""
        # Mock fetcher
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_post_analytics.return_value = {
            "platform": "linkedin",
            "likes_count": 100,
            "comments_count": 10,
            "shares_count": 5,
            "impressions": 1000,
            "engagement_rate": 11.5,
            "fetched_at": datetime.utcnow()
        }
        mock_linkedin_class.return_value = mock_fetcher
        
        # Sync LinkedIn posts
        service = AnalyticsSyncService(test_db)
        service.sync_business_analytics(
            test_business.id,
            platforms=["linkedin"]
        )
        
        # Get sync status
        status = service.get_sync_status(test_business.id)
        
        linkedin_posts_count = len([p for p in test_published_posts if p.platform == "linkedin"])
        
        assert status["total_posts"] == 5
        assert status["synced_posts"] == linkedin_posts_count
        assert status["unsynced_posts"] == 5 - linkedin_posts_count
        assert status["last_sync_at"] is not None
        assert status["sync_percentage"] > 0
        assert status["sync_percentage"] == round((linkedin_posts_count / 5 * 100), 2)
    
    def test_sync_business_not_found(self, test_db: Session):
        """Test syncing analytics for non-existent business."""
        service = AnalyticsSyncService(test_db)
        
        with pytest.raises(ValueError, match="Business 99999 not found"):
            service.sync_business_analytics(99999)
    
    @patch('app.services.platform_fetchers.analytics_sync_service.LinkedInAnalyticsFetcher')
    def test_fetch_post_analytics_no_fetcher(
        self,
        mock_linkedin_class,
        test_db: Session,
        test_business,
        test_published_posts
    ):
        """Test fetching analytics when no fetcher is initialized."""
        linkedin_post = next(p for p in test_published_posts if p.platform == "linkedin")
        
        service = AnalyticsSyncService(test_db)
        # Don't initialize fetchers
        
        with pytest.raises(PlatformAPIError, match="No fetcher initialized"):
            service._fetch_post_analytics(linkedin_post)
    
    @patch('app.services.platform_fetchers.analytics_sync_service.LinkedInAnalyticsFetcher')
    def test_save_analytics_updates_post_cache(
        self,
        mock_linkedin_class,
        test_db: Session,
        test_business,
        test_social_account_linkedin,
        test_published_posts
    ):
        """Test that saving analytics updates post's cached metrics."""
        linkedin_post = next(p for p in test_published_posts if p.platform == "linkedin")
        
        # Mock fetcher
        mock_fetcher = MagicMock()
        analytics_data = {
            "platform": "linkedin",
            "platform_post_id": linkedin_post.platform_post_id,
            "likes_count": 999,
            "comments_count": 88,
            "shares_count": 77,
            "impressions": 10000,
            "engagement_rate": 11.64,
            "fetched_at": datetime.utcnow()
        }
        mock_fetcher.fetch_post_analytics.return_value = analytics_data
        mock_linkedin_class.return_value = mock_fetcher
        
        # Sync post
        service = AnalyticsSyncService(test_db)
        service.sync_single_post(linkedin_post.id)
        
        # Verify post cache was updated
        test_db.refresh(linkedin_post)
        assert linkedin_post.likes_count == 999
        assert linkedin_post.comments_count == 88
        assert linkedin_post.shares_count == 77
        assert linkedin_post.impressions_count == 10000
        assert linkedin_post.last_metrics_sync is not None
    
    @patch('app.services.platform_fetchers.analytics_sync_service.LinkedInAnalyticsFetcher')
    def test_multiple_analytics_records_created(
        self,
        mock_linkedin_class,
        test_db: Session,
        test_business,
        test_social_account_linkedin,
        test_published_posts
    ):
        """Test that multiple syncs create multiple analytics records."""
        linkedin_post = next(p for p in test_published_posts if p.platform == "linkedin")
        
        # Mock fetcher
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_post_analytics.return_value = {
            "platform": "linkedin",
            "platform_post_id": linkedin_post.platform_post_id,
            "likes_count": 100,
            "comments_count": 10,
            "shares_count": 5,
            "impressions": 1000,
            "engagement_rate": 11.5,
            "fetched_at": datetime.utcnow()
        }
        mock_linkedin_class.return_value = mock_fetcher
        
        # Sync post twice
        service = AnalyticsSyncService(test_db)
        service.sync_single_post(linkedin_post.id)
        
        # Change mock data for second sync
        mock_fetcher.fetch_post_analytics.return_value = {
            "platform": "linkedin",
            "platform_post_id": linkedin_post.platform_post_id,
            "likes_count": 200,
            "comments_count": 20,
            "shares_count": 10,
            "impressions": 2000,
            "engagement_rate": 11.5,
            "fetched_at": datetime.utcnow()
        }
        
        service.sync_single_post(linkedin_post.id)
        
        # Verify two analytics records exist
        analytics_count = test_db.query(PostAnalytics).filter(
            PostAnalytics.published_post_id == linkedin_post.id
        ).count()
        assert analytics_count == 2
        
        # Verify post cache has latest values
        test_db.refresh(linkedin_post)
        assert linkedin_post.likes_count == 200
        assert linkedin_post.comments_count == 20
