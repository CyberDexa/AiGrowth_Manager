"""Custom exceptions for platform analytics fetchers."""


class PlatformAPIError(Exception):
    """Base exception for platform API errors."""
    
    def __init__(self, message: str, platform: str = None, status_code: int = None):
        self.message = message
        self.platform = platform
        self.status_code = status_code
        super().__init__(self.message)


class RateLimitError(PlatformAPIError):
    """Exception raised when API rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: int = None, platform: str = None):
        self.retry_after = retry_after
        super().__init__(message, platform=platform, status_code=429)


class AuthenticationError(PlatformAPIError):
    """Exception raised when authentication fails."""
    
    def __init__(self, message: str, platform: str = None):
        super().__init__(message, platform=platform, status_code=401)


class PostNotFoundError(PlatformAPIError):
    """Exception raised when a post is not found on the platform."""
    
    def __init__(self, message: str, post_id: str = None, platform: str = None):
        self.post_id = post_id
        super().__init__(message, platform=platform, status_code=404)


class InvalidTokenError(AuthenticationError):
    """Exception raised when access token is invalid or expired."""
    
    def __init__(self, message: str = "Access token is invalid or expired", platform: str = None):
        super().__init__(message, platform=platform)
