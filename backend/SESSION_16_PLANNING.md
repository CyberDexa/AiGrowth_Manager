# Session 16 Planning: OAuth 2.0 & Dashboard Enhancements

**Date**: October 13, 2025  
**Session Goal**: Complete OAuth flows, dashboard sync status, and structured logging  
**Previous Session**: Session 15 (60% complete - Testing & Background Scheduler)

---

## 📋 Session 16 Objectives

### Remaining from Session 15
- **Task 7**: OAuth 2.0 Implementation (High Priority)
- **Task 8**: Dashboard Sync Status Features (High Priority)
- **Task 9**: Structured Logging & Monitoring (Medium Priority)
- **Task 4**: Integration Tests with PostgreSQL (Deferred - Low Priority)

---

## 🎯 Phase 1: OAuth 2.0 Implementation (3-4 hours)

### LinkedIn OAuth
- [ ] Update oauth_linkedin.py with complete OAuth 2.0 flow
- [ ] Implement authorization URL generation
- [ ] Handle callback and token exchange
- [ ] Implement token refresh logic
- [ ] Add token expiration checking
- [ ] Test with LinkedIn OAuth app

### Twitter OAuth 2.0 PKCE
- [ ] Update oauth_twitter.py with OAuth 2.0 PKCE flow
- [ ] Generate code verifier and challenge
- [ ] Implement authorization URL with PKCE
- [ ] Handle callback with code verifier
- [ ] Implement token refresh
- [ ] Test with Twitter OAuth app

### Meta (Facebook/Instagram) OAuth
- [ ] Update oauth_meta.py with long-lived token exchange
- [ ] Implement authorization URL generation
- [ ] Handle callback and short-lived token exchange
- [ ] Exchange short-lived for long-lived token
- [ ] Add Instagram account linking
- [ ] Test with Meta app

### OAuth API Endpoints
- [ ] Create oauth router in app/api/oauth.py
- [ ] GET /api/v1/oauth/{platform}/authorize - Initiate flow
- [ ] GET /api/v1/oauth/{platform}/callback - Handle redirect
- [ ] POST /api/v1/oauth/{platform}/refresh - Refresh tokens
- [ ] DELETE /api/v1/oauth/{platform}/disconnect - Revoke tokens
- [ ] GET /api/v1/oauth/status - Check connection status

### Security Enhancements
- [ ] Implement PKCE for all flows
- [ ] Add state parameter for CSRF protection
- [ ] Encrypt tokens in database
- [ ] Add token expiration tracking
- [ ] Implement automatic token refresh

---

## 🎯 Phase 2: Dashboard Sync Status (1-2 hours)

### Backend API Enhancements
- [ ] GET /api/v1/analytics/sync-status/{business_id}
- [ ] GET /api/v1/analytics/sync-history/{business_id}
- [ ] POST /api/v1/analytics/sync/{business_id} (manual trigger)
- [ ] WebSocket endpoint for real-time sync updates (optional)

### Frontend Components
- [ ] Create SyncStatusCard component
- [ ] Display last sync time
- [ ] Show success/failure counts by platform
- [ ] Add manual sync button
- [ ] Show next scheduled sync time
- [ ] Add sync progress indicator
- [ ] Display sync history table

### Real-time Updates
- [ ] Poll sync status every 30 seconds
- [ ] Show "Syncing..." indicator during active sync
- [ ] Toast notifications for sync completion
- [ ] Error notifications for failed syncs

---

## 🎯 Phase 3: Structured Logging (30-45 minutes)

### Python JSON Logger
- [ ] Install and configure python-json-logger
- [ ] Create logging configuration module
- [ ] Add structured logging to all services
- [ ] Include request IDs for tracing
- [ ] Add performance timing logs

### Sentry Integration
- [ ] Install sentry-sdk
- [ ] Configure Sentry DSN
- [ ] Add Sentry to FastAPI app
- [ ] Configure error sampling
- [ ] Add breadcrumbs for debugging
- [ ] Test error reporting

### Logging Guidelines
- [ ] Document logging levels
- [ ] Create logging best practices guide
- [ ] Add examples for common scenarios
- [ ] Set up log aggregation (optional)

---

## 🎯 Phase 4: Integration Tests (Optional - 1-2 hours)

### PostgreSQL Test Database
- [ ] Create docker-compose for test database
- [ ] Update conftest.py for PostgreSQL
- [ ] Run integration tests
- [ ] Achieve 85%+ coverage for sync service

