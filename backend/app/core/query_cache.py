"""
Query Result Caching

Redis-based caching for expensive database queries.
Useful for analytics and dashboard data that doesn't change frequently.
"""
import json
import hashlib
import logging
from typing import Optional, Any, Callable
from functools import wraps
from datetime import datetime

from app.core.redis_client import get_redis_client

logger = logging.getLogger(__name__)


class QueryCache:
    """
    Redis-based query result caching.
    
    Usage:
        cache = QueryCache(ttl=300)  # 5 minutes
        
        # Manual caching
        result = cache.get("key")
        if result is None:
            result = expensive_query()
            cache.set("key", result)
        
        # Decorator caching
        @cache.cached(ttl=60)
        def get_analytics(business_id: int):
            return db.query(...).all()
    """
    
    def __init__(self, ttl: int = 300, prefix: str = "query_cache"):
        """
        Initialize query cache.
        
        Args:
            ttl: Time-to-live in seconds (default: 5 minutes)
            prefix: Redis key prefix (default: "query_cache")
        """
        self.redis = get_redis_client()
        self.ttl = ttl
        self.prefix = prefix
        self.enabled = self.redis is not None
        
        if not self.enabled:
            logger.warning("Query caching disabled: Redis not available")
    
    def _make_key(self, key: str) -> str:
        """Generate Redis key with prefix"""
        return f"{self.prefix}:{key}"
    
    def _hash_key(self, data: Any) -> str:
        """Generate hash from data for cache key"""
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found/expired
        """
        if not self.enabled:
            return None
        
        try:
            redis_key = self._make_key(key)
            value = self.redis.get(redis_key)
            
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            
            logger.debug(f"Cache MISS: {key}")
            return None
        
        except Exception as e:
            logger.warning(f"Cache get error for {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set cached value.
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Custom TTL for this key (optional)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            redis_key = self._make_key(key)
            ttl_seconds = ttl or self.ttl
            
            json_value = json.dumps(value, default=str)
            self.redis.setex(redis_key, ttl_seconds, json_value)
            
            logger.debug(f"Cache SET: {key} (TTL: {ttl_seconds}s)")
            return True
        
        except Exception as e:
            logger.warning(f"Cache set error for {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete cached value.
        
        Args:
            key: Cache key
        
        Returns:
            True if deleted, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            redis_key = self._make_key(key)
            result = self.redis.delete(redis_key)
            logger.debug(f"Cache DELETE: {key}")
            return result > 0
        
        except Exception as e:
            logger.warning(f"Cache delete error for {key}: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching pattern.
        
        Args:
            pattern: Redis key pattern (e.g., "analytics:*")
        
        Returns:
            Number of keys deleted
        """
        if not self.enabled:
            return 0
        
        try:
            redis_pattern = self._make_key(pattern)
            keys = self.redis.keys(redis_pattern)
            
            if keys:
                count = self.redis.delete(*keys)
                logger.info(f"Cache INVALIDATE: {pattern} ({count} keys)")
                return count
            
            return 0
        
        except Exception as e:
            logger.warning(f"Cache invalidate error for {pattern}: {e}")
            return 0
    
    def cached(self, ttl: Optional[int] = None, key_func: Optional[Callable] = None):
        """
        Decorator for caching function results.
        
        Args:
            ttl: Custom TTL for cached results (optional)
            key_func: Custom function to generate cache key from args/kwargs
        
        Usage:
            @query_cache.cached(ttl=60)
            def get_analytics(business_id: int, date: str):
                return expensive_query(business_id, date)
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    # Default: hash function name + args + kwargs
                    key_data = {
                        "func": func.__name__,
                        "args": args,
                        "kwargs": kwargs
                    }
                    cache_key = self._hash_key(key_data)
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl=ttl)
                
                return result
            
            return wrapper
        return decorator


# Global query cache instances for different use cases

# Analytics cache: 5 minutes (frequently updated)
analytics_cache = QueryCache(ttl=300, prefix="analytics_cache")

# Dashboard cache: 1 minute (real-time data)
dashboard_cache = QueryCache(ttl=60, prefix="dashboard_cache")

# Strategy cache: 15 minutes (rarely changes)
strategy_cache = QueryCache(ttl=900, prefix="strategy_cache")

# Published posts cache: 10 minutes (historical data)
posts_cache = QueryCache(ttl=600, prefix="posts_cache")


# Example usage functions

def cache_analytics_summary(business_id: int, date: str):
    """
    Cache key generator for analytics summary.
    
    Usage:
        @analytics_cache.cached(key_func=cache_analytics_summary)
        def get_analytics_summary(business_id: int, date: str):
            # Expensive query...
    """
    return f"summary:{business_id}:{date}"


def invalidate_business_cache(business_id: int):
    """
    Invalidate all cached data for a business.
    
    Useful when:
    - Publishing new content
    - Syncing analytics
    - Updating strategies
    """
    patterns = [
        f"analytics_cache:*:{business_id}:*",
        f"dashboard_cache:*:{business_id}:*",
        f"posts_cache:*:{business_id}:*"
    ]
    
    total_deleted = 0
    for pattern in patterns:
        total_deleted += analytics_cache.invalidate_pattern(pattern)
    
    logger.info(f"Invalidated {total_deleted} cache keys for business {business_id}")
    return total_deleted


def invalidate_all_analytics():
    """
    Invalidate all analytics cache.
    
    Useful after bulk analytics sync.
    """
    return analytics_cache.invalidate_pattern("*")


# Example: Cached query function
@analytics_cache.cached(ttl=300)
def get_cached_analytics_summary(business_id: int, start_date: str, end_date: str):
    """
    Example of a cached analytics query.
    
    This would normally query the database, but results are cached for 5 minutes.
    """
    from app.db.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Expensive query example
        # result = db.query(AnalyticsSummary).filter(...).all()
        # return [r.to_dict() for r in result]
        
        # Placeholder
        return {
            "business_id": business_id,
            "start_date": start_date,
            "end_date": end_date,
            "cached_at": datetime.utcnow().isoformat()
        }
    finally:
        db.close()
