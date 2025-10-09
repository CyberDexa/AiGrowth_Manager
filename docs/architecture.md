# 🏗️ System Architecture - AI Growth Manager

*High-level architecture and system design*

**Last Updated**: October 9, 2025
**Status**: Planning Phase

---

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER DEVICES                             │
│              (Web Browser - Desktop/Mobile)                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTPS
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    FRONTEND LAYER                                │
│                  (Vercel - Global CDN)                           │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Next.js 14 (App Router) + React + TypeScript           │  │
│  │  - shadcn/ui components + TailwindCSS                    │  │
│  │  - Clerk (Authentication UI)                             │  │
│  │  - React Query (State & API caching)                     │  │
│  │  - PostHog (Analytics & Feature flags)                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ REST API / tRPC
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    BACKEND LAYER                                 │
│                 (Railway - us-west-1)                            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FastAPI (Python 3.11+)                                   │  │
│  │  - Uvicorn (ASGI server)                                 │  │
│  │  - SQLAlchemy ORM                                        │  │
│  │  - Alembic (Migrations)                                  │  │
│  │  - Pydantic (Validation)                                 │  │
│  │  - JWT token verification (Clerk)                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Background Jobs (Celery)                                 │  │
│  │  - Celery workers                                        │  │
│  │  - Celery Beat (Scheduler)                               │  │
│  │  - Redis as message broker                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└──┬────────┬─────────┬─────────┬────────────┬──────────────────┘
   │        │         │         │            │
   │        │         │         │            │
┌──▼──┐  ┌─▼───┐  ┌──▼──┐   ┌──▼────┐   ┌──▼─────────────────┐
│ DB  │  │Cache│  │ AI  │   │Social │   │External Services   │
│Layer│  │Layer│  │Layer│   │APIs   │   │(Stripe, Clerk)     │
└─────┘  └─────┘  └─────┘   └───────┘   └────────────────────┘
```

---

## 🗄️ Database Layer

### PostgreSQL (Primary Database)
**Hosted on**: Railway
**Version**: PostgreSQL 15+

#### Schema Design

```sql
-- Users (synced from Clerk via webhooks)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clerk_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    stripe_customer_id VARCHAR(255),
    plan VARCHAR(50) DEFAULT 'free',  -- free, pro, enterprise
    onboarding_completed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Business/Project descriptions
CREATE TABLE businesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    industry VARCHAR(100),
    target_audience TEXT,
    goals JSONB,  -- {followers: 1000, conversions: 100}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI-generated strategies
CREATE TABLE strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    strategy_text TEXT NOT NULL,
    content_pillars JSONB,
    platforms JSONB,  -- ["linkedin", "twitter", "meta"]
    posting_frequency JSONB,  -- {linkedin: 3, twitter: 5}
    tone_voice VARCHAR(100),
    version INT DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Generated content
CREATE TABLE content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id UUID REFERENCES strategies(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,  -- linkedin, twitter, instagram, facebook
    content_type VARCHAR(50),  -- post, thread, article
    text TEXT NOT NULL,
    media_urls JSONB,  -- ["https://..."]
    hashtags JSONB,
    status VARCHAR(50) DEFAULT 'draft',  -- draft, scheduled, published, failed
    scheduled_for TIMESTAMP,
    published_at TIMESTAMP,
    external_post_id VARCHAR(255),  -- ID from social platform
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Social media account connections
CREATE TABLE social_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    account_id VARCHAR(255),  -- Platform's account ID
    account_name VARCHAR(255),
    access_token TEXT NOT NULL,  -- Encrypted
    refresh_token TEXT,  -- Encrypted
    token_expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, platform, account_id)
);