---

## 📦 Dependencies to Add

```txt
# OAuth
authlib==1.3.1  # Already added

# Logging
python-json-logger==2.0.7  # Already added
sentry-sdk==2.14.0  # Already added

# Testing (if doing PostgreSQL tests)
psycopg2-binary==2.9.9
testcontainers==4.7.0  # Optional: Docker containers in tests
```

---

## 🎯 Success Criteria

### OAuth Implementation
- [ ] All 3 platforms have working OAuth flows
- [ ] Tokens refresh automatically before expiration
- [ ] Tokens encrypted in database
- [ ] CSRF protection implemented
- [ ] OAuth endpoints documented

### Dashboard Features
- [ ] Sync status visible in dashboard
- [ ] Manual sync button works
- [ ] Real-time updates show progress
- [ ] Sync history displays correctly
- [ ] Error states handled gracefully

### Logging
- [ ] JSON logs in production
- [ ] Sentry captures errors
- [ ] Request tracing works
- [ ] Performance metrics logged
- [ ] Logging guidelines documented

---

## 📝 Task Breakdown

### High Priority (Must Complete)
1. **OAuth LinkedIn** (1 hour)
2. **OAuth Twitter** (1 hour)
3. **OAuth Meta** (1 hour)
4. **OAuth API Endpoints** (30 minutes)
5. **Dashboard Sync Status Backend** (30 minutes)
6. **Dashboard Sync Status Frontend** (1 hour)

### Medium Priority (Should Complete)
7. **Structured Logging** (30 minutes)
8. **Sentry Integration** (15 minutes)

### Nice to Have (Time Permitting)
9. **WebSocket Real-time Updates** (1 hour)
10. **PostgreSQL Integration Tests** (2 hours)

---

## 🔄 Development Workflow

1. **Start with OAuth LinkedIn** (most straightforward)
2. **Test OAuth flow end-to-end**
3. **Repeat for Twitter and Meta**
4. **Create unified OAuth API**
5. **Build dashboard components**
6. **Add logging and monitoring**
7. **Test everything together**
8. **Document and deploy**

---

## 🎓 Technical Considerations

### OAuth Security
- Use HTTPS in production
- Validate state parameter on callback
- Store tokens encrypted
- Implement token rotation
- Handle revocation gracefully

### Dashboard UX
- Show clear sync status indicators
- Provide helpful error messages
- Allow retry on failures
- Display sync progress
- Cache status to reduce API calls

### Logging Strategy
- Log all OAuth attempts
- Log sync job start/end
- Log API errors with context
- Include user/business IDs
- Sanitize sensitive data

---

## 📊 Estimated Timeline

| Phase | Task | Time | Priority |
|-------|------|------|----------|
| 1 | LinkedIn OAuth | 1h | High |
| 1 | Twitter OAuth | 1h | High |
| 1 | Meta OAuth | 1h | High |
| 1 | OAuth API Endpoints | 30m | High |
| 1 | Security Enhancements | 30m | High |
| 2 | Backend API | 30m | High |
| 2 | Frontend Components | 1h | High |
| 2 | Real-time Updates | 30m | Medium |
| 3 | Structured Logging | 30m | Medium |
| 3 | Sentry Integration | 15m | Medium |
| 4 | Integration Tests | 2h | Low |

**Total Estimated Time**: 6-8 hours  
**Target Completion**: 80-100% of Session 16 goals

---

## 🚀 Getting Started

### Step 1: Set Up OAuth Apps
```bash
# LinkedIn: https://www.linkedin.com/developers/apps
# Twitter: https://developer.twitter.com/en/portal/dashboard
# Meta: https://developers.facebook.com/apps/
```

### Step 2: Update Environment Variables
```bash
# Add to .env
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_REDIRECT_URI=http://localhost:3000/oauth/linkedin/callback

TWITTER_CLIENT_ID=your_client_id
TWITTER_CLIENT_SECRET=your_client_secret
TWITTER_REDIRECT_URI=http://localhost:3000/oauth/twitter/callback

META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
META_REDIRECT_URI=http://localhost:3000/oauth/meta/callback
```

### Step 3: Start Development
```bash
# Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8003

# Frontend
cd frontend
npm run dev
```

---

**Session 16 Ready to Start!** 🚀

Let's make the platform fully production-ready with OAuth, real-time sync status, and enterprise logging! 💪
