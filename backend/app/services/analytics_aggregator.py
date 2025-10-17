"""Analytics aggregator service - combines data from all platform fetchers."""

from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.post_analytics import PostAnalytics
from app.models.analytics_summary import AnalyticsSummary
from app.models.published_post import PublishedPost
from app.services.analytics_calculator import AnalyticsCalculator


class AnalyticsAggregator:
    """Service for aggregating analytics data from all platforms."""
    
    def __init__(self, db: Session):
        self.db = db
        self.calculator = AnalyticsCalculator()
    
    async def get_post_analytics(
        self,
        published_post_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get analytics for a single post."""
        analytics = self.db.query(PostAnalytics).filter(
            PostAnalytics.published_post_id == published_post_id
        ).first()
        
        if not analytics:
            return None
        
        # Get post details
        post = self.db.query(PublishedPost).filter(
            PublishedPost.id == published_post_id
        ).first()
        
        result = analytics.to_dict()
        if post:
            result["content_preview"] = post.content_text[:100] + "..." if len(post.content_text) > 100 else post.content_text
            result["published_at"] = post.published_at
        
        return result
    
    async def get_overview(
        self,
        business_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        platform: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive analytics overview for dashboard.
        """
        # Default to last 30 days if no dates provided
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Build query
        query = self.db.query(PostAnalytics).join(PublishedPost).filter(
            PostAnalytics.business_id == business_id,
            func.date(PostAnalytics.fetched_at) >= start_date,
            func.date(PostAnalytics.fetched_at) <= end_date
        )
        
        if platform and platform != 'all':
            query = query.filter(PostAnalytics.platform == platform)
        
        analytics_records = query.all()
        
        if not analytics_records:
            return self._empty_overview(start_date, end_date)
        
        # Convert to dicts for processing
        analytics_list = []
        for record in analytics_records:
            data = record.to_dict()
            # Add published_at from relationship
            if record.published_post:
                data["published_at"] = record.published_post.published_at
                data["content_text"] = record.published_post.content_text
                data["content_images"] = record.published_post.content_images
                data["content_links"] = record.published_post.content_links
            analytics_list.append(data)
        
        # Calculate overall summary
        summary = {
            "total_posts": len(analytics_list),
            "total_likes": sum(a["likes_count"] for a in analytics_list),
            "total_comments": sum(a["comments_count"] for a in analytics_list),
            "total_shares": sum(a["shares_count"] for a in analytics_list),
            "total_impressions": sum(a["impressions"] for a in analytics_list),
            "total_reach": sum(a["reach"] for a in analytics_list),
            "total_clicks": sum(a["clicks"] for a in analytics_list),
        }
        
        if summary["total_impressions"] > 0:
            total_engagement = summary["total_likes"] + summary["total_comments"] + summary["total_shares"]
            summary["avg_engagement_rate"] = round(
                (total_engagement / summary["total_impressions"]) * 100,
                2
            )
        else:
            summary["avg_engagement_rate"] = 0.0
        
        # Platform breakdown
        platforms_data = {}
        for record in analytics_list:
            platform_key = record["platform"]
            if platform_key not in platforms_data:
                platforms_data[platform_key] = []
            platforms_data[platform_key].append(record)
        
        by_platform = []
        total_posts_all = len(analytics_list)
        
        for plat, plat_analytics in platforms_data.items():
            plat_posts = len(plat_analytics)
            plat_likes = sum(a["likes_count"] for a in plat_analytics)
            plat_comments = sum(a["comments_count"] for a in plat_analytics)
            plat_shares = sum(a["shares_count"] for a in plat_analytics)
            plat_impressions = sum(a["impressions"] for a in plat_analytics)
            plat_reach = sum(a["reach"] for a in plat_analytics)
            
            plat_engagement = plat_likes + plat_comments + plat_shares
            plat_eng_rate = round(
                (plat_engagement / plat_impressions * 100) if plat_impressions > 0 else 0.0,
                2
            )
            
            by_platform.append({
                "platform": plat,
                "total_posts": plat_posts,
                "total_likes": plat_likes,
                "total_comments": plat_comments,
                "total_shares": plat_shares,
                "total_impressions": plat_impressions,
                "total_reach": plat_reach,
                "avg_engagement_rate": plat_eng_rate,
                "percentage_of_total": round((plat_posts / total_posts_all) * 100, 1)
            })
        
        # Sort by engagement rate
        by_platform.sort(key=lambda x: x["avg_engagement_rate"], reverse=True)
        
        # Calculate trends
        trends = self.calculator.calculate_engagement_trends(analytics_list, period="daily")
        
        # Find top posts
        top_posts_data = self.calculator.identify_top_posts(analytics_list, limit=10)
        top_posts = []
        for post_data in top_posts_data:
            top_posts.append({
                "id": post_data.get("id"),
                "published_post_id": post_data.get("published_post_id"),
                "content_preview": post_data.get("content_text", "")[:100] + "..." if post_data.get("content_text") and len(post_data.get("content_text", "")) > 100 else post_data.get("content_text", ""),
                "platform": post_data.get("platform"),
                "published_at": post_data.get("published_at"),
                "engagement_rate": post_data.get("engagement_rate"),
                "likes_count": post_data.get("likes_count"),
                "comments_count": post_data.get("comments_count"),
                "shares_count": post_data.get("shares_count"),
                "impressions": post_data.get("impressions"),
                "platform_post_url": post_data.get("platform_post_url")
            })
        
        # Best posting times
        best_times_data = self.calculator.find_best_posting_times(analytics_list)
        
        # Convert to API format
        best_times = []
        for day, stats in best_times_data.get("by_day", {}).items():
            # Find best hour for this day
            day_posts = [a for a in analytics_list if datetime.fromisoformat(str(a["published_at"]).replace('Z', '+00:00')).strftime("%A") == day]
            best_hour = 12  # default
            if day_posts:
                hour_rates = {}
                for post in day_posts:
                    pub_at = datetime.fromisoformat(str(post["published_at"]).replace('Z', '+00:00'))
                    hour = pub_at.hour
                    if hour not in hour_rates:
                        hour_rates[hour] = []
                    hour_rates[hour].append(post["engagement_rate"])
                if hour_rates:
                    best_hour = max(hour_rates.items(), key=lambda x: sum(x[1])/len(x[1]))[0]
            
            best_times.append({
                "day_of_week": day,
                "hour_of_day": best_hour,
                "avg_engagement_rate": stats["avg_engagement_rate"],
                "posts_count": stats["posts_count"],
                "confidence_score": stats["confidence"]
            })
        
        # Sort by engagement rate
        best_times.sort(key=lambda x: x["avg_engagement_rate"], reverse=True)
        
        return {
            "period_start": start_date,
            "period_end": end_date,
            "summary": summary,
            "by_platform": by_platform,
            "trends": trends,
            "top_posts": top_posts,
            "best_times": best_times[:7]  # Top 7 days
        }
    
    async def get_platform_comparison(
        self,
        business_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Compare performance across all platforms."""
        analytics_records = self.db.query(PostAnalytics).filter(
            PostAnalytics.business_id == business_id,
            func.date(PostAnalytics.fetched_at) >= start_date,
            func.date(PostAnalytics.fetched_at) <= end_date
        ).all()
        
        # Group by platform
        by_platform = {}
        for record in analytics_records:
            platform = record.platform
            if platform not in by_platform:
                by_platform[platform] = []
            by_platform[platform].append(record.to_dict())
        
        # Use calculator to compare
        comparison = self.calculator.compare_platforms(by_platform)
        
        return {
            "period_start": start_date,
            "period_end": end_date,
            **comparison
        }
    
    async def get_best_times(
        self,
        business_id: int,
        platform: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get best times to post analysis."""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        query = self.db.query(PostAnalytics).join(PublishedPost).filter(
            PostAnalytics.business_id == business_id,
            func.date(PostAnalytics.fetched_at) >= start_date
        )
        
        if platform and platform != 'all':
            query = query.filter(PostAnalytics.platform == platform)
        
        analytics_records = query.all()
        
        analytics_list = []
        for record in analytics_records:
            data = record.to_dict()
            if record.published_post:
                data["published_at"] = record.published_post.published_at
            analytics_list.append(data)
        
        best_times_data = self.calculator.find_best_posting_times(analytics_list)
        
        # Format response
        by_day = []
        for day, stats in sorted(best_times_data.get("by_day", {}).items()):
            by_day.append({
                "day": day,
                "day_number": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(day),
                "posts_count": stats["posts_count"],
                "avg_engagement_rate": stats["avg_engagement_rate"],
                "total_impressions": 0,  # Would need to calculate
                "best_hour": 12  # Would need to calculate per day
            })
        
        by_hour = []
        for hour, stats in sorted(best_times_data.get("by_hour", {}).items()):
            by_hour.append({
                "hour": hour,
                "posts_count": stats["posts_count"],
                "avg_engagement_rate": stats["avg_engagement_rate"],
                "total_impressions": 0  # Would need to calculate
            })
        
        # Generate recommendations
        recommendations = []
        if best_times_data.get("best_day") and best_times_data.get("best_hour"):
            recommendations.append(
                f"Post on {best_times_data['best_day']} at {best_times_data['best_hour']}:00 for best engagement"
            )
        
        return {
            "by_day": by_day,
            "by_hour": by_hour,
            "recommendations": recommendations
        }
    
    async def generate_summary(
        self,
        business_id: int,
        period_type: str,
        period_start: date,
        period_end: date,
        platform: str = "all"
    ) -> Dict[str, Any]:
        """Generate an analytics summary for a time period."""
        query = self.db.query(PostAnalytics).filter(
            PostAnalytics.business_id == business_id,
            func.date(PostAnalytics.fetched_at) >= period_start,
            func.date(PostAnalytics.fetched_at) <= period_end
        )
        
        if platform != "all":
            query = query.filter(PostAnalytics.platform == platform)
        
        analytics_records = query.all()
        
        if not analytics_records:
            return None
        
        # Calculate summary metrics
        total_posts = len(analytics_records)
        total_likes = sum(r.likes_count for r in analytics_records)
        total_comments = sum(r.comments_count for r in analytics_records)
        total_shares = sum(r.shares_count for r in analytics_records)
        total_impressions = sum(r.impressions for r in analytics_records)
        total_reach = sum(r.reach for r in analytics_records)
        total_clicks = sum(r.clicks for r in analytics_records)
        
        # Calculate averages
        total_engagement = total_likes + total_comments + total_shares
        avg_engagement_rate = round(
            (total_engagement / total_impressions * 100) if total_impressions > 0 else 0.0,
            2
        )
        avg_impressions = round(total_impressions / total_posts) if total_posts > 0 else 0
        
        # Find best post
        best_post = max(analytics_records, key=lambda x: x.engagement_rate) if analytics_records else None
        
        summary_data = {
            "business_id": business_id,
            "platform": platform,
            "period_type": period_type,
            "period_start": period_start,
            "period_end": period_end,
            "total_posts": total_posts,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "total_impressions": total_impressions,
            "total_reach": total_reach,
            "total_clicks": total_clicks,
            "avg_engagement_rate": avg_engagement_rate,
            "avg_impressions": avg_impressions,
            "follower_growth": 0,  # Would need historical data
            "best_post_id": best_post.published_post_id if best_post else None,
            "best_post_engagement_rate": float(best_post.engagement_rate) if best_post else None
        }
        
        # Create or update summary in database
        existing_summary = self.db.query(AnalyticsSummary).filter(
            and_(
                AnalyticsSummary.business_id == business_id,
                AnalyticsSummary.platform == platform,
                AnalyticsSummary.period_start == period_start,
                AnalyticsSummary.period_end == period_end
            )
        ).first()
        
        if existing_summary:
            for key, value in summary_data.items():
                setattr(existing_summary, key, value)
            existing_summary.updated_at = datetime.utcnow()
            summary = existing_summary
        else:
            summary = AnalyticsSummary(**summary_data)
            self.db.add(summary)
        
        self.db.commit()
        self.db.refresh(summary)
        
        return summary.to_dict()
    
    def _empty_overview(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Return empty overview structure."""
        return {
            "period_start": start_date,
            "period_end": end_date,
            "summary": {
                "total_posts": 0,
                "total_likes": 0,
                "total_comments": 0,
                "total_shares": 0,
                "total_impressions": 0,
                "total_reach": 0,
                "total_clicks": 0,
                "avg_engagement_rate": 0.0
            },
            "by_platform": [],
            "trends": [],
            "top_posts": [],
            "best_times": []
        }
