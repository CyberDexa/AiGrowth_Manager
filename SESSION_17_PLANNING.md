# Session 17 - Planning Document
## Publishing API, Redis Integration & Performance Enhancement

**Session Date**: October 14, 2025  
**Estimated Duration**: 6-8 hours  
**Status**: 🚀 Ready to Start  

---

## 📋 Session Overview

Session 17 focuses on completing the core publishing functionality, replacing in-memory state storage with Redis for production scalability, adding rate limiting for security, and optimizing performance. This session bridges the gap between OAuth authentication (Session 16) and actual content publishing to social platforms.

**Previous Session**: Session 16 - OAuth 2.0, Dashboard Monitoring, Observability (✅ Complete)  
**Next Session**: Session 18 - Advanced Analytics & AI Enhancements

---

## 🎯 Session Goals

### Primary Objectives
1. **Publishing API** - Create posts on LinkedIn, Twitter, and Meta using OAuth tokens
2. **Redis Integration** - Replace in-memory state storage with Redis
3. **Rate Limiting** - Protect OAuth and publishing endpoints
4. **Content Scheduling** - Queue posts for future publishing
5. **Performance Optimization** - Database indexing and query optimization

### Success Criteria
- ✅ Successfully publish posts to all 3 platforms using stored OAuth tokens
- ✅ Redis state manager operational with 10-minute TTL
- ✅ Rate limiting active on all public endpoints
- ✅ Scheduled posts working with Celery background jobs
- ✅ API response times <200ms for 95th percentile
- ✅ All features tested and documented

---

## 📊 Current State Analysis

### What's Working (From Session 16)
- ✅ OAuth 2.0 flows for LinkedIn, Twitter, Meta
- ✅ Token encryption with Fernet
- ✅ State validation with CSRF protection
- ✅ Dashboard sync status monitoring
- ✅ Structured JSON logging
- ✅ Sentry error tracking
- ✅ Token refresh mechanisms

### What's Missing
- ❌ Actual posting to platforms (OAuth ready, but no publishing)
- ❌ Redis for state storage (currently in-memory)
- ❌ Rate limiting on endpoints
- ❌ Content scheduling system
- ❌ Database performance optimization
- ❌ Webhook handling for platform events

### Technical Debt from Session 16
- 🔧 In-memory state storage (not production-ready)
- 🔧 No rate limiting (vulnerable to abuse)
- 🔧 Missing background job system for scheduling
- 🔧 No database indexing strategy

---

## 🛠️ Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Content    │  │  Publishing  │  │  Scheduling  │  │
│  │   Creator    │  │   Interface  │  │   Calendar   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (API Layer)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Publishing  │  │    OAuth     │  │     Rate     │  │
│  │     API      │  │   Endpoints  │  │   Limiter    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
┌──────────────────────┐    ┌──────────────────────┐
│   Redis (State &     │    │   PostgreSQL         │
│   Rate Limiting)     │    │   (Persistent Data)  │
│                      │    │                      │
│ • OAuth States       │    │ • Users              │
│ • Rate Limit Counters│    │ • Businesses         │
│ • Job Queues         │    │ • SocialAccounts     │
│ • Cache              │    │ • PublishedPosts     │
└──────────────────────┘    │ • ScheduledPosts     │
                            └──────────────────────┘
                                      │
                                      ▼
                            ┌──────────────────────┐
                            │  Celery Workers      │
                            │  (Background Jobs)   │
                            │                      │
                            │ • Scheduled Posting  │
                            │ • Token Refresh      │
                            │ • Analytics Sync     │
                            └──────────────────────┘
                                      │
                                      ▼
                            ┌──────────────────────┐
                            │  Social Platforms    │
                            │                      │
                            │ • LinkedIn API       │
                            │ • Twitter API        │
                            │ • Meta Graph API     │
                            └──────────────────────┘
