"""
Redis Client Configuration

Provides a singleton Redis client for caching, state management, and rate limiting.
"""
import redis
from typing import Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Singleton Redis client for application-wide use.
    
    Used for:
    - OAuth state management (CSRF protection)
    - Rate limiting
    - Session caching
    - Celery task queue (broker)
    """
    
    _instance: Optional[redis.Redis] = None
    
    @classmethod
    def get_client(cls) -> redis.Redis:
        """
        Get or create Redis client instance.
        
        Returns:
            Redis client configured with connection pool
        """
        if cls._instance is None:
            try:
                # Parse Redis URL from settings
                redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
                
                # Create Redis client with connection pooling
                cls._instance = redis.from_url(
                    redis_url,
                    encoding="utf-8",
                    decode_responses=True,  # Automatically decode responses to strings
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                
                # Test connection
                cls._instance.ping()
                logger.info(f"✅ Redis connected successfully: {redis_url}")
                
            except redis.ConnectionError as e:
                logger.error(f"❌ Failed to connect to Redis: {e}")
                logger.warning("⚠️  Falling back to in-memory state storage (NOT RECOMMENDED FOR PRODUCTION)")
                raise
            except Exception as e:
                logger.error(f"❌ Unexpected error connecting to Redis: {e}")
                raise
        
        return cls._instance
    
    @classmethod
    def close(cls):
        """Close Redis connection (for graceful shutdown)."""
        if cls._instance:
            cls._instance.close()
            cls._instance = None
            logger.info("Redis connection closed")


# Convenience function for getting client
def get_redis_client() -> redis.Redis:
    """Get Redis client instance."""
    return RedisClient.get_client()


# Test connection on module import
try:
    redis_client = get_redis_client()
except Exception as e:
    logger.warning(f"Redis not available: {e}")
    redis_client = None
