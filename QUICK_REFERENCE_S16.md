# Session 16 - Quick Reference Guide
## OAuth, Dashboard, and Observability

---

## 🚀 Quick Start

### Start Backend
```bash
cd backend
docker-compose up -d
# Or
python -m uvicorn app.main:app --reload --port 8003
```

### Start Frontend
```bash
cd frontend
npm run dev
```

### Access Points
- Backend API: http://localhost:8003
- API Docs: http://localhost:8003/docs
- Frontend: http://localhost:3000
- Analytics Dashboard: http://localhost:3000/dashboard/analytics

---

## 🔑 OAuth Flows

### Initiate OAuth (Any Platform)
```bash
# Visit in browser:
http://localhost:8003/api/v1/oauth/{platform}/authorize?business_id=1

# Platforms: linkedin, twitter, meta
```

### Check Connection Status
```bash
curl http://localhost:8003/api/v1/oauth/{platform}/status?business_id=1
```

### Refresh Token (Twitter only)
```bash
curl -X POST http://localhost:8003/api/v1/oauth/twitter/refresh?business_id=1
```

### Disconnect Platform
```bash
curl -X DELETE http://localhost:8003/api/v1/oauth/{platform}/disconnect?business_id=1
```

---

## 📊 Dashboard Endpoints

### Get Sync Status
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8003/api/v1/analytics/sync-status/1
```

**Response**:
```json
{
  "overall_status": "success",
  "last_sync": "2024-01-15T10:30:00",
  "connected_platforms": 3,
  "platforms": {
    "linkedin": { "status": "success", "message": "Last sync successful" },
    "twitter": { "status": "error", "message": "Token expired" }
  }
}
```

### Get Sync History
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8003/api/v1/analytics/sync-history/1?limit=10
```

### Trigger Manual Sync
```bash
curl -X POST -H "Authorization: Bearer <token>" \
  http://localhost:8003/api/v1/scheduler/trigger/1
```

---

## 🔒 Security Features

### Generate Encryption Key
```bash
cd backend
python scripts/generate_encryption_key.py
```

Copy the output to your `.env`:
```bash
ENCRYPTION_KEY=<generated-key>
```

### Token Encryption
All OAuth tokens are automatically encrypted before database storage.

**Helper Functions**:
```python
from app.core.token_helpers import (
    get_decrypted_access_token,
    get_decrypted_refresh_token,
    is_token_valid
)

# Get decrypted token
access_token = get_decrypted_access_token(social_account)

# Check if token is valid
if is_token_valid(social_account, linkedin_oauth):
    # Token is valid and not expired
```

### State Management
- 10-minute expiry
- One-time use
- Automatic cleanup
- CSRF protection

---

## 📝 Structured Logging

### Log Format (JSON)
```json
{
  "timestamp": "2024-01-15T12:30:45.123456",
  "level": "INFO",
  "service": "app.services.oauth_linkedin",
  "request_id": "abc-123-def-456",
  "user_id": "user_abc123",
  "business_id": 42,
  "event_type": "oauth_token_exchange",
  "message": "Successfully exchanged code for LinkedIn token"
}
```

### Using Structured Logging
```python
from app.core.logging_config import get_logger, log_event

logger = get_logger(__name__)

# Standard logging
logger.info("User logged in")

# Structured event logging
log_event(
    logger,
    event_type='oauth_token_exchange',
    message='Successfully exchanged code for LinkedIn token',
    platform='linkedin',
    expires_in=5184000
)
```

### View Logs
```bash
# Docker
docker-compose logs backend -f

# Direct
tail -f backend.log | jq .
```

---

## 🐛 Sentry Integration

### Manual Error Capture
```python
from app.core.sentry_config import (
    capture_exception,
    capture_message,
    add_breadcrumb,
    set_user_context
)

# Capture exception
try:
    risky_operation()
except Exception as e:
    event_id = capture_exception(e, extra_context={'key': 'value'})

# Capture message
event_id = capture_message('Something went wrong', level='error')

# Add breadcrumb
add_breadcrumb(
    category='oauth',
    message='Starting token exchange',
    level='info',
    data={'platform': 'linkedin'}
)

# Set user context
set_user_context(user_id='user_123', business_id=42)
```

### Test Sentry
Add test endpoint:
```python
@router.get("/test-sentry")
async def test_sentry():
    raise Exception("Testing Sentry!")
```

Visit: http://localhost:8003/test-sentry

---

## 🧪 Testing

### Test OAuth Flow
1. **LinkedIn**:
   ```
   http://localhost:8003/api/v1/oauth/linkedin/authorize?business_id=1
   ```

2. **Twitter** (with PKCE):
   ```
   http://localhost:8003/api/v1/oauth/twitter/authorize?business_id=1
   ```

3. **Meta** (Facebook/Instagram):
   ```
   http://localhost:8003/api/v1/oauth/meta/authorize?business_id=1
   ```

