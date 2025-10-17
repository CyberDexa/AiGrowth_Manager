"""
Database session management and base model
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings

# Create database engine with optimized connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    # Connection pool settings
    poolclass=QueuePool,  # Thread-safe connection pool
    pool_size=10,  # Base number of connections to maintain
    max_overflow=20,  # Additional connections under load (total max: 30)
    pool_timeout=30,  # Seconds to wait for available connection
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Verify connections before using
    # Performance settings
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    echo_pool=False,  # Set to True for pool debugging
    # Execution settings
    connect_args={
        "connect_timeout": 10,  # Connection timeout in seconds
        "application_name": "ai-growth-manager",  # Identify in pg_stat_activity
    }
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for getting database session
    Use in FastAPI endpoints with Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
