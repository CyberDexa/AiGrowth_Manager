"""Pytest configuration and fixtures."""

import pytest
from sqlalchemy import create_engine, event, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from faker import Faker
from datetime import datetime, timedelta
import sys
import os
import json

# Add app directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import Base
from app.models.business import Business
from app.models.user import User
from app.models.social_account import SocialAccount
from app.models.published_post import PublishedPost

fake = Faker()


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_db():
    """
    Create a fresh test database for each test function.
    Uses in-memory SQLite database for speed.
    
    Note: Modifies ARRAY columns to use Text type for SQLite compatibility.
    """
    from sqlalchemy import Text, Column
    
    # Replace ARRAY columns with Text in the table definition
    for column in PublishedPost.__table__.columns:
        if column.name in ('content_images', 'content_links'):
            column.type = Text()
    
    # Create in-memory SQLite database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)


# ============================================================================
# Model Fixtures
# ============================================================================

@pytest.fixture
def test_user(test_db):
    """Create a test user."""
    user = User(
        clerk_id=f"user_{fake.uuid4()}",
        email=fake.email(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_business(test_db, test_user):
    """Create a test business."""
    business = Business(
        user_id=test_user.clerk_id,
        name=fake.company(),
        description=fake.text(max_nb_chars=200),
        target_audience=fake.text(max_nb_chars=100),
        marketing_goals=fake.text(max_nb_chars=100),
        industry=fake.bs(),
        company_size="1-10"
    )
    test_db.add(business)
    test_db.commit()
    test_db.refresh(business)
    return business


@pytest.fixture
def test_social_account_linkedin(test_db, test_business):
    """Create a test LinkedIn social account."""
    account = SocialAccount(
        business_id=test_business.id,
        platform="linkedin",
        platform_user_id=f"linkedin_{fake.uuid4()}",
        platform_username=fake.user_name(),
        access_token=f"test_linkedin_token_{fake.uuid4()}",
        refresh_token=None,
        token_expires_at=datetime.utcnow() + timedelta(days=30),
        page_id=f"urn:li:organization:{fake.random_number(digits=8)}",
        is_active=True
    )
    test_db.add(account)
    test_db.commit()
    test_db.refresh(account)
    return account


@pytest.fixture
def test_social_account_twitter(test_db, test_business):
    """Create a test Twitter social account."""
    account = SocialAccount(
        business_id=test_business.id,
        platform="twitter",
        platform_user_id=f"twitter_{fake.random_number(digits=15)}",
        platform_username=fake.user_name(),
        access_token=f"test_twitter_token_{fake.uuid4()}",
        refresh_token=f"test_twitter_refresh_{fake.uuid4()}",
        token_expires_at=datetime.utcnow() + timedelta(hours=2),
        is_active=True
    )
    test_db.add(account)
    test_db.commit()
    test_db.refresh(account)
    return account


@pytest.fixture
def test_social_account_facebook(test_db, test_business):
    """Create a test Facebook social account."""
    account = SocialAccount(
        business_id=test_business.id,
        platform="facebook",
        platform_user_id=f"facebook_{fake.random_number(digits=12)}",
        platform_username=fake.user_name(),
        access_token=f"test_facebook_token_{fake.uuid4()}",
        page_id=str(fake.random_number(digits=15)),
        page_name=fake.company(),
        page_access_token=f"test_page_token_{fake.uuid4()}",
        instagram_account_id=str(fake.random_number(digits=12)),
        instagram_username=fake.user_name(),
        is_active=True
    )
    test_db.add(account)
    test_db.commit()
    test_db.refresh(account)
    return account


@pytest.fixture
def test_published_posts(test_db, test_business, test_social_account_linkedin):
    """Create test published posts."""
    posts = []
    
    for i in range(5):
        post = PublishedPost(
            business_id=test_business.id,
            social_account_id=test_social_account_linkedin.id,
            content_text=fake.paragraph(nb_sentences=3),
            platform="linkedin",
            platform_post_id=f"urn:li:share:{fake.random_number(digits=10)}",
            platform_post_url=fake.url(),
            status="published",
            published_at=datetime.utcnow() - timedelta(days=i),
            likes_count=fake.random_int(min=10, max=500),
            comments_count=fake.random_int(min=5, max=100),
            shares_count=fake.random_int(min=1, max=50),
            impressions_count=fake.random_int(min=500, max=5000)
        )
        test_db.add(post)
        posts.append(post)
    
    test_db.commit()
    for post in posts:
        test_db.refresh(post)
    
    return posts


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_linkedin_api_response():
    """Mock LinkedIn API response."""
    return {
        "elements": [{
            "totalShareStatistics": {
                "likeCount": 150,
                "commentCount": 25,
                "shareCount": 12,
                "impressionCount": 5500,
                "clickCount": 80,
                "uniqueImpressionsCount": 4800,
                "engagement": 187
            }
        }]
    }


@pytest.fixture
def mock_twitter_api_response():
    """Mock Twitter API response."""
    return {
        "data": {
            "id": "1234567890123456789",
            "text": "Test tweet content",
            "created_at": "2025-10-01T12:00:00.000Z",
            "public_metrics": {
                "like_count": 200,
                "reply_count": 30,
                "retweet_count": 45,
                "quote_count": 8,
                "bookmark_count": 15
            },
            "non_public_metrics": {
                "impression_count": 12000,
                "url_link_clicks": 150,
                "user_profile_clicks": 25
            }
        }
    }


@pytest.fixture
def mock_facebook_api_response():
    """Mock Facebook API response."""
    return {
        "id": "123456789_987654321",
        "created_time": "2025-10-01T12:00:00+0000",
        "message": "Test Facebook post",
        "reactions": {
            "summary": {
                "total_count": 300
            }
        },
        "comments": {
            "summary": {
                "total_count": 50
            }
        },
        "shares": {
            "count": 20
        },
        "permalink_url": "https://facebook.com/..."
    }


@pytest.fixture
def mock_facebook_insights_response():
    """Mock Facebook insights API response."""
    return {
        "data": [
            {"name": "post_impressions", "values": [{"value": 8000}]},
            {"name": "post_impressions_unique", "values": [{"value": 6500}]},
            {"name": "post_engaged_users", "values": [{"value": 370}]},
            {"name": "post_clicks", "values": [{"value": 120}]},
            {"name": "post_video_views", "values": [{"value": 0}]}
        ]
    }


@pytest.fixture
def mock_instagram_api_response():
    """Mock Instagram API response."""
    return {
        "id": "123456789",
        "media_type": "IMAGE",
        "media_url": "https://instagram.com/...",
        "permalink": "https://instagram.com/p/...",
        "timestamp": "2025-10-01T12:00:00+0000",
        "like_count": 450,
        "comments_count": 35,
        "caption": "Test Instagram post"
    }


@pytest.fixture
def mock_instagram_insights_response():
    """Mock Instagram insights API response."""
    return {
        "data": [
            {"name": "impressions", "values": [{"value": 9500}]},
            {"name": "reach", "values": [{"value": 8200}]},
            {"name": "engagement", "values": [{"value": 485}]},
            {"name": "saved", "values": [{"value": 25}]},
            {"name": "video_views", "values": [{"value": 0}]}
        ]
    }


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        "linkedin": {
            "client_id": "test_linkedin_client_id",
            "client_secret": "test_linkedin_client_secret",
            "redirect_uri": "http://localhost:8003/oauth/linkedin/callback"
        },
        "twitter": {
            "api_key": "test_twitter_api_key",
            "api_secret": "test_twitter_api_secret",
            "bearer_token": "test_twitter_bearer_token",
            "redirect_uri": "http://localhost:8003/oauth/twitter/callback"
        },
        "meta": {
            "app_id": "test_meta_app_id",
            "app_secret": "test_meta_app_secret",
            "redirect_uri": "http://localhost:8003/oauth/meta/callback"
        }
    }
