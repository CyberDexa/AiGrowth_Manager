"""
Structured JSON logging configuration for AI Growth Manager
"""

import logging
import sys
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from pythonjsonlogger import jsonlogger
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar

# Context variable to store request ID across async calls
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
business_id_var: ContextVar[Optional[int]] = ContextVar('business_id', default=None)


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that adds request context to all log records
    """
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """
        Add custom fields to the log record
        """
        # Add timestamp in ISO format
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add logger name (module/service name)
        log_record['service'] = record.name
        
        # Add the message
        log_record['message'] = record.getMessage()
        
        # Add request context if available
        request_id = request_id_var.get()
        if request_id:
            log_record['request_id'] = request_id
        
        user_id = user_id_var.get()
        if user_id:
            log_record['user_id'] = user_id
        
        business_id = business_id_var.get()
        if business_id:
            log_record['business_id'] = business_id
        
        # Add extra fields from message_dict
        for key, value in message_dict.items():
            if key not in log_record:
                log_record[key] = value
        
        # Add exception info if present
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add request ID and user context to all requests
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and add context
        """
        # Generate or extract request ID
        request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        request_id_var.set(request_id)
        
        # Extract user context from request state (set by auth middleware)
        if hasattr(request.state, 'user'):
            user = request.state.user
            user_id_var.set(user.get('user_id'))
        
        # Extract business_id from query params or path params
        business_id = request.query_params.get('business_id')
        if business_id:
            try:
                business_id_var.set(int(business_id))
            except (ValueError, TypeError):
                pass
        
        # Log the request
        logger = logging.getLogger('api.request')
        logger.info(
            "Incoming request",
            extra={
                'event_type': 'http_request',
                'method': request.method,
                'path': request.url.path,
                'query_params': str(request.query_params),
                'client_host': request.client.host if request.client else None,
            }
        )
        
        # Process the request
        try:
            response: Response = await call_next(request)
            
            # Log the response
            logger.info(
                "Request completed",
                extra={
                    'event_type': 'http_response',
                    'status_code': response.status_code,
                    'method': request.method,
                    'path': request.url.path,
                }
            )
            
            # Add request ID to response headers
            response.headers['X-Request-ID'] = request_id
            
            return response
        except Exception as e:
            # Log the error
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    'event_type': 'http_error',
                    'method': request.method,
                    'path': request.url.path,
                    'error': str(e),
                },
                exc_info=True
            )
            raise
        finally:
            # Clear context variables
            request_id_var.set(None)
            user_id_var.set(None)
            business_id_var.set(None)


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure JSON logging for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Create JSON formatter (don't use rename_fields as it causes KeyError)
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(service)s %(message)s'
    )
    
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    
    # Set log levels for specific loggers
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)  # Reduce uvicorn noise
    logging.getLogger('uvicorn.error').setLevel(logging.INFO)
    
    # Log configuration complete
    root_logger.info(
        "Logging configuration complete",
        extra={
            'event_type': 'logging_configured',
            'log_level': log_level,
        }
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger
    """
    return logging.getLogger(name)


# Utility functions for adding context to logs
def set_request_context(request_id: str, user_id: Optional[str] = None, business_id: Optional[int] = None) -> None:
    """
    Manually set request context (useful for background tasks)
    
    Args:
        request_id: Request ID
        user_id: User ID
        business_id: Business ID
    """
    request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)
    if business_id:
        business_id_var.set(business_id)


def clear_request_context() -> None:
    """
    Clear request context
    """
    request_id_var.set(None)
    user_id_var.set(None)
    business_id_var.set(None)


def log_event(
    logger: logging.Logger,
    event_type: str,
    message: str,
    level: str = "INFO",
    **kwargs
) -> None:
    """
    Log a structured event
    
    Args:
        logger: Logger instance
        event_type: Type of event (e.g., 'oauth_success', 'sync_complete')
        message: Human-readable message
        level: Log level
        **kwargs: Additional fields to include in the log
    """
    log_method = getattr(logger, level.lower())
    log_method(
        message,
        extra={
            'event_type': event_type,
            **kwargs
        }
    )
