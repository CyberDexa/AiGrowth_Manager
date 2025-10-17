"""Analytics sync service to orchestrate fetching analytics from all platforms."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.business import Business
from app.models.published_post import PublishedPost
from app.models.post_analytics import PostAnalytics
from app.models.social_account import SocialAccount
from .linkedin_fetcher import LinkedInAnalyticsFetcher
from .twitter_fetcher import TwitterAnalyticsFetcher
from .meta_fetcher import MetaAnalyticsFetcher
from .exceptions import PlatformAPIError, RateLimitError, AuthenticationError

logger = logging.getLogger(__name__)


class AnalyticsSyncService:
    """
    Service to sync analytics data from all connected social media platforms.
    
    This service:
    1. Fetches published posts for a business
    2. Initializes appropriate platform fetchers with access tokens
    3. Fetches analytics for each post from the platform
    4. Saves/updates analytics data in the database
    5. Returns summary of sync results (successes, failures, rate limits)
    """
    
    def __init__(self, db: Session):
        """
        Initialize the sync service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.fetchers: Dict[str, Any] = {}
        
    def sync_business_analytics(
        self,
        business_id: int,
        platforms: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Sync analytics for all published posts of a business.
        
        Args:
            business_id: Business ID
            platforms: List of platforms to sync (None = all platforms)
            limit: Maximum number of posts to sync per platform
            
        Returns:
            Dictionary with sync results:
            {
                "total_posts": 50,
                "synced": 45,
                "failed": 3,
                "rate_limited": 2,
                "by_platform": {
                    "linkedin": {"synced": 10, "failed": 0, "rate_limited": 0},
                    "twitter": {"synced": 15, "failed": 1, "rate_limited": 0},
                    ...
                },
                "errors": [list of error messages]
            }
        """
        logger.info(f"Starting analytics sync for business {business_id}")
        
        # Verify business exists
        business = self.db.query(Business).filter(Business.id == business_id).first()
        if not business:
            raise ValueError(f"Business {business_id} not found")
        
        # Initialize fetchers for this business
        self._initialize_fetchers(business_id)
        
        # Get published posts
        query = self.db.query(PublishedPost).filter(
            PublishedPost.business_id == business_id,
            PublishedPost.status == "published"
        )
        
        if platforms:
            query = query.filter(PublishedPost.platform.in_(platforms))
        
        if limit:
            query = query.limit(limit)
        
        posts = query.all()
        
        # Initialize results
        results = {
            "total_posts": len(posts),
            "synced": 0,
            "failed": 0,
            "rate_limited": 0,
            "by_platform": {},
            "errors": []
        }
        
        # Sync each post
        for post in posts:
            platform = post.platform.lower()
            
            # Initialize platform results if needed
            if platform not in results["by_platform"]:
                results["by_platform"][platform] = {
                    "synced": 0,
                    "failed": 0,
                    "rate_limited": 0
                }
            
            try:
                # Fetch and save analytics
                analytics_data = self._fetch_post_analytics(post)
                self._save_analytics(post, analytics_data)
                
                # Update counts
                results["synced"] += 1
                results["by_platform"][platform]["synced"] += 1
                
                logger.info(f"Synced analytics for post {post.id} ({platform})")
                
            except RateLimitError as e:
                results["rate_limited"] += 1
                results["by_platform"][platform]["rate_limited"] += 1
                error_msg = f"Rate limited on {platform} for post {post.id}: {str(e)}"
                results["errors"].append(error_msg)
                logger.warning(error_msg)
                
                # Stop syncing this platform if rate limited
                if platform in self.fetchers:
                    del self.fetchers[platform]
                
            except Exception as e:
                results["failed"] += 1
                results["by_platform"][platform]["failed"] += 1
                error_msg = f"Failed to sync post {post.id} ({platform}): {str(e)}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        logger.info(f"Completed analytics sync for business {business_id}: "
                   f"{results['synced']}/{results['total_posts']} successful")
        
        return results
    
    def sync_single_post(
        self,
        post_id: int
    ) -> Dict[str, Any]:
        """
        Sync analytics for a single published post.
        
        Args:
            post_id: Published post ID
            
        Returns:
            Analytics data dictionary or error information
        """
        # Get post
        post = self.db.query(PublishedPost).filter(PublishedPost.id == post_id).first()
        if not post:
            raise ValueError(f"Post {post_id} not found")
        
        if post.status != "published":
            raise ValueError(f"Post {post_id} is not published (status: {post.status})")
        
        logger.info(f"Syncing analytics for post {post_id} ({post.platform})")
        
        try:
            # Initialize fetchers
            self._initialize_fetchers(post.business_id)
            
            # Fetch and save analytics
            analytics_data = self._fetch_post_analytics(post)
            analytics_record = self._save_analytics(post, analytics_data)
            
            return {
                "success": True,
                "post_id": post_id,
                "platform": post.platform,
                "analytics": analytics_data,
                "analytics_id": analytics_record.id
            }
            
        except Exception as e:
            logger.error(f"Failed to sync post {post_id}: {e}")
            return {
                "success": False,
                "post_id": post_id,
                "platform": post.platform,
                "error": str(e)
            }
    
    def _initialize_fetchers(self, business_id: int):
        """
        Initialize platform fetchers with access tokens.
        
        Args:
            business_id: Business ID to get social accounts for
        """
        # Get all active social accounts for this business
        social_accounts = self.db.query(SocialAccount).filter(
            SocialAccount.business_id == business_id,
            SocialAccount.is_active == True
        ).all()
        
        for account in social_accounts:
            platform = account.platform.lower()
            
            # Skip if no access token
            if not account.access_token:
                logger.warning(f"No access token for {platform} account {account.id}")
                continue
            
            try:
                # Initialize appropriate fetcher
                if platform == "linkedin":
                    self.fetchers[platform] = LinkedInAnalyticsFetcher(
                        access_token=account.access_token,
                        organization_id=account.page_id  # LinkedIn org ID
                    )
                    
                elif platform == "twitter":
                    self.fetchers[platform] = TwitterAnalyticsFetcher(
                        access_token=account.access_token
                    )
                    
                elif platform in ["facebook", "instagram"]:
                    self.fetchers[platform] = MetaAnalyticsFetcher(
                        access_token=account.access_token,
                        page_id=account.page_id,
                        instagram_account_id=account.instagram_account_id
                    )
                    
                else:
                    logger.warning(f"Unsupported platform: {platform}")
                    
                logger.info(f"Initialized {platform} fetcher for business {business_id}")
                
            except Exception as e:
                logger.error(f"Failed to initialize {platform} fetcher: {e}")
    
    def _fetch_post_analytics(self, post: PublishedPost) -> Dict[str, Any]:
        """
        Fetch analytics for a published post.
        
        Args:
            post: PublishedPost model instance
            
        Returns:
            Analytics data dictionary
            
        Raises:
            PlatformAPIError: If fetching fails
        """
        platform = post.platform.lower()
        
        # Check if we have a fetcher for this platform
        if platform not in self.fetchers:
            raise PlatformAPIError(
                f"No fetcher initialized for platform {platform}",
                platform=platform
            )
        
        fetcher = self.fetchers[platform]
        
        # Fetch analytics
        try:
            analytics_data = fetcher.fetch_post_analytics(
                post_id=str(post.id),
                platform_post_id=post.platform_post_id
            )
            
            return analytics_data
            
        except AuthenticationError as e:
            logger.error(f"Authentication failed for {platform}: {e}")
            # Remove fetcher to prevent further attempts
            del self.fetchers[platform]
            raise
            
        except Exception as e:
            logger.error(f"Failed to fetch analytics for post {post.id}: {e}")
            raise
    
    def _save_analytics(
        self,
        post: PublishedPost,
        analytics_data: Dict[str, Any]
    ) -> PostAnalytics:
        """
        Save or update analytics data in database.
        
        Args:
            post: PublishedPost model instance
            analytics_data: Analytics data dictionary
            
        Returns:
            PostAnalytics model instance
        """
        # Check if analytics record already exists
        existing_analytics = self.db.query(PostAnalytics).filter(
            PostAnalytics.published_post_id == post.id
        ).order_by(PostAnalytics.fetched_at.desc()).first()
        
        # Create new analytics record
        analytics = PostAnalytics(
            published_post_id=post.id,
            business_id=post.business_id,
            platform=analytics_data.get("platform", post.platform),
            likes_count=analytics_data.get("likes_count", 0),
            comments_count=analytics_data.get("comments_count", 0),
            shares_count=analytics_data.get("shares_count", 0),
            reactions_count=analytics_data.get("reactions_count", 0),
            retweets_count=analytics_data.get("retweets_count", 0),
            quote_tweets_count=analytics_data.get("quote_tweets_count", 0),
            impressions=analytics_data.get("impressions", 0),
            reach=analytics_data.get("reach", 0),
            clicks=analytics_data.get("clicks", 0),
            video_views=analytics_data.get("video_views", 0),
            video_watch_time=analytics_data.get("video_watch_time", 0),
            engagement_rate=analytics_data.get("engagement_rate", 0.0),
            click_through_rate=analytics_data.get("click_through_rate", 0.0),
            fetched_at=analytics_data.get("fetched_at", datetime.utcnow()),
            platform_post_id=analytics_data.get("platform_post_id"),
            platform_post_url=analytics_data.get("platform_post_url", post.platform_post_url)
        )
        
        self.db.add(analytics)
        self.db.commit()
        self.db.refresh(analytics)
        
        # Update post's metrics cache
        post.likes_count = analytics.likes_count
        post.comments_count = analytics.comments_count
        post.shares_count = analytics.shares_count
        post.impressions_count = analytics.impressions
        post.last_metrics_sync = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Saved analytics for post {post.id}")
        
        return analytics
    
    def get_sync_status(self, business_id: int) -> Dict[str, Any]:
        """
        Get sync status for a business (when was last sync, how many posts synced, etc.)
        
        Args:
            business_id: Business ID
            
        Returns:
            Sync status dictionary
        """
        # Get all published posts
        total_posts = self.db.query(PublishedPost).filter(
            PublishedPost.business_id == business_id,
            PublishedPost.status == "published"
        ).count()
        
        # Get posts with analytics
        synced_posts = self.db.query(PublishedPost).filter(
            PublishedPost.business_id == business_id,
            PublishedPost.status == "published",
            PublishedPost.last_metrics_sync.isnot(None)
        ).count()
        
        # Get last sync time
        last_sync = self.db.query(PostAnalytics).filter(
            PostAnalytics.business_id == business_id
        ).order_by(PostAnalytics.fetched_at.desc()).first()
        
        return {
            "total_posts": total_posts,
            "synced_posts": synced_posts,
            "unsynced_posts": total_posts - synced_posts,
            "last_sync_at": last_sync.fetched_at if last_sync else None,
            "sync_percentage": round((synced_posts / total_posts * 100), 2) if total_posts > 0 else 0
        }