### Test Dashboard Widget
1. Go to: http://localhost:3000/dashboard/analytics
2. Check sync status widget
3. Click "Sync Now" button
4. Expand platform details
5. Wait 30 seconds for auto-refresh

### Test Token Encryption
```python
# In Python shell
from app.core.security import token_encryption

# Encrypt
encrypted = token_encryption.encrypt_token("my-secret-token")
print(f"Encrypted: {encrypted}")

# Decrypt
decrypted = token_encryption.decrypt_token(encrypted)
print(f"Decrypted: {decrypted}")
```

---

## 🔧 Common Issues & Solutions

### Issue: "Invalid or expired state parameter"
**Solution**: State expires after 10 minutes. Start OAuth flow again.

### Issue: "Token encryption failed"
**Solution**: 
1. Generate encryption key: `python scripts/generate_encryption_key.py`
2. Add to .env: `ENCRYPTION_KEY=<key>`
3. Restart backend

### Issue: "Sentry not initialized"
**Solution**: Add to .env:
```bash
SENTRY_DSN=https://your-dsn@sentry.io/project-id
```

### Issue: "Frontend sync status not loading"
**Solution**:
1. Check backend is running: http://localhost:8003/health
2. Check authentication token is valid
3. Check browser console for errors
4. Verify business_id exists

### Issue: "Twitter PKCE error"
**Solution**: code_verifier is stored server-side. Don't pass it as parameter.

---

## 📦 Key Files Reference

### Backend Core Files
```
backend/app/
├── core/
│   ├── security.py           # Token encryption + State management
│   ├── logging_config.py     # JSON logging + Request middleware
│   ├── sentry_config.py      # Sentry SDK initialization
│   └── token_helpers.py      # Encryption helper utilities
```

### OAuth Services
```
backend/app/services/
├── oauth_linkedin.py         # LinkedIn OAuth 2.0
├── oauth_twitter.py          # Twitter OAuth 2.0 PKCE
└── oauth_meta.py             # Meta OAuth (Facebook/Instagram)
```

### API Endpoints
```
backend/app/api/
├── oauth.py                  # 6 OAuth endpoints
└── analytics.py              # 3 sync status endpoints
```

### Frontend Components
```
frontend/app/
├── components/
│   └── SyncStatus.tsx        # Real-time sync status widget
└── dashboard/analytics/
    └── page.tsx              # Analytics dashboard (integrated)
```

---

## 🌐 API Endpoints Summary

### OAuth Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/oauth/platforms` | List supported platforms |
| GET | `/api/v1/oauth/{platform}/authorize` | Start OAuth flow |
| GET | `/api/v1/oauth/{platform}/callback` | OAuth callback handler |
| POST | `/api/v1/oauth/{platform}/refresh` | Refresh access token |
| DELETE | `/api/v1/oauth/{platform}/disconnect` | Disconnect platform |
| GET | `/api/v1/oauth/{platform}/status` | Check connection status |

### Analytics/Sync Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/sync-status/{business_id}` | Get sync status |
| GET | `/api/v1/analytics/sync-history/{business_id}` | Get sync history |
| GET | `/api/v1/analytics/sync-progress/{job_id}` | Get sync progress |
| POST | `/api/v1/scheduler/trigger/{business_id}` | Manual sync trigger |

---

## 🎯 Environment Variables

### Required
```bash
# OAuth Credentials
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret
META_CLIENT_ID=your_meta_app_id
META_CLIENT_SECRET=your_meta_app_secret

# Security
ENCRYPTION_KEY=<generate with scripts/generate_encryption_key.py>

# Observability (Optional)
SENTRY_DSN=https://your-dsn@sentry.io/project-id
LOG_LEVEL=INFO
ENVIRONMENT=development
VERSION=0.2.0
```

### Redirect URIs
```bash
LINKEDIN_REDIRECT_URI=http://localhost:8003/api/v1/oauth/linkedin/callback
TWITTER_REDIRECT_URI=http://localhost:8003/api/v1/oauth/twitter/callback
META_REDIRECT_URI=http://localhost:8003/api/v1/oauth/meta/callback
```

---

## 📚 Next Steps

1. **Test OAuth flows** on all 3 platforms
2. **Generate encryption key** and add to .env
3. **Set up Sentry** for error tracking (optional but recommended)
4. **Test dashboard** sync status widget
5. **Review logs** in JSON format
6. **Check Sentry** for captured events

---

## 🆘 Getting Help

### Check Documentation
- SESSION_16_COMPLETE_SUMMARY.md - Full implementation details
- OAUTH_SETUP_GUIDE.md - Platform-specific setup
- API Docs: http://localhost:8003/docs

### Debug Checklist
- [ ] Check backend logs: `docker-compose logs backend -f`
- [ ] Check frontend console: Browser DevTools
- [ ] Verify environment variables in .env
- [ ] Test health endpoint: http://localhost:8003/health
- [ ] Check database connections
- [ ] Verify encryption key is set

---

**Quick Reference v1.0**  
**Last Updated**: Session 16  
**Status**: Production Ready ✅