```

---

## 📝 Task Breakdown

### Task 1: Publishing API Implementation (2.5 hours)
**Priority**: Critical  
**Dependencies**: Session 16 OAuth complete

**Subtasks**:
1. Create `app/services/publishing/` module
   - `linkedin_publisher.py` - LinkedIn UGC Posts API v2
   - `twitter_publisher.py` - Twitter API v2 posts
   - `meta_publisher.py` - Meta Graph API posts
   - `base_publisher.py` - Abstract base class

2. Create `app/api/publishing.py` endpoints
   - `POST /api/v1/publish/linkedin` - Publish to LinkedIn
   - `POST /api/v1/publish/twitter` - Publish to Twitter (with thread support)
   - `POST /api/v1/publish/meta` - Publish to Facebook/Instagram
   - `POST /api/v1/publish/multi` - Multi-platform publishing

3. Add database model `ScheduledPost`
   ```python
   class ScheduledPost(Base):
       id: int
       business_id: int
       content: str
       platforms: List[str]
       scheduled_for: datetime
       status: str  # pending, published, failed
       published_post_ids: Dict[str, str]
       created_at: datetime
   ```

4. Implement error handling and retries
   - Platform-specific error codes
   - Automatic retry logic (3 attempts)
   - Failed post notifications

**Testing**:
- Manual post to each platform
- Thread posting (Twitter)
- Multi-platform publishing
- Error scenarios (invalid token, API errors)

---

### Task 2: Redis State Manager (1.5 hours)
**Priority**: Critical  
**Dependencies**: None

**Subtasks**:
1. Install Redis dependencies
   ```bash
   # backend/requirements.txt
   redis==5.0.1
   ```

2. Create `app/core/redis_client.py`
   ```python
   from redis import Redis
   from app.core.config import settings
   
   redis_client = Redis(
       host=settings.REDIS_HOST,
       port=settings.REDIS_PORT,
       db=settings.REDIS_DB,
       decode_responses=True
   )
   ```

3. Update `app/core/security.py` StateManager
   - Replace in-memory dict with Redis
   - Use Redis TTL for 10-minute expiry
   - Atomic operations for state validation
   ```python
   class RedisStateManager:
       def generate_state(self, business_id, platform, code_verifier=None):
           state = secrets.token_urlsafe(32)
           key = f"oauth:state:{state}"
           redis_client.setex(key, 600, json.dumps(state_data))
           return state
       
       def validate_state(self, state, business_id, platform):
           key = f"oauth:state:{state}"
           data = redis_client.get(key)
           if not data:
               raise ValueError("Invalid or expired state")
           redis_client.delete(key)  # One-time use
           return json.loads(data)
   ```

4. Add Redis health check to `/health` endpoint

5. Update docker-compose.yml
   ```yaml
   redis:
     image: redis:7-alpine
     ports:
       - "6379:6379"
     volumes:
       - redis_data:/data
   ```

**Testing**:
- State generation and validation
- TTL expiry (wait 10 minutes)
- Concurrent access
- Redis connection failures

---

### Task 3: Rate Limiting (1 hour)
**Priority**: High  
**Dependencies**: Task 2 (Redis)

**Subtasks**:
1. Install rate limiting library
   ```bash
   pip install slowapi
   ```

2. Create `app/core/rate_limit.py`
   ```python
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(
       key_func=get_remote_address,
       storage_uri=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
   )
   ```

3. Apply rate limits to endpoints
   - OAuth endpoints: 10 requests/minute
   - Publishing endpoints: 20 requests/hour
   - Analytics endpoints: 100 requests/minute
   - Auth endpoints: 5 requests/minute

4. Custom rate limit by user_id
   ```python
   def get_user_id(request: Request):
       return request.state.user.get("user_id", get_remote_address(request))
   
   @router.post("/publish/linkedin")
   @limiter.limit("20/hour", key_func=get_user_id)
   async def publish_to_linkedin(...):
       ...
   ```

5. Add rate limit headers
   - `X-RateLimit-Limit`
   - `X-RateLimit-Remaining`
   - `X-RateLimit-Reset`

**Testing**:
- Exceed rate limits
- Different users
- Rate limit reset
- Header validation

---

### Task 4: Content Scheduling System (2 hours)
**Priority**: High  
**Dependencies**: Task 1 (Publishing API)

**Subtasks**:
1. Install Celery and dependencies
   ```bash
   pip install celery==5.3.4
   pip install celery[redis]
   ```

2. Create `app/celery_app.py`
   ```python
   from celery import Celery
   from app.core.config import settings
   
   celery_app = Celery(
       "ai_growth_manager",
       broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
       backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
   )
   
   celery_app.conf.update(
       task_serializer="json",
       result_serializer="json",
       accept_content=["json"],
       timezone="UTC",
       enable_utc=True,
   )
   ```

3. Create `app/tasks/publishing_tasks.py`
   ```python
   from app.celery_app import celery_app
   from app.services.publishing import publish_to_platform
   
   @celery_app.task(bind=True, max_retries=3)
   def publish_scheduled_post(self, scheduled_post_id: int):
       # Fetch scheduled post
       # Decrypt tokens
       # Publish to platforms
       # Update status
       # Handle errors with retry
   ```

4. Create scheduling endpoints
   - `POST /api/v1/schedule` - Schedule a post
   - `GET /api/v1/schedule/{business_id}` - List scheduled posts
   - `DELETE /api/v1/schedule/{post_id}` - Cancel scheduled post
   - `PUT /api/v1/schedule/{post_id}` - Reschedule post

5. Create Celery beat schedule for recurring tasks
   ```python
   celery_app.conf.beat_schedule = {
       'check-scheduled-posts': {
           'task': 'app.tasks.publishing_tasks.check_scheduled_posts',
           'schedule': 60.0,  # Every minute
       },
       'refresh-tokens': {
           'task': 'app.tasks.oauth_tasks.refresh_expiring_tokens',
           'schedule': 3600.0,  # Every hour
       },
   }
   ```

6. Add frontend calendar component
   - Create `components/ScheduleCalendar.tsx`
   - Integrate with `react-big-calendar`
   - Show scheduled posts on calendar
   - Drag-and-drop rescheduling

**Testing**:
- Schedule posts for future
- Immediate publishing
- Cancellation
- Rescheduling
- Failed post handling
- Celery worker functionality

---

### Task 5: Database Performance Optimization (1 hour)
**Priority**: Medium  
**Dependencies**: None

**Subtasks**:
1. Add database indexes
   ```python
   # Migration: add_performance_indexes
   
   # SocialAccount indexes
   op.create_index('idx_social_account_business_platform', 
                   'social_accounts', ['business_id', 'platform'])
   op.create_index('idx_social_account_active', 
                   'social_accounts', ['is_active'])
   
   # PublishedPost indexes
   op.create_index('idx_published_post_business', 
                   'published_posts', ['business_id'])
   op.create_index('idx_published_post_published_at', 
                   'published_posts', ['published_at'])
   
   # ScheduledPost indexes
   op.create_index('idx_scheduled_post_scheduled_for', 
                   'scheduled_posts', ['scheduled_for', 'status'])
   op.create_index('idx_scheduled_post_business', 
                   'scheduled_posts', ['business_id'])
   ```

2. Optimize queries
   - Add eager loading for relationships
   - Use `select_related()` and `prefetch_related()`
   - Batch operations where possible

3. Add query result caching
   ```python
   from functools import lru_cache
   from cachetools import TTLCache
   
   # Cache analytics data for 5 minutes
   analytics_cache = TTLCache(maxsize=100, ttl=300)
   ```

4. Database connection pooling
   ```python
   # app/db/database.py
   engine = create_engine(
       settings.DATABASE_URL,
       pool_size=20,
       max_overflow=40,
       pool_pre_ping=True,
       pool_recycle=3600,
   )
   ```

5. Add query monitoring with Sentry
   ```python
   from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
   
   sentry_sdk.init(
       integrations=[SqlalchemyIntegration()]
   )
   ```

**Testing**:
- Load test with 1000 concurrent requests
- Query performance profiling
- Database connection pool monitoring
- Cache hit rate analysis

---

### Task 6: Frontend Publishing Interface (1.5 hours)
**Priority**: High  
**Dependencies**: Task 1 (Publishing API)

**Subtasks**:
1. Create `components/PublishNowButton.tsx`
   ```tsx
   interface PublishNowButtonProps {
     content: string;
     platforms: string[];
     businessId: number;
     onSuccess?: () => void;
   }
   ```

2. Create `components/SchedulePostModal.tsx`
   - Date/time picker
   - Platform selection
   - Preview
   - Timezone selection

3. Update `app/dashboard/content/page.tsx`
   - Add "Publish Now" button
   - Add "Schedule" button
   - Show publishing status
   - Handle multi-platform publishing

4. Create `app/dashboard/scheduled/page.tsx`
   - Calendar view of scheduled posts
   - List view with filters
   - Edit/cancel scheduled posts
   - Drag-and-drop rescheduling

5. Add publishing notifications
   - Success toast
   - Error alerts
   - Progress indicator for multi-platform

**Testing**:
- Publish immediately
- Schedule for future
- Multi-platform selection
- Error handling
- UI responsiveness

---

### Task 7: Testing & Documentation (0.5 hours)
**Priority**: Medium  
**Dependencies**: All tasks

**Subtasks**:
1. Create `TESTING_GUIDE_SESSION_17.md`
   - Publishing API testing
   - Redis state management testing
   - Rate limiting testing
   - Scheduling testing

2. Create `QUICK_REFERENCE_S17.md`
   - Quick commands
   - API endpoints
   - Troubleshooting

3. Update `SESSION_17_SUMMARY.md`
   - Complete implementation details
   - Code samples
   - Architecture diagrams

4. API documentation updates
   - OpenAPI schema for new endpoints
   - Request/response examples
   - Error codes

---

## 🔧 Environment Setup

### New Environment Variables
```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # Optional, for production

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_STRATEGY=moving-window