-- Analytics (cached from social platforms)
CREATE TABLE analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES content(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    impressions INT DEFAULT 0,
    likes INT DEFAULT 0,
    comments INT DEFAULT 0,
    shares INT DEFAULT 0,
    clicks INT DEFAULT 0,
    engagement_rate DECIMAL(5,2),
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subscriptions (synced from Stripe)
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    plan VARCHAR(50) NOT NULL,
    status VARCHAR(50),  -- active, trialing, past_due, canceled
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    cancel_at_period_end BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Usage tracking (for limits and analytics)
CREATE TABLE usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,  -- content_generated, content_scheduled, etc.
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_clerk_id ON users(clerk_id);
CREATE INDEX idx_users_stripe_customer_id ON users(stripe_customer_id);
CREATE INDEX idx_content_user_id ON content(user_id);
CREATE INDEX idx_content_status ON content(status);
CREATE INDEX idx_content_scheduled_for ON content(scheduled_for);
CREATE INDEX idx_social_accounts_user_id ON social_accounts(user_id);
CREATE INDEX idx_analytics_content_id ON analytics(content_id);
```

### Redis (Cache + Message Broker)
**Hosted on**: Railway
**Version**: Redis 7+

#### Use Cases
1. **Session caching** - Clerk session validation
2. **API response caching** - AI-generated content (24h TTL)
3. **Rate limiting** - Per-user API limits
4. **Celery message broker** - Job queue
5. **Celery result backend** - Task results

```python
# Cache structure examples
CACHE_KEYS = {
    "user_session": "session:{clerk_id}",  # TTL: 1 hour
    "ai_response": "ai:{business_id}:{prompt_hash}",  # TTL: 24 hours
    "rate_limit": "rate_limit:{user_id}:{endpoint}",  # TTL: 1 minute
    "social_token": "social:{user_id}:{platform}",  # TTL: token expiry
}
```

---

## 🤖 AI Layer

### LangChain Pipeline

```python
# Strategy Generation Pipeline
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

# 1. Strategy Generation
strategy_prompt = PromptTemplate(
    input_variables=["business_description", "goals", "audience"],
    template="""
    You are an expert marketing strategist. Create a comprehensive marketing 
    strategy for the following business:
    
    Business: {business_description}
    Goals: {goals}
    Target Audience: {audience}
    
    Provide:
    1. Target platforms and why
    2. Content pillars (3-5 themes)
    3. Posting frequency per platform
    4. Tone and voice guidelines
    5. KPIs to track
    """
)

# 2. Content Generation
content_prompt = PromptTemplate(
    input_variables=["strategy", "platform", "content_pillar"],
    template="""
    Based on this marketing strategy:
    {strategy}
    
    Generate a {platform} post about: {content_pillar}
    
    Requirements:
    - Engaging hook
    - Value-driven content
    - Clear CTA
    - Appropriate hashtags
    - Platform-specific formatting
    """
)

# 3. Content Optimization
optimization_prompt = PromptTemplate(
    input_variables=["content", "platform", "feedback"],
    template="""
    Optimize this {platform} post based on feedback:
    
    Original: {content}
    Feedback: {feedback}
    
    Provide improved version.
    """
)
```

### Cost Optimization
- Use `gpt-4o-mini` for content generation ($0.60/1M tokens output)
- Use `gpt-4o` for strategy (higher quality, infrequent)
- Cache responses for 24 hours
- Batch content generation (generate 7-30 posts at once)

---

## ⚙️ Background Jobs (Celery)

### Job Types

```python
# 1. Scheduled Content Publishing
@celery.task
def publish_content(content_id: str):
    """
    Publishes scheduled content to social media platforms.
    Runs every minute to check for content ready to publish.
    """
    content = get_content_by_id(content_id)
    
    if content.scheduled_for <= datetime.utcnow():
        # Publish to platform
        result = social_api_client.post(
            platform=content.platform,
            text=content.text,
            media_urls=content.media_urls
        )
        
        # Update content status
        update_content_status(
            content_id, 
            status='published',
            external_post_id=result.post_id
        )

# 2. Analytics Fetching
@celery.task
def fetch_analytics(content_id: str):
    """
    Fetches analytics for published content.
    Runs daily for all published content from last 30 days.
    """
    content = get_content_by_id(content_id)
    
    metrics = social_api_client.get_metrics(
        platform=content.platform,
        post_id=content.external_post_id
    )
    
    save_analytics(content_id, metrics)

# 3. Token Refresh
@celery.task
def refresh_social_tokens():
    """
    Refreshes expiring social media access tokens.
    Runs every 6 hours.
    """
    accounts = get_expiring_tokens(within_hours=12)
    
    for account in accounts:
        new_token = social_api_client.refresh_token(
            platform=account.platform,
            refresh_token=account.refresh_token
        )
        update_access_token(account.id, new_token)

# Celery Beat Schedule
from celery.schedules import crontab

app.conf.beat_schedule = {
    'publish-content': {
        'task': 'tasks.publish_content',
        'schedule': 60.0,  # Every minute
    },
    'fetch-analytics': {
        'task': 'tasks.fetch_analytics',
        'schedule': crontab(hour=3, minute=0),  # 3 AM daily
    },
    'refresh-tokens': {
        'task': 'tasks.refresh_social_tokens',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
    },
}
```

---

## 🔐 Security Architecture

### Authentication Flow
```
1. User signs up/logs in via Clerk (frontend)
2. Clerk issues JWT session token
3. Frontend includes token in Authorization header
4. Backend verifies token with Clerk API
5. Backend fetches user from DB using clerk_id
6. Request proceeds with authenticated user context
```

### Token Storage
- **Frontend**: Clerk handles token storage (httpOnly cookies)
- **Backend**: No token storage (stateless verification)
- **Social tokens**: Encrypted in database using Fernet

```python
from cryptography.fernet import Fernet

# Encrypt tokens before storing
def encrypt_token(token: str) -> str:
    f = Fernet(ENCRYPTION_KEY)
    return f.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    f = Fernet(ENCRYPTION_KEY)
    return f.decrypt(encrypted_token.encode()).decode()
```

### Environment Variables
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379
CLERK_SECRET_KEY=sk_test_xxxxx
STRIPE_SECRET_KEY=sk_test_xxxxx
OPENROUTER_API_KEY=sk-or-xxxxx
ENCRYPTION_KEY=xxxxx
META_APP_ID=xxxxx
META_APP_SECRET=xxxxx
TWITTER_CLIENT_ID=xxxxx
TWITTER_CLIENT_SECRET=xxxxx
LINKEDIN_CLIENT_ID=xxxxx
LINKEDIN_CLIENT_SECRET=xxxxx

# Frontend (.env.local)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxx
NEXT_PUBLIC_POSTHOG_KEY=phc_xxxxx
NEXT_PUBLIC_API_URL=https://api.aigrowth.app
```

---

## 📡 API Design

### REST API Structure
```
/api/v1
├── /auth
│   ├── GET /me - Get current user
│   └── POST /webhook/clerk - Clerk webhook
│
├── /businesses
│   ├── GET / - List user's businesses
│   ├── POST / - Create business
│   ├── GET /:id - Get business
│   └── PUT /:id - Update business
│
├── /strategies
│   ├── POST /generate - Generate strategy
│   ├── GET /:business_id - Get strategy
│   └── PUT /:id - Update strategy
│
├── /content
│   ├── POST /generate - Generate content
│   ├── GET / - List content (filter by status, platform)
│   ├── GET /:id - Get content
│   ├── PUT /:id - Update content
│   ├── POST /:id/schedule - Schedule content
│   └── DELETE /:id - Delete content
│
├── /social
│   ├── GET /accounts - List connected accounts
│   ├── POST /connect/:platform - Initiate OAuth
│   ├── GET /callback/:platform - OAuth callback
│   └── DELETE /accounts/:id - Disconnect account
│
├── /analytics
│   ├── GET /overview - Dashboard overview
│   ├── GET /content/:id - Content-specific analytics
│   └── GET /export - Export analytics data
│
├── /billing
│   ├── GET /subscription - Get subscription status
│   ├── POST /checkout - Create Stripe checkout session
│   ├── POST /portal - Create customer portal session
│   └── POST /webhook/stripe - Stripe webhook
│
└── /admin (future)
    ├── GET /users - List all users
    └── GET /stats - Platform statistics
```

---

## 🚀 Deployment Architecture

### Development Environment
```yaml
# docker-compose.yml for local development
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/aigrowth
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  celery_worker:
    build: ./backend
    command: celery -A app.celery worker --loglevel=info
    depends_on:
      - redis
      - db

  celery_beat:
    build: ./backend
    command: celery -A app.celery beat --loglevel=info
    depends_on:
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: aigrowth
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Production Deployment

#### Frontend (Vercel)
```json
// vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY": "@clerk_publishable_key",
    "NEXT_PUBLIC_API_URL": "https://api.aigrowth.app"
  }
}
```

#### Backend (Railway)
```toml
# railway.toml
[build]
builder = "NIXPACKS"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 300

