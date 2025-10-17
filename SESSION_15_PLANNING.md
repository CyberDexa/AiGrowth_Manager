# Session 15: Testing, Background Jobs & OAuth Implementation

**Date**: October 13, 2025  
**Status**: 🚀 **IN PROGRESS** (0%)  
**Previous Session**: Session 14 - Platform API Integration (✅ Complete)

---

## 🎯 Session Goals

Make the analytics platform production-ready by implementing:
1. Comprehensive unit and integration tests
2. Background job scheduling for automatic analytics refresh
3. OAuth 2.0 flows for LinkedIn, Twitter, and Meta
4. Dashboard enhancements to show sync status
5. Error monitoring and logging infrastructure

---

## 📋 Session Plan

### Phase 1: Testing Infrastructure (25% - 2-3 hours)
- [ ] Set up pytest configuration
- [ ] Create mock API response fixtures
- [ ] Write unit tests for base fetcher
- [ ] Write unit tests for LinkedIn fetcher
- [ ] Write unit tests for Twitter fetcher
- [ ] Write unit tests for Meta fetcher
- [ ] Write integration tests for sync service
- [ ] Test error handling and rate limiting

### Phase 2: Background Job Scheduler (20% - 1-2 hours)
- [ ] Install and configure APScheduler
- [ ] Create background job for hourly analytics refresh
- [ ] Add job monitoring and health checks
- [ ] Create admin endpoint to trigger manual sync
- [ ] Handle job failures and retries
- [ ] Log job execution metrics

### Phase 3: OAuth Implementation (30% - 3-4 hours)
- [ ] Design OAuth callback endpoints
- [ ] Implement LinkedIn OAuth 2.0 flow
- [ ] Implement Twitter OAuth 2.0 flow
- [ ] Implement Meta OAuth 2.0 flow
- [ ] Store access tokens securely
- [ ] Handle token refresh automatically
- [ ] Add OAuth connection UI endpoints

### Phase 4: Dashboard Enhancements (15% - 2 hours)
- [ ] Add "Last Synced" indicator
- [ ] Add "Sync Now" button
- [ ] Show sync status (syncing, completed, failed)
- [ ] Display platform-specific sync results
- [ ] Show rate limit warnings
- [ ] Add sync history timeline

### Phase 5: Error Monitoring & Logging (10% - 1-2 hours)
- [ ] Set up structured logging
- [ ] Configure log levels and formatters
- [ ] Add request ID tracking
- [ ] Create error dashboard endpoint
- [ ] Log sync health metrics
- [ ] Add performance monitoring

---

## 🎯 Success Criteria

- ✅ Test coverage > 80% for platform fetchers
- ✅ Background jobs run reliably every hour
- ✅ Users can connect social accounts via OAuth
- ✅ Dashboard shows real-time sync status
- ✅ All errors are logged with context
- ✅ Token refresh happens automatically
- ✅ Rate limits are respected and reported

---

## 📊 Current System State

### From Session 14 ✅
- ✅ 4 platform fetchers implemented (LinkedIn, Twitter, Facebook, Instagram)
- ✅ Analytics sync service orchestrating all platforms
- ✅ `/refresh` endpoint using real platform data
- ✅ Database with 9 tables (including analytics tables)
- ✅ Custom exception hierarchy for error handling
- ✅ Retry logic and rate limiting

### Gaps to Address 🔧
- ⚠️ No automated testing (0% coverage)
- ⚠️ Manual refresh only (no background jobs)
- ⚠️ No OAuth flows (users must manually add tokens)
- ⚠️ Limited sync status visibility on dashboard
- ⚠️ Basic error logging (needs structured logging)
- ⚠️ No token refresh mechanism

---

## 🛠️ Technical Approach

### Testing Strategy