# Publishing Configuration
PUBLISH_RETRY_ATTEMPTS=3
PUBLISH_RETRY_DELAY=5  # seconds
```

### Docker Compose Updates
```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
  
  celery_worker:
    build: ./backend
    command: celery -A app.celery_app worker --loglevel=info
    depends_on:
      - redis
      - db
    env_file:
      - ./backend/.env
  
  celery_beat:
    build: ./backend
    command: celery -A app.celery_app beat --loglevel=info
    depends_on:
      - redis
      - db
    env_file:
      - ./backend/.env

volumes:
  redis_data:
```

### NPM Packages (Frontend)
```json
{
  "dependencies": {
    "react-big-calendar": "^1.8.5",
    "date-fns": "^2.30.0",
    "react-datepicker": "^4.21.0"
  }
}
```

---

## 📊 Success Metrics

### Performance Targets
- API response time: <200ms (p95)
- Publishing success rate: >98%
- Rate limit effectiveness: 100% enforcement
- Scheduled post accuracy: ±1 minute
- Database query time: <50ms (p95)

### Feature Completeness
- ✅ Publish to all 3 platforms
- ✅ Thread support (Twitter)
- ✅ Multi-platform publishing
- ✅ Content scheduling
- ✅ Redis state management
- ✅ Rate limiting active
- ✅ Background jobs running
- ✅ Error handling robust

### Quality Metrics
- Test coverage: >80%
- Documentation: 100% complete
- Error handling: Comprehensive
- Security: Production-ready
- Performance: Optimized

---

## 🚨 Risk Assessment

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Redis connection failures | High | Low | Fallback to in-memory, alerting |
| Platform API changes | High | Medium | Version pinning, monitoring |
| Celery worker crashes | High | Low | Auto-restart, health checks |
| Rate limit bypass | Medium | Low | Multiple layers (IP + User) |
| Timezone handling errors | Medium | Medium | UTC everywhere, clear conversions |

### Timeline Risks
- Redis integration may take longer than expected
- Platform API testing needs real accounts
- Celery setup complexity
- Frontend calendar component integration

---

## 📋 Pre-Session Checklist

### Before Starting
- [x] Session 16 complete and documented
- [x] OAuth tokens working for all platforms
- [x] Database migrations up to date
- [x] Development environment running
- [ ] Redis installed locally or Docker ready
- [ ] Test social accounts verified
- [ ] Celery dependencies reviewed

### Development Environment
```bash
# Backend
cd backend
source venv/bin/activate
pip install redis celery slowapi