[[services]]
name = "backend"

[[services]]
name = "celery-worker"
startCommand = "celery -A app.celery worker --loglevel=info"

[[services]]
name = "celery-beat"
startCommand = "celery -A app.celery beat --loglevel=info"
```

---

## 📊 Monitoring & Observability

### Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": check_db_connection(),
        "redis": check_redis_connection(),
        "celery": check_celery_workers(),
        "timestamp": datetime.utcnow()
    }
```

### Error Tracking (Sentry)
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://xxxxx@sentry.io/xxxxx",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment="production"
)
```

### Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Log important events
logger.info(f"Content published: {content_id}")
logger.error(f"Failed to publish: {error}")
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: vercel/actions/deploy@v1
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: |
          railway deploy
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

---

## ✅ Architecture Decision Records (ADRs)

### ADR-001: Why FastAPI over Django?
**Decision**: Use FastAPI for backend
**Reasoning**:
- Async support crucial for AI API calls
- Lightweight and fast
- Better for microservices if we scale
- Auto-generated API docs

### ADR-002: Why PostgreSQL over MongoDB?
**Decision**: Use PostgreSQL as primary database
**Reasoning**:
- Structured data (users, subscriptions, content)
- Strong ACID guarantees for billing
- Better for analytics queries
- Can add JSONB for flexibility

### ADR-003: Why Celery over Cloud Functions?
**Decision**: Use Celery for background jobs
**Reasoning**:
- More control over scheduling
- Cheaper than cloud functions at scale
- Better for long-running tasks
- Easy to monitor and debug

---

*This architecture will evolve as we build and scale the platform.*
