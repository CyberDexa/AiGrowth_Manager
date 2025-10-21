"""
Database migration script to add content library columns
Run this on Render or locally to update the database schema
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db.database import engine, get_db
from app.core.config import settings

def run_migration():
    """Add content library columns to content and published_posts tables"""
    
    print("🔧 Starting database migration...")
    print(f"📍 Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'local'}")
    
    migration_sql = """
    -- CONTENT TABLE
    -- Add saved_to_library column
    ALTER TABLE content 
    ADD COLUMN IF NOT EXISTS saved_to_library BOOLEAN NOT NULL DEFAULT FALSE;
    
    -- Add index on saved_to_library for performance
    CREATE INDEX IF NOT EXISTS ix_content_saved_to_library ON content(saved_to_library);
    
    -- Add library_saved_at column
    ALTER TABLE content 
    ADD COLUMN IF NOT EXISTS library_saved_at TIMESTAMP;
    
    -- Update existing records
    UPDATE content 
    SET saved_to_library = FALSE 
    WHERE saved_to_library IS NULL;
    
    -- PUBLISHED_POSTS TABLE
    -- Add saved_to_library column
    ALTER TABLE published_posts 
    ADD COLUMN IF NOT EXISTS saved_to_library BOOLEAN NOT NULL DEFAULT FALSE;
    
    -- Add index on saved_to_library for performance
    CREATE INDEX IF NOT EXISTS ix_published_posts_saved_to_library ON published_posts(saved_to_library);
    
    -- Add library_saved_at column
    ALTER TABLE published_posts 
    ADD COLUMN IF NOT EXISTS library_saved_at TIMESTAMP;
    
    -- Update existing records
    UPDATE published_posts 
    SET saved_to_library = FALSE 
    WHERE saved_to_library IS NULL;
    """
    
    try:
        with engine.begin() as connection:
            # Execute migration
            for statement in migration_sql.split(';'):
                statement = statement.strip()
                if statement:
                    print(f"Executing: {statement[:60]}...")
                    connection.execute(text(statement))
            
            print("✅ Migration completed successfully!")
            
            # Verify columns exist in both tables
            verification_sql = """
            SELECT table_name, column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name IN ('content', 'published_posts')
              AND column_name IN ('saved_to_library', 'library_saved_at')
            ORDER BY table_name, ordinal_position;
            """
            
            result = connection.execute(text(verification_sql))
            columns = result.fetchall()
            
            print("\n📊 Verification - Columns added:")
            current_table = None
            for col in columns:
                if col[0] != current_table:
                    current_table = col[0]
                    print(f"\n  {current_table}:")
                print(f"    - {col[1]}: {col[2]} (nullable: {col[3]}, default: {col[4]})")
            
            if len(columns) == 4:  # 2 columns x 2 tables
                print("\n✅ All columns verified successfully in both tables!")
                return True
            else:
                print(f"\n⚠️  Warning: Expected 4 columns (2 per table), found {len(columns)}")
                return False
                
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        print("\nIf this is a duplicate column error, the columns may already exist.")
        print("You can safely ignore this error and verify columns exist.")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Add Content Library Columns")
    print("=" * 60)
    print()
    
    success = run_migration()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("⚠️  Migration completed with warnings. Please verify manually.")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
