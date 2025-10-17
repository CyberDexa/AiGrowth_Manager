"""
Rate Limiting Configuration

Implements rate limiting for API endpoints using SlowAPI with Redis backend.
Protects against abuse and ensures fair API usage.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
import logging

logger = logging.getLogger(__name__)

# Try to use Redis for distributed rate limiting
try:
    from app.core.redis_client import get_redis_client
    redis_client = get_redis_client()
    REDIS_AVAILABLE = True
    logger.info("✅ Rate limiter using Redis for distributed tracking")
except Exception as e:
    logger.warning(f"⚠️  Redis not available for rate limiting, using in-memory: {e}")
    redis_client = None
    REDIS_AVAILABLE = False


def get_user_identifier(request: Request) -> str:
    """
    Get unique identifier for rate limiting.
    
    Priority order:
    1. User ID from auth (if authenticated)
    2. IP address (for unauthenticated requests)
    
    Args:
        request: FastAPI request object
        
    Returns:
        Unique identifier string
    """
    # Try to get user_id from request state (set by auth middleware)
    user_id = getattr(request.state, 'user_id', None)
    
    if user_id:
        return f"user:{user_id}"
    
    # Fallback to IP address
    return f"ip:{get_remote_address(request)}"


# Initialize limiter
if REDIS_AVAILABLE:
    # Use Redis for distributed rate limiting
    limiter = Limiter(
        key_func=get_user_identifier,
        storage_uri=f"redis://{redis_client.connection_pool.connection_kwargs.get('host', 'localhost')}:"
                   f"{redis_client.connection_pool.connection_kwargs.get('port', 6379)}/1",  # Use DB 1 for rate limits
        strategy="fixed-window",  # or "moving-window" for more accuracy
        headers_enabled=True,  # Add X-RateLimit-* headers to responses
    )
else:
    # Use in-memory storage (not recommended for production with multiple workers)
    limiter = Limiter(
        key_func=get_user_identifier,
        strategy="fixed-window",
        headers_enabled=True,
    )


# Rate limit configurations by endpoint category
class RateLimits:
    """Rate limit definitions for different endpoint categories"""
    
    # OAuth endpoints - prevent brute force attacks
    OAUTH_INITIATE = "10/minute"  # 10 OAuth flows per minute per user
    OAUTH_CALLBACK = "20/minute"  # 20 callbacks per minute (allow retries)
    OAUTH_REFRESH = "30/minute"   # 30 token refreshes per minute
    
    # Publishing endpoints - prevent spam
    PUBLISH_NOW = "20/hour"       # 20 posts per hour per user
    PUBLISH_MULTI = "10/hour"     # 10 multi-platform publishes per hour
    SCHEDULE_POST = "50/hour"     # 50 scheduled posts per hour
    
    # Analytics endpoints - allow frequent polling
    ANALYTICS_READ = "100/minute" # 100 analytics reads per minute
    ANALYTICS_SYNC = "20/minute"  # 20 sync requests per minute
    
    # Content generation - expensive AI operations
    CONTENT_GENERATE = "30/hour"  # 30 AI generations per hour
    CONTENT_IMAGES = "20/hour"    # 20 image generations per hour
    
    # General API
    DEFAULT = "60/minute"         # Default: 60 requests per minute


# Pre-configured decorators for common limits
def rate_limit_oauth():
    """Decorator for OAuth endpoints"""
    return limiter.limit(RateLimits.OAUTH_INITIATE)


def rate_limit_publishing():
    """Decorator for publishing endpoints"""
    return limiter.limit(RateLimits.PUBLISH_NOW)


def rate_limit_analytics():
    """Decorator for analytics endpoints"""
    return limiter.limit(RateLimits.ANALYTICS_READ)


def rate_limit_content():
    """Decorator for content generation endpoints"""
    return limiter.limit(RateLimits.CONTENT_GENERATE)


# Custom rate limit with dynamic limits based on user tier
def get_user_tier_limit(request: Request) -> str:
    """
    Get rate limit based on user subscription tier.
    
    Future enhancement: Check user's subscription plan and return different limits.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Rate limit string (e.g., "100/hour")
    """
    # TODO: Implement tier-based limits
    # user_tier = get_user_tier_from_db(request.state.user_id)
    # 
    # if user_tier == "premium":
    #     return "200/hour"
    # elif user_tier == "pro":
    #     return "100/hour"
    # else:
    #     return "50/hour"
    
    return RateLimits.DEFAULT


# Error messages
class RateLimitMessages:
    """User-friendly rate limit error messages"""
    
    OAUTH = "Too many OAuth attempts. Please wait a minute before trying again."
    PUBLISHING = "Publishing rate limit exceeded. Please wait before posting again."
    ANALYTICS = "Too many analytics requests. Please slow down."
    CONTENT = "Content generation limit reached. Please try again later."
    DEFAULT = "Rate limit exceeded. Please try again later."


def get_rate_limit_message(limit_type: str = "default") -> str:
    """
    Get user-friendly error message for rate limit.
    
    Args:
        limit_type: Type of rate limit ("oauth", "publishing", etc.)
        
    Returns:
        User-friendly error message
    """
    messages = {
        "oauth": RateLimitMessages.OAUTH,
        "publishing": RateLimitMessages.PUBLISHING,
        "analytics": RateLimitMessages.ANALYTICS,
        "content": RateLimitMessages.CONTENT,
    }
    
    return messages.get(limit_type, RateLimitMessages.DEFAULT)


# Export commonly used items
__all__ = [
    'limiter',
    'RateLimits',
    'rate_limit_oauth',
    'rate_limit_publishing',
    'rate_limit_analytics',
    'rate_limit_content',
    'get_rate_limit_message',
]