**Unit Tests** (using pytest + unittest.mock):
```python
# tests/test_linkedin_fetcher.py
from unittest.mock import Mock, patch
import pytest
from app.services.platform_fetchers import LinkedInAnalyticsFetcher

@patch('requests.Session.request')
def test_fetch_post_analytics_success(mock_request):
    # Mock LinkedIn API response
    mock_response = Mock()
    mock_response.json.return_value = {
        "elements": [{
            "totalShareStatistics": {
                "likeCount": 100,
                "commentCount": 20,
                "shareCount": 10,
                "impressionCount": 5000
            }
        }]
    }
    mock_response.status_code = 200
    mock_request.return_value = mock_response
    
    fetcher = LinkedInAnalyticsFetcher(access_token="test_token")
    analytics = fetcher.fetch_post_analytics("1", "urn:li:share:123")
    
    assert analytics["likes_count"] == 100
    assert analytics["comments_count"] == 20
    assert analytics["engagement_rate"] > 0

@patch('requests.Session.request')
def test_rate_limit_handling(mock_request):
    # Mock rate limit response
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.headers = {"Retry-After": "60"}
    mock_request.return_value = mock_response
    
    fetcher = LinkedInAnalyticsFetcher(access_token="test_token")
    
    with pytest.raises(RateLimitError) as exc_info:
        fetcher.fetch_post_analytics("1", "urn:li:share:123")
    
    assert exc_info.value.retry_after == 60
```

**Integration Tests** (using test database):
```python
# tests/test_analytics_sync_service.py
def test_sync_business_analytics(test_db, mock_social_accounts):
    sync_service = AnalyticsSyncService(test_db)
    
    results = sync_service.sync_business_analytics(
        business_id=1,
        platforms=["linkedin"]
    )
    
    assert results["total_posts"] > 0
    assert results["synced"] == results["total_posts"]
    assert len(results["errors"]) == 0
```

### Background Scheduler (APScheduler)

```python
# backend/app/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def sync_all_businesses():
    """Background job to sync analytics for all businesses."""
    from app.db.database import SessionLocal
    from app.services.platform_fetchers import AnalyticsSyncService
    from app.models.business import Business
    
    db = SessionLocal()
    try:
        businesses = db.query(Business).all()
        
        for business in businesses:
            try:
                sync_service = AnalyticsSyncService(db)
                results = sync_service.sync_business_analytics(business.id)
                logger.info(f"Synced business {business.id}: {results['synced']} posts")
            except Exception as e:
                logger.error(f"Failed to sync business {business.id}: {e}")
    finally:
        db.close()

# Schedule job to run every hour
scheduler.add_job(
    func=sync_all_businesses,
    trigger=IntervalTrigger(hours=1),
    id='sync_analytics_hourly',
    name='Sync analytics from all platforms',
    replace_existing=True
)

def start_scheduler():
    scheduler.start()
    logger.info("Scheduler started")

def shutdown_scheduler():
    scheduler.shutdown()
    logger.info("Scheduler stopped")
```

### OAuth Implementation

**LinkedIn OAuth Flow**:
```python
# backend/app/api/oauth.py
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
import httpx

router = APIRouter(prefix="/api/v1/oauth", tags=["oauth"])

@router.get("/linkedin/authorize")
async def linkedin_authorize(business_id: int):
    """Redirect user to LinkedIn authorization page."""
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code"
        f"&client_id={LINKEDIN_CLIENT_ID}"
        f"&redirect_uri={LINKEDIN_REDIRECT_URI}"
        f"&state={business_id}"
        f"&scope=r_organization_social r_basicprofile"
    )
    return RedirectResponse(url=auth_url)

@router.get("/linkedin/callback")
async def linkedin_callback(
    code: str = Query(...),
    state: str = Query(...)  # business_id
):
    """Handle LinkedIn OAuth callback."""
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": LINKEDIN_CLIENT_ID,
                "client_secret": LINKEDIN_CLIENT_SECRET,
                "redirect_uri": LINKEDIN_REDIRECT_URI
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        token_data = response.json()
        
        # Save to social_accounts table
        # ... (database logic)
        
        return {"success": True, "platform": "linkedin"}
```

### Dashboard Enhancements

