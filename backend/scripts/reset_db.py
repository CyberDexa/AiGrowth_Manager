"""
Reset database for development
"""
from sqlalchemy import text
from app.db.database import engine

def reset_database():
    print("Checking current database state...")
    
    with engine.connect() as conn:
        # Check what tables exist
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = [row[0] for row in result]
        print(f"Existing tables: {tables}")
        
        # Reset alembic version to allow fresh migrations
        if 'alembic_version' in tables:
            print("\nResetting alembic_version table...")
            conn.execute(text("DELETE FROM alembic_version"))
            conn.commit()
            print("Alembic version table cleared")
        
        # Drop all tables except alembic_version
        for table in tables:
            if table != 'alembic_version':
                print(f"Dropping table: {table}")
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    conn.commit()
                except Exception as e:
                    print(f"  Error dropping {table}: {e}")
        
        # Drop all enums
        print("\nDropping enums...")
        result = conn.execute(text("""
            SELECT t.typname 
            FROM pg_type t 
            JOIN pg_namespace n ON n.oid = t.typnamespace 
            WHERE t.typtype = 'e' AND n.nspname = 'public'
        """))
        enums = [row[0] for row in result]
        for enum_name in enums:
            print(f"Dropping enum: {enum_name}")
            try:
                conn.execute(text(f"DROP TYPE IF EXISTS {enum_name} CASCADE"))
                conn.commit()
            except Exception as e:
                print(f"  Error dropping {enum_name}: {e}")
    
    print("\nDatabase reset complete! Now run: alembic upgrade head")

if __name__ == "__main__":
    reset_database()
