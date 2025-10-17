from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Growth Manager"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "https://localhost:3000",
    ]
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@127.0.0.1:5432/ai_growth_manager"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Clerk
    CLERK_SECRET_KEY: str = ""
    CLERK_WEBHOOK_SECRET: str = ""
    CLERK_DOMAIN: str = "romantic-lemming-17.clerk.accounts.dev"
    
    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # AI
    OPENROUTER_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # Image Storage (Cloudinary)
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    
    # Social Media
    META_APP_ID: str = ""
    META_APP_SECRET: str = ""
    META_REDIRECT_URI: str = "http://localhost:8003/api/v1/social/meta/callback"
    
    TWITTER_CLIENT_ID: str = ""
    TWITTER_CLIENT_SECRET: str = ""
    TWITTER_REDIRECT_URI: str = "http://localhost:8003/api/v1/social/twitter/callback"
    
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    LINKEDIN_REDIRECT_URI: str = "http://localhost:8003/api/v1/social/linkedin/callback"
    
    # Email
    RESEND_API_KEY: str = ""
    
    # Security
    ENCRYPTION_KEY: str = ""
    JWT_SECRET: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env


settings = Settings()