**New API Endpoint**:
```python
@router.get("/sync-status")
async def get_sync_status(
    business_id: int,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """Get current sync status for dashboard."""
    sync_service = AnalyticsSyncService(db)
    status = sync_service.get_sync_status(business_id)
    
    return {
        "total_posts": status["total_posts"],
        "synced_posts": status["synced_posts"],
        "unsynced_posts": status["unsynced_posts"],
        "last_sync_at": status["last_sync_at"],
        "sync_percentage": status["sync_percentage"],
        "is_syncing": False,  # TODO: Track active sync jobs
        "platforms": {
            "linkedin": {"connected": True, "last_sync": "..."},
            "twitter": {"connected": False, "last_sync": None},
            # ...
        }
    }
```

---

## 📦 Dependencies to Install

### Backend Dependencies

```bash
# Testing
pip install pytest pytest-asyncio pytest-cov pytest-mock faker

# Background Jobs
pip install apscheduler

# OAuth & HTTP
pip install httpx authlib

# Logging & Monitoring (optional)
pip install python-json-logger sentry-sdk
```

**Add to `requirements.txt`**:
```
pytest==8.3.3
pytest-asyncio==0.24.0
pytest-cov==5.0.0
pytest-mock==3.14.0
faker==28.0.0
apscheduler==3.10.4
authlib==1.3.1
python-json-logger==2.0.7
sentry-sdk==2.14.0
```

---

## 📁 Files to Create

### Testing Files (8 files)
```
backend/tests/
├── __init__.py
├── conftest.py                              # Pytest fixtures
├── fixtures/
│   ├── __init__.py
│   ├── linkedin_responses.py                # Mock LinkedIn API responses
│   ├── twitter_responses.py                 # Mock Twitter API responses
│   └── meta_responses.py                    # Mock Meta API responses
├── test_base_fetcher.py                     # Base fetcher tests
├── test_linkedin_fetcher.py                 # LinkedIn fetcher tests
├── test_twitter_fetcher.py                  # Twitter fetcher tests
├── test_meta_fetcher.py                     # Meta fetcher tests
├── test_analytics_sync_service.py           # Sync service tests
└── test_oauth_flows.py                      # OAuth integration tests
```

### Background Jobs (2 files)
```
backend/app/
├── scheduler.py                             # APScheduler configuration
└── jobs/
    ├── __init__.py
    └── analytics_sync_job.py                # Hourly sync job
```

### OAuth Implementation (2 files)
```
backend/app/api/
├── oauth.py                                 # OAuth endpoints
└── social_accounts.py                       # Social account management
```

### Logging Configuration (1 file)
```
backend/app/core/
└── logging_config.py                        # Structured logging setup
```

---

## 🔜 Next Steps After This Session

### Session 16: Advanced Analytics Features
- Sentiment analysis for posts
- Competitor benchmarking
- Best time to post predictions
- Content performance insights
- Audience growth tracking

### Session 17: Notifications & Alerts
- Email notifications for sync failures
- Slack/Discord webhooks
- Performance alerts (e.g., "Your post is performing 200% better than average!")
- Weekly analytics reports

### Session 18: Content Calendar & Publishing
- Visual content calendar
- Multi-platform scheduling
- Post preview
- Auto-publishing to platforms
- Content recycling suggestions

---

## 📊 Session 15 Progress Tracker

| Phase | Tasks | Completed | Remaining | Progress |
|-------|-------|-----------|-----------|----------|
| Testing Infrastructure | 8 | 0 | 8 | 0% |
| Background Jobs | 6 | 0 | 6 | 0% |
| OAuth Implementation | 7 | 0 | 7 | 0% |
| Dashboard Enhancements | 6 | 0 | 6 | 0% |
| Error Monitoring | 5 | 0 | 5 | 0% |
| **TOTAL** | **32** | **0** | **32** | **0%** |

---

## 🚀 Let's Begin!

**Session 15 starts now!** 🎉

First priority: Set up testing infrastructure and write tests for platform fetchers.

---

**Session 15 Status**: 🚀 **IN PROGRESS** (0%)  
**Created by**: AI Coding Agent  
**Date**: October 13, 2025
