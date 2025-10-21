#!/usr/bin/env python3
"""
Auto-run database migrations on startup
This script runs when the backend starts on Render
"""
import logging
from sqlalchemy import text, inspect
from app.db.database import engine

logger = logging.getLogger(__name__)

def check_and_add_library_columns(table_name: str):
    """
    Check if library columns exist in a table, and add them if missing.
    Safe to run on every startup - only adds columns if they don't exist.
    
    Args:
        table_name: Name of the table to migrate (content or published_posts)
    """
    try:
        with engine.begin() as connection:
            # Check if columns exist
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns(table_name)]
            
            needs_migration = False
            
            if 'saved_to_library' not in columns:
                logger.info(f"Adding saved_to_library column to {table_name} table...")
                connection.execute(text(f"""
                    ALTER TABLE {table_name} 
                    ADD COLUMN saved_to_library BOOLEAN NOT NULL DEFAULT FALSE
                """))
                connection.execute(text(f"""
                    CREATE INDEX ix_{table_name}_saved_to_library ON {table_name}(saved_to_library)
                """))
                needs_migration = True
                logger.info(f"✅ Added saved_to_library column to {table_name}")
            
            if 'library_saved_at' not in columns:
                logger.info(f"Adding library_saved_at column to {table_name} table...")
                connection.execute(text(f"""
                    ALTER TABLE {table_name} 
                    ADD COLUMN library_saved_at TIMESTAMP
                """))
                needs_migration = True
                logger.info(f"✅ Added library_saved_at column to {table_name}")
            
            if needs_migration:
                logger.info(f"✅ Library columns migration completed for {table_name}")
            else:
                logger.info(f"✓ Library columns already exist in {table_name}, skipping migration")
                
            return True
            
    except Exception as e:
        logger.error(f"Migration error for {table_name}: {str(e)}", exc_info=True)
        # Don't crash the app if migration fails
        # This allows the app to start even if there's a migration issue
        return False

def check_and_add_content_library_columns():
    """
    Check if content and published_posts library columns exist, and add them if missing.
    Safe to run on every startup - only adds columns if they don't exist.
    """
    success = True
    
    # Migrate content table
    logger.info("Checking content table...")
    success = check_and_add_library_columns('content') and success
    
    # Migrate published_posts table
    logger.info("Checking published_posts table...")
    success = check_and_add_library_columns('published_posts') and success
    
    return success

def run_startup_migrations():
    """Run all startup migrations"""
    logger.info("🔧 Running startup database migrations...")
    
    success = check_and_add_content_library_columns()
    
    if success:
        logger.info("✅ All startup migrations completed")
    else:
        logger.warning("⚠️  Some migrations failed, check logs")
    
    return success
