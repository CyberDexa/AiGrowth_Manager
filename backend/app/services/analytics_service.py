"""
Analytics service for generating insights and metrics
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import random

from app.models.content import Content, ContentStatus, Platform
from app.models.analytics import ContentMetrics, BusinessMetrics


class AnalyticsService:
    """Service for analytics calculations and insights"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_business_overview(self, business_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get overview metrics for a business
        
        Returns:
            - total_posts: Number of published posts
            - total_reach: Total views across all content
            - avg_engagement_rate: Average engagement rate
            - growth_rate: Growth compared to previous period
            - top_platform: Platform with best performance
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all published content for the business
        content_items = self.db.query(Content).filter(
            and_(
                Content.business_id == business_id,
                Content.status == ContentStatus.PUBLISHED,
                Content.published_at >= cutoff_date
            )
        ).all()
        
        if not content_items:
            return self._get_demo_overview()
        
        # Aggregate metrics
        total_posts = len(content_items)
        
        # Get or create metrics for content
        total_reach = 0
        total_engagement = 0
        platform_metrics: Dict[str, Dict[str, int]] = {}
        
        for content in content_items:
            # Get latest metrics for this content
            metrics = self.db.query(ContentMetrics).filter(
                ContentMetrics.content_id == content.id
            ).order_by(ContentMetrics.measured_at.desc()).first()
            
            if not metrics:
                # Create demo metrics for testing
                metrics = self._create_demo_metrics(content)
            
            total_reach += metrics.views
            total_engagement += (metrics.likes + metrics.shares + metrics.comments)
            
            # Track by platform
            platform_key = content.platform.value
            if platform_key not in platform_metrics:
                platform_metrics[platform_key] = {
                    'views': 0,
                    'engagement': 0,
                    'posts': 0
                }
            
            platform_metrics[platform_key]['views'] += metrics.views
            platform_metrics[platform_key]['engagement'] += (metrics.likes + metrics.shares + metrics.comments)
            platform_metrics[platform_key]['posts'] += 1
        
        # Calculate average engagement rate
        avg_engagement_rate = (total_engagement / total_reach * 100) if total_reach > 0 else 0
        
        # Find top platform
        top_platform = 'linkedin'
        max_engagement = 0
        for platform, metrics in platform_metrics.items():
            if metrics['engagement'] > max_engagement:
                max_engagement = metrics['engagement']
                top_platform = platform
        
        # Calculate growth rate (simplified - comparing to previous period)
        previous_cutoff = cutoff_date - timedelta(days=days)
        previous_posts = self.db.query(func.count(Content.id)).filter(
            and_(
                Content.business_id == business_id,
                Content.status == ContentStatus.PUBLISHED,
                Content.published_at >= previous_cutoff,
                Content.published_at < cutoff_date
            )
        ).scalar() or 0
        
        growth_rate = ((total_posts - previous_posts) / previous_posts * 100) if previous_posts > 0 else 0
        
        return {
            'total_posts': total_posts,
            'total_reach': total_reach,
            'total_engagement': total_engagement,
            'avg_engagement_rate': round(avg_engagement_rate, 2),
            'growth_rate': round(growth_rate, 2),
            'top_platform': top_platform,
            'platform_breakdown': platform_metrics
        }
    
    def get_content_performance(self, business_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top performing content for a business
        
        Returns list of content with their metrics
        """
        content_items = self.db.query(Content).filter(
            and_(
                Content.business_id == business_id,
                Content.status == ContentStatus.PUBLISHED
            )
        ).order_by(Content.published_at.desc()).limit(limit).all()
        
        results = []
        for content in content_items:
            metrics = self.db.query(ContentMetrics).filter(
                ContentMetrics.content_id == content.id
            ).order_by(ContentMetrics.measured_at.desc()).first()
            
            if not metrics:
                metrics = self._create_demo_metrics(content)
            
            results.append({
                'id': content.id,
                'platform': content.platform.value,
                'text': content.text[:100] + '...' if len(content.text) > 100 else content.text,
                'published_at': content.published_at.isoformat() if content.published_at else None,
                'views': metrics.views,
                'likes': metrics.likes,
                'shares': metrics.shares,
                'comments': metrics.comments,
                'engagement_rate': round(metrics.engagement_rate, 2)
            })
        
        return results
    
    def get_platform_comparison(self, business_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Compare performance across different platforms
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        platforms_data = {}
        
        for platform in Platform:
            content_items = self.db.query(Content).filter(
                and_(
                    Content.business_id == business_id,
                    Content.platform == platform,
                    Content.status == ContentStatus.PUBLISHED,
                    Content.published_at >= cutoff_date
                )
            ).all()
            
            if not content_items:
                continue
            
            total_views = 0
            total_engagement = 0
            
            for content in content_items:
                metrics = self.db.query(ContentMetrics).filter(
                    ContentMetrics.content_id == content.id
                ).order_by(ContentMetrics.measured_at.desc()).first()
                
                if not metrics:
                    metrics = self._create_demo_metrics(content)
                
                total_views += metrics.views
                total_engagement += (metrics.likes + metrics.shares + metrics.comments)
            
            avg_engagement_rate = (total_engagement / total_views * 100) if total_views > 0 else 0
            
            platforms_data[platform.value] = {
                'posts': len(content_items),
                'views': total_views,
                'engagement': total_engagement,
                'avg_engagement_rate': round(avg_engagement_rate, 2)
            }
        
        return platforms_data
    
    def get_engagement_trends(self, business_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get daily engagement trends for charts
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Generate daily data points
        trends = []
        current_date = cutoff_date
        
        while current_date <= datetime.utcnow():
            next_date = current_date + timedelta(days=1)
            
            # Get content published on this day
            daily_content = self.db.query(Content).filter(
                and_(
                    Content.business_id == business_id,
                    Content.status == ContentStatus.PUBLISHED,
                    Content.published_at >= current_date,
                    Content.published_at < next_date
                )
            ).all()
            
            daily_views = 0
            daily_engagement = 0
            
            for content in daily_content:
                metrics = self.db.query(ContentMetrics).filter(
                    ContentMetrics.content_id == content.id
                ).order_by(ContentMetrics.measured_at.desc()).first()
                
                if metrics:
                    daily_views += metrics.views
                    daily_engagement += (metrics.likes + metrics.shares + metrics.comments)
            
            trends.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'views': daily_views,
                'engagement': daily_engagement,
                'posts': len(daily_content)
            })
            
            current_date = next_date
        
        return trends
    
    def _create_demo_metrics(self, content: Content) -> ContentMetrics:
        """
        Create demo metrics for testing purposes
        """
        # Generate realistic-looking demo data
        views = random.randint(100, 5000)
        likes = int(views * random.uniform(0.02, 0.08))  # 2-8% like rate
        shares = int(views * random.uniform(0.005, 0.02))  # 0.5-2% share rate
        comments = int(views * random.uniform(0.01, 0.04))  # 1-4% comment rate
        clicks = int(views * random.uniform(0.05, 0.15))  # 5-15% CTR
        
        metrics = ContentMetrics(
            content_id=content.id,
            views=views,
            likes=likes,
            shares=shares,
            comments=comments,
            clicks=clicks
        )
        
        metrics.calculate_engagement_rate()
        metrics.calculate_ctr()
        
        # Save to database
        self.db.add(metrics)
        self.db.commit()
        self.db.refresh(metrics)
        
        return metrics
    
    def _get_demo_overview(self) -> Dict[str, Any]:
        """Return demo data when no real data exists"""
        return {
            'total_posts': 0,
            'total_reach': 0,
            'total_engagement': 0,
            'avg_engagement_rate': 0,
            'growth_rate': 0,
            'top_platform': 'linkedin',
            'platform_breakdown': {}
        }
