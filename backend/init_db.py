"""
Database initialization script - creates all tables
Run this before starting the application
"""
import asyncio
from app.db.database import Base, engine
from app.models import User, Business, Strategy, Content, SocialAccount

def init_db():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    init_db()
