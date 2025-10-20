from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging_config import configure_logging, RequestContextMiddleware, get_logger
from app.core.sentry_config import init_sentry

# Configure structured JSON logging
configure_logging(log_level=settings.LOG_LEVEL if hasattr(settings, 'LOG_LEVEL') else "INFO")
logger = get_logger(__name__)

# Initialize Sentry for error tracking
init_sentry()

# Initialize rate limiting
try:
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from app.core.rate_limit import limiter
    RATE_LIMITING_ENABLED = True
    logger.info("✅ Rate limiting enabled")
except ImportError:
    logger.warning("⚠️  SlowAPI not installed, rate limiting disabled")
    RATE_LIMITING_ENABLED = False

app = FastAPI(
    title="AI Growth Manager API",
    description="Autonomous AI marketing system API",
    version="0.1.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
)

# Add rate limiter to app state
if RATE_LIMITING_ENABLED:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - must be added before other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers
)

# Request context middleware for logging
app.add_middleware(RequestContextMiddleware)


# Global exception handler to ensure CORS headers on errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler that ensures CORS headers are sent even on errors.
    This prevents CORS errors when the backend crashes.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )


@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    
    Initializes background services like the analytics sync scheduler.
    Runs database migrations on startup.
    """
    logger.info("Starting AI Growth Manager API...")
    
    # Run database migrations
    try:
        from app.db.migrations import run_startup_migrations
        logger.info("Running database migrations...")
        run_startup_migrations()
        logger.info("Database migrations completed")
    except Exception as e:
        logger.error(f"Failed to run database migrations: {e}", exc_info=True)
        # Don't crash the app - allow it to start even if migrations fail
    
    # Start background scheduler
    try:
        from app.scheduler import start_scheduler
        start_scheduler()
        logger.info("Background scheduler started successfully")
    except Exception as e:
        logger.error(f"Failed to start background scheduler: {e}", exc_info=True)
    
    logger.info("AI Growth Manager API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    
    Gracefully shuts down background services.
    """
    logger.info("Shutting down AI Growth Manager API...")
    
    # Shutdown background scheduler
    try:
        from app.scheduler import shutdown_scheduler
        shutdown_scheduler()
        logger.info("Background scheduler shut down successfully")
    except Exception as e:
        logger.error(f"Failed to shut down background scheduler: {e}", exc_info=True)
    
    logger.info("AI Growth Manager API shut down complete")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Growth Manager API",
        "version": "0.1.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
    }

# Include routers
from app.api import users, businesses, strategies, content, analytics, analytics_simple, social, publishing, images, scheduler, oauth, publishing_v2, content_library, content_templates, posting_insights

app.include_router(users.router, prefix="/api/v1")
app.include_router(businesses.router, prefix="/api/v1")
app.include_router(strategies.router, prefix="/api/v1/strategies", tags=["strategies"])
app.include_router(content.router, prefix="/api/v1", tags=["content"])
app.include_router(analytics.router, tags=["analytics"])
app.include_router(analytics_simple.router, tags=["analytics-simple"])
app.include_router(social.router, prefix="/api/v1", tags=["social"])
app.include_router(publishing.router, prefix="/api/v1", tags=["publishing"])  # Legacy publishing
app.include_router(publishing_v2.router, prefix="/api", tags=["publishing-v2"])  # New publishing API
app.include_router(images.router, prefix="/api/v1", tags=["images"])
app.include_router(content_library.router, prefix="/api/v1", tags=["content-library"])
app.include_router(content_templates.router, prefix="/api/v1/templates", tags=["templates"])
app.include_router(posting_insights.router, prefix="/api/v1/insights", tags=["insights"])
app.include_router(scheduler.router, tags=["scheduler"])
app.include_router(oauth.router, prefix="/api/v1", tags=["oauth"])

# Additional routers to add later:
# from app.api import billing
# app.include_router(social.router, prefix="/api/v1")
# etc...

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False
    )
