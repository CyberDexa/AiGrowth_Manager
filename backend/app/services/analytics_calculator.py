"""Analytics calculator service for computing metrics and insights."""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from collections import defaultdict
from decimal import Decimal
import statistics


class AnalyticsCalculator:
    """Service for calculating analytics metrics and insights."""
    
    @staticmethod
    def calculate_engagement_rate(
        likes: int,
        comments: int,
        shares: int,
        impressions: int
    ) -> float:
        """
        Calculate engagement rate as percentage.
        Formula: (likes + comments + shares) / impressions * 100
        """
        if impressions == 0:
            return 0.0
        
        total_engagement = likes + comments + shares
        rate = (total_engagement / impressions) * 100
        return round(rate, 2)
    
    @staticmethod
    def calculate_click_through_rate(clicks: int, impressions: int) -> float:
        """
        Calculate click-through rate as percentage.
        Formula: clicks / impressions * 100
        """
        if impressions == 0:
            return 0.0
        
        rate = (clicks / impressions) * 100
        return round(rate, 2)
    
    @staticmethod
    def calculate_virality_score(shares: int, impressions: int) -> float:
        """
        Calculate virality score based on shares.
        Formula: shares / impressions * 100
        """
        if impressions == 0:
            return 0.0
        
        score = (shares / impressions) * 100
        return round(score, 2)
    
    @staticmethod
    def calculate_video_completion_rate(
        watch_time: int,
        views: int,
        video_duration: int
    ) -> Optional[float]:
        """
        Calculate video completion rate.
        Formula: (avg_watch_time / video_duration) * 100
        """
        if views == 0 or video_duration == 0:
            return None
        
        avg_watch_time = watch_time / views
        rate = (avg_watch_time / video_duration) * 100
        return round(min(rate, 100.0), 2)  # Cap at 100%
    
    @staticmethod
    def calculate_growth_rate(current: int, previous: int) -> float:
        """
        Calculate growth rate percentage.
        Formula: ((current - previous) / previous) * 100
        """
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        
        growth = ((current - previous) / previous) * 100
        return round(growth, 2)
    
    @staticmethod
    def calculate_average_metrics(analytics_list: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate average metrics from a list of analytics records."""
        if not analytics_list:
            return {
                "avg_engagement_rate": 0.0,
                "avg_impressions": 0.0,
                "avg_clicks": 0.0,
                "avg_likes": 0.0,
                "avg_comments": 0.0,
                "avg_shares": 0.0
            }
        
        total_engagement_rate = sum(a.get("engagement_rate", 0) for a in analytics_list)
        total_impressions = sum(a.get("impressions", 0) for a in analytics_list)
        total_clicks = sum(a.get("clicks", 0) for a in analytics_list)
        total_likes = sum(a.get("likes_count", 0) for a in analytics_list)
        total_comments = sum(a.get("comments_count", 0) for a in analytics_list)
        total_shares = sum(a.get("shares_count", 0) for a in analytics_list)
        
        count = len(analytics_list)
        
        return {
            "avg_engagement_rate": round(total_engagement_rate / count, 2),
            "avg_impressions": round(total_impressions / count, 2),
            "avg_clicks": round(total_clicks / count, 2),
            "avg_likes": round(total_likes / count, 2),
            "avg_comments": round(total_comments / count, 2),
            "avg_shares": round(total_shares / count, 2)
        }
    
    @staticmethod
    def find_best_posting_times(
        analytics_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze best times to post based on engagement rates.
        Returns insights by day of week and hour of day.
        """
        if not analytics_list:
            return {
                "best_day": None,
                "best_hour": None,
                "by_day": {},
                "by_hour": {}
            }
        
        # Group by day of week
        day_stats = defaultdict(lambda: {"engagement_rates": [], "posts": 0})
        hour_stats = defaultdict(lambda: {"engagement_rates": [], "posts": 0})
        
        for analytics in analytics_list:
            published_at = analytics.get("published_at")
            if not published_at:
                continue
            
            # Parse datetime if it's a string
            if isinstance(published_at, str):
                try:
                    published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                except:
                    continue
            
            engagement_rate = analytics.get("engagement_rate", 0)
            
            # Day of week analysis
            day_name = published_at.strftime("%A")
            day_stats[day_name]["engagement_rates"].append(engagement_rate)
            day_stats[day_name]["posts"] += 1
            
            # Hour of day analysis
            hour = published_at.hour
            hour_stats[hour]["engagement_rates"].append(engagement_rate)
            hour_stats[hour]["posts"] += 1
        
        # Calculate averages
        by_day = {}
        for day, stats in day_stats.items():
            if stats["engagement_rates"]:
                by_day[day] = {
                    "avg_engagement_rate": round(statistics.mean(stats["engagement_rates"]), 2),
                    "posts_count": stats["posts"],
                    "confidence": min(stats["posts"] / 5.0, 1.0) * 100  # 5+ posts = 100% confidence
                }
        
        by_hour = {}
        for hour, stats in hour_stats.items():
            if stats["engagement_rates"]:
                by_hour[hour] = {
                    "avg_engagement_rate": round(statistics.mean(stats["engagement_rates"]), 2),
                    "posts_count": stats["posts"],
                    "confidence": min(stats["posts"] / 3.0, 1.0) * 100  # 3+ posts = 100% confidence
                }
        
        # Find best day and hour
        best_day = max(by_day.items(), key=lambda x: x[1]["avg_engagement_rate"])[0] if by_day else None
        best_hour = max(by_hour.items(), key=lambda x: x[1]["avg_engagement_rate"])[0] if by_hour else None
        
        return {
            "best_day": best_day,
            "best_hour": best_hour,
            "by_day": by_day,
            "by_hour": by_hour
        }
    
    @staticmethod
    def calculate_engagement_trends(
        analytics_list: List[Dict[str, Any]],
        period: str = "daily"
    ) -> List[Dict[str, Any]]:
        """
        Calculate engagement trends over time.
        Groups data by day/week/month depending on period.
        """
        if not analytics_list:
            return []
        
        # Group by date
        trends = defaultdict(lambda: {
            "total_engagement": 0,
            "total_impressions": 0,
            "posts": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0
        })
        
        for analytics in analytics_list:
            published_at = analytics.get("published_at")
            if not published_at:
                continue
            
            # Parse datetime if string
            if isinstance(published_at, str):
                try:
                    published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                except:
                    continue
            
            # Group by period
            if period == "daily":
                date_key = published_at.date().isoformat()
            elif period == "weekly":
                # Get Monday of the week
                monday = published_at.date() - timedelta(days=published_at.weekday())
                date_key = monday.isoformat()
            else:  # monthly
                date_key = f"{published_at.year}-{published_at.month:02d}-01"
            
            trends[date_key]["posts"] += 1
            trends[date_key]["likes"] += analytics.get("likes_count", 0)
            trends[date_key]["comments"] += analytics.get("comments_count", 0)
            trends[date_key]["shares"] += analytics.get("shares_count", 0)
            trends[date_key]["total_impressions"] += analytics.get("impressions", 0)
        
        # Calculate engagement rates
        result = []
        for date_key in sorted(trends.keys()):
            data = trends[date_key]
            data["total_engagement"] = data["likes"] + data["comments"] + data["shares"]
            
            if data["total_impressions"] > 0:
                data["engagement_rate"] = round(
                    (data["total_engagement"] / data["total_impressions"]) * 100,
                    2
                )
            else:
                data["engagement_rate"] = 0.0
            
            result.append({
                "date": date_key,
                "engagement_rate": data["engagement_rate"],
                "total_engagement": data["total_engagement"],
                "impressions": data["total_impressions"],
                "posts_count": data["posts"],
                "likes": data["likes"],
                "comments": data["comments"],
                "shares": data["shares"]
            })
        
        return result
    
    @staticmethod
    def identify_top_posts(
        analytics_list: List[Dict[str, Any]],
        metric: str = "engagement_rate",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Identify top performing posts based on specified metric.
        Metric options: engagement_rate, likes_count, impressions, total_engagement
        """
        if not analytics_list:
            return []
        
        # Sort by metric
        if metric == "total_engagement":
            sorted_analytics = sorted(
                analytics_list,
                key=lambda x: (x.get("likes_count", 0) + 
                             x.get("comments_count", 0) + 
                             x.get("shares_count", 0)),
                reverse=True
            )
        else:
            sorted_analytics = sorted(
                analytics_list,
                key=lambda x: x.get(metric, 0),
                reverse=True
            )
        
        return sorted_analytics[:limit]
    
    @staticmethod
    def compare_platforms(
        analytics_by_platform: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Compare performance across different platforms.
        Returns winner, rankings, and insights.
        """
        if not analytics_by_platform:
            return {
                "best_platform": None,
                "rankings": [],
                "insights": []
            }
        
        platform_metrics = {}
        
        for platform, analytics_list in analytics_by_platform.items():
            if not analytics_list:
                continue
            
            total_posts = len(analytics_list)
            total_likes = sum(a.get("likes_count", 0) for a in analytics_list)
            total_comments = sum(a.get("comments_count", 0) for a in analytics_list)
            total_shares = sum(a.get("shares_count", 0) for a in analytics_list)
            total_impressions = sum(a.get("impressions", 0) for a in analytics_list)
            
            total_engagement = total_likes + total_comments + total_shares
            avg_engagement_rate = round(
                (total_engagement / total_impressions * 100) if total_impressions > 0 else 0.0,
                2
            )
            
            platform_metrics[platform] = {
                "platform": platform,
                "total_posts": total_posts,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "total_shares": total_shares,
                "total_impressions": total_impressions,
                "avg_engagement_rate": avg_engagement_rate
            }
        
        # Rank platforms by engagement rate
        rankings = sorted(
            platform_metrics.values(),
            key=lambda x: x["avg_engagement_rate"],
            reverse=True
        )
        
        best_platform = rankings[0]["platform"] if rankings else None
        
        # Generate insights
        insights = []
        if len(rankings) > 1:
            insights.append(
                f"{rankings[0]['platform']} has the highest engagement rate at {rankings[0]['avg_engagement_rate']}%"
            )
            insights.append(
                f"{rankings[-1]['platform']} has the lowest engagement rate at {rankings[-1]['avg_engagement_rate']}%"
            )
        
        return {
            "best_platform": best_platform,
            "rankings": rankings,
            "insights": insights
        }
    
    @staticmethod
    def calculate_content_type_performance(
        analytics_list: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyze performance by content type (text, image, video, link).
        """
        content_types = defaultdict(lambda: {
            "posts": 0,
            "engagement_rates": [],
            "impressions": []
        })
        
        for analytics in analytics_list:
            # Determine content type based on fields
            content_type = "text"  # default
            
            if analytics.get("content_images") and len(analytics.get("content_images", [])) > 0:
                content_type = "image"
            elif analytics.get("video_views", 0) > 0:
                content_type = "video"
            elif analytics.get("content_links") and len(analytics.get("content_links", [])) > 0:
                content_type = "link"
            
            content_types[content_type]["posts"] += 1
            content_types[content_type]["engagement_rates"].append(analytics.get("engagement_rate", 0))
            content_types[content_type]["impressions"].append(analytics.get("impressions", 0))
        
        # Calculate averages
        result = {}
        for ctype, data in content_types.items():
            if data["engagement_rates"]:
                result[ctype] = {
                    "posts_count": data["posts"],
                    "avg_engagement_rate": round(statistics.mean(data["engagement_rates"]), 2),
                    "avg_impressions": round(statistics.mean(data["impressions"]), 2)
                }
        
        return result