# Start Redis (Docker)
docker-compose up redis -d

# Frontend
cd frontend
npm install react-big-calendar date-fns react-datepicker
```

---

## 📚 Reference Materials

### APIs to Review
- [LinkedIn UGC Posts API v2](https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin)
- [Twitter API v2 - Create Tweet](https://developer.twitter.com/en/docs/twitter-api/tweets/manage-tweets/api-reference/post-tweets)
- [Meta Graph API - Posts](https://developers.facebook.com/docs/graph-api/reference/v18.0/post)

### Libraries Documentation
- [Redis-py Documentation](https://redis-py.readthedocs.io/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [SlowAPI (Rate Limiting)](https://github.com/laurentS/slowapi)
- [React Big Calendar](https://jquense.github.io/react-big-calendar/)

### Internal Documentation
- SESSION_16_COMPLETE_SUMMARY.md - OAuth implementation
- OAUTH_SETUP_GUIDE.md - Platform credentials
- QUICK_REFERENCE_S16.md - Quick commands

---

## 🎯 Session Workflow

### Phase 1: Publishing API (Hours 1-2.5)
1. Create publishing services for each platform
2. Implement API endpoints
3. Add ScheduledPost model and migration
4. Test publishing to each platform
5. Error handling and retry logic

### Phase 2: Redis & Rate Limiting (Hours 2.5-5)
1. Set up Redis client
2. Migrate StateManager to Redis
3. Implement rate limiting
4. Test state management and limits
5. Update health checks

### Phase 3: Scheduling & Jobs (Hours 5-7)
1. Install and configure Celery
2. Create publishing tasks
3. Implement scheduling endpoints
4. Set up Celery beat
5. Test background jobs

### Phase 4: Frontend & Optimization (Hours 7-8)
1. Create publishing UI components
2. Build scheduling calendar
3. Database optimization
4. Performance testing
5. Documentation

---

## ✅ Definition of Done

### Code Complete
- [ ] All 7 tasks implemented
- [ ] Unit tests written (>80% coverage)
- [ ] Integration tests passing
- [ ] No critical bugs
- [ ] Code reviewed (self-review)

### Documentation Complete
- [ ] SESSION_17_SUMMARY.md created
- [ ] QUICK_REFERENCE_S17.md created
- [ ] TESTING_GUIDE_SESSION_17.md created
- [ ] API documentation updated
- [ ] Code comments added

### Deployment Ready
- [ ] Environment variables documented
- [ ] Docker Compose updated
- [ ] Migration scripts tested
- [ ] Redis configured
- [ ] Celery workers ready
- [ ] Health checks passing

### User Experience
- [ ] Can publish to all platforms
- [ ] Can schedule posts
- [ ] Can view scheduled posts
- [ ] Error messages clear
- [ ] UI responsive and intuitive

---

## 🚀 Let's Begin!

**Session 17 is ready to start!**

First task: Create the publishing services module and implement LinkedIn publishing.

**Estimated completion**: 6-8 hours of focused work  
**Break frequency**: Every 90 minutes  
**Testing approach**: Test after each task completion  

---

**Session 17 Status: 🟢 READY TO START**

*Let's build the publishing engine!* 🚀
