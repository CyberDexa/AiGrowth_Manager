"""
Sentry integration for error tracking and performance monitoring
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from typing import Optional, Dict, Any
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def init_sentry() -> None:
    """
    Initialize Sentry SDK for error tracking and performance monitoring
    
    Configuration:
    - DSN: Sentry Data Source Name (from environment)
    - Environment: development, staging, production
    - Release: Application version for tracking deployments
    - Traces sample rate: Percentage of transactions to trace (1.0 = 100%)
    - Profiles sample rate: Percentage of transactions to profile
    """
    
    # Check if Sentry DSN is configured
    if not hasattr(settings, 'SENTRY_DSN') or not settings.SENTRY_DSN:
        logger.warning("Sentry DSN not configured - error tracking disabled")
        return
    
    # Determine sampling rates based on environment
    traces_sample_rate = 1.0 if settings.ENVIRONMENT == "development" else 0.1
    profiles_sample_rate = 1.0 if settings.ENVIRONMENT == "development" else 0.1
    
    # Initialize Sentry
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        
        # Environment and release tracking
        environment=settings.ENVIRONMENT,
        release=getattr(settings, 'VERSION', '0.1.0'),
        
        # Performance monitoring
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        
        # Integrations
        integrations=[
            # FastAPI integration for automatic request tracking
            FastApiIntegration(
                transaction_style="endpoint",  # Group by endpoint name
                failed_request_status_codes=[400, 499],  # Track client errors
            ),
            
            # SQLAlchemy integration for database query tracking
            SqlalchemyIntegration(),
            
            # HTTPX integration for external API call tracking
            HttpxIntegration(),
            
            # Logging integration (INFO and above)
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR,  # Only send ERROR logs as Sentry events
            ),
        ],
        
        # Data scrubbing - remove sensitive information
        send_default_pii=False,  # Don't send personally identifiable information
        
        # Error filtering
        before_send=before_send_handler,
        before_breadcrumb=before_breadcrumb_handler,
        
        # Performance tuning
        max_breadcrumbs=50,  # Keep last 50 breadcrumbs
        attach_stacktrace=True,  # Attach stack traces to all events
        
        # Debug mode
        debug=settings.ENVIRONMENT == "development",
    )
    
    logger.info(
        f"Sentry initialized successfully",
        extra={
            'environment': settings.ENVIRONMENT,
            'release': getattr(settings, 'VERSION', '0.1.0'),
            'traces_sample_rate': traces_sample_rate,
        }
    )


def before_send_handler(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Filter and modify events before sending to Sentry
    
    Use this to:
    - Filter out noise (e.g., specific error types)
    - Scrub sensitive data
    - Add additional context
    """
    
    # Filter out common/expected errors in development
    if settings.ENVIRONMENT == "development":
        # Don't send HTTPException errors to Sentry (they're expected)
        if 'exc_info' in hint:
            exc_type, exc_value, exc_tb = hint['exc_info']
            if exc_type.__name__ == "HTTPException":
                return None
    
    # Add custom tags
    event.setdefault('tags', {})
    event['tags']['environment'] = settings.ENVIRONMENT
    
    return event


def before_breadcrumb_handler(crumb: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Filter and modify breadcrumbs before attaching to events
    
    Breadcrumbs are trail of events leading up to an error
    """
    
    # Filter out noisy breadcrumbs
    if crumb.get('category') == 'httplib':
        # Don't log health check requests
        if '/health' in crumb.get('data', {}).get('url', ''):
            return None
    
    return crumb


def set_user_context(user_id: Optional[str] = None, business_id: Optional[int] = None) -> None:
    """
    Set user context for Sentry events
    
    Args:
        user_id: User ID (from Clerk)
        business_id: Business ID
    """
    if user_id or business_id:
        sentry_sdk.set_user({
            "id": user_id,
            "business_id": business_id,
        })


def add_breadcrumb(
    category: str,
    message: str,
    level: str = "info",
    data: Optional[Dict[str, Any]] = None
) -> None:
    """
    Manually add a breadcrumb to the current scope
    
    Args:
        category: Breadcrumb category (e.g., 'oauth', 'sync', 'api')
        message: Human-readable message
        level: Severity level (debug, info, warning, error, fatal)
        data: Additional structured data
    """
    sentry_sdk.add_breadcrumb(
        category=category,
        message=message,
        level=level,
        data=data or {}
    )


def capture_exception(error: Exception, **kwargs) -> str:
    """
    Manually capture an exception
    
    Args:
        error: Exception to capture
        **kwargs: Additional context
    
    Returns:
        Event ID
    """
    with sentry_sdk.push_scope() as scope:
        # Add additional context
        for key, value in kwargs.items():
            scope.set_context(key, value)
        
        return sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info", **kwargs) -> str:
    """
    Manually capture a message
    
    Args:
        message: Message to capture
        level: Severity level
        **kwargs: Additional context
    
    Returns:
        Event ID
    """
    with sentry_sdk.push_scope() as scope:
        # Add additional context
        for key, value in kwargs.items():
            scope.set_context(key, value)
        
        return sentry_sdk.capture_message(message, level=level)


# Context manager for tracking operations
class SentrySpan:
    """
    Context manager for tracking operations with Sentry
    
    Usage:
        with SentrySpan(op="oauth", description="LinkedIn token exchange"):
            # Your code here
            pass
    """
    
    def __init__(self, op: str, description: str):
        self.op = op
        self.description = description
        self.span = None
    
    def __enter__(self):
        transaction = sentry_sdk.Hub.current.scope.transaction
        if transaction:
            self.span = transaction.start_child(op=self.op, description=self.description)
            self.span.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            self.span.__exit__(exc_type, exc_val, exc_tb)
