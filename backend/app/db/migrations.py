#!/usr/bin/env python3
"""
Auto-run database migrations on startup
This script runs when the backend starts on Render
"""
import logging
from sqlalchemy import text, inspect
from app.db.database import engine

logger = logging.getLogger(__name__)

def check_and_add_content_library_columns():
    """
    Check if content library columns exist, and add them if missing.
    Safe to run on every startup - only adds columns if they don't exist.
    """
    try:
        with engine.begin() as connection:
            # Check if columns exist
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('content')]
            
            needs_migration = False
            
            if 'saved_to_library' not in columns:
                logger.info("Adding saved_to_library column to content table...")
                connection.execute(text("""
                    ALTER TABLE content 
                    ADD COLUMN saved_to_library BOOLEAN NOT NULL DEFAULT FALSE
                """))
                connection.execute(text("""
                    CREATE INDEX ix_content_saved_to_library ON content(saved_to_library)
                """))
                needs_migration = True
                logger.info("✅ Added saved_to_library column")
            
            if 'library_saved_at' not in columns:
                logger.info("Adding library_saved_at column to content table...")
                connection.execute(text("""
                    ALTER TABLE content 
                    ADD COLUMN library_saved_at TIMESTAMP
                """))
                needs_migration = True
                logger.info("✅ Added library_saved_at column")
            
            if needs_migration:
                logger.info("✅ Content library migration completed successfully")
            else:
                logger.info("✓ Content library columns already exist, skipping migration")
                
            return True
            
    except Exception as e:
        logger.error(f"Migration error: {str(e)}", exc_info=True)
        # Don't crash the app if migration fails
        # This allows the app to start even if there's a migration issue
        return False

def run_startup_migrations():
    """Run all startup migrations"""
    logger.info("🔧 Running startup database migrations...")
    
    success = check_and_add_content_library_columns()
    
    if success:
        logger.info("✅ All startup migrations completed")
    else:
        logger.warning("⚠️  Some migrations failed, check logs")
    
    return success
