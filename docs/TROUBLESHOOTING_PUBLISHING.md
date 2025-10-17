# Publishing System Troubleshooting Guide

## Overview

This guide covers common issues with the Publishing System and their solutions.

**System Components**:
- Backend API (FastAPI)
- Celery Worker (Background tasks)
- Celery Beat (Scheduler)
- Redis (Message broker & cache)
- PostgreSQL (Database)
- Frontend (Next.js React)

---

## 1. Posts Not Publishing

### Symptom
Scheduled posts stay in "pending" status and never publish.

### Diagnosis

**Check Celery Services**:
```bash
# Check if services are running
docker-compose ps

# Should show:
# celery_worker    running
# celery_beat      running
# redis            running
```

**Check Celery Worker Logs**:
```bash
docker-compose logs -f celery_worker

# Look for:
# [INFO] Connected to redis://redis:6379/0
# [INFO] celery@worker ready
# [ERROR] <any error messages>
```

**Check Celery Beat Logs**:
```bash
docker-compose logs -f celery_beat

# Look for:
# [INFO] Scheduler: Sending due task publish_scheduled_post
# [ERROR] <any error messages>
```

### Solutions

**Solution 1: Restart Celery Services**
```bash
docker-compose restart celery_worker celery_beat
```

**Solution 2: Check Celery Configuration**
```python
# In app/core/celery_app.py
print(f"Broker: {celery_app.conf.broker_url}")
print(f"Backend: {celery_app.conf.result_backend}")

# Should be:
# Broker: redis://redis:6379/0
# Backend: redis://redis:6379/0
```

**Solution 3: Verify Task Registration**
```bash
# Connect to Celery worker
docker-compose exec celery_worker celery -A app.core.celery_app inspect registered

# Should show:
# - app.services.publishing_service.publish_scheduled_post_task
```

**Solution 4: Check Database Connection**
```python
# In backend container
python -c "from app.db.database import engine; engine.connect()"

# Should connect without errors
```

**Solution 5: Manual Task Execution**
```python
# Test task directly
from app.services.publishing_service import publish_scheduled_post_task

result = publish_scheduled_post_task.delay(scheduled_post_id=1)
print(f"Task ID: {result.id}")
print(f"Status: {result.status}")
```

---

## 2. Rate Limit Errors

### Symptom
```
429 Too Many Requests: Rate limit exceeded: 20 per 1 hour
```

### Diagnosis

**Check Current Rate Limit**:
```bash
# Via API response headers
curl -I "http://localhost:8000/api/v2/publish" \
  -H "Authorization: Bearer $TOKEN"

# Headers:
# X-RateLimit-Limit: 20
# X-RateLimit-Remaining: 0
# X-RateLimit-Reset: 1697290800
```

**Check Redis Keys**:
```bash
# Connect to Redis
docker-compose exec redis redis-cli

# List rate limit keys
KEYS *rate_limit*

# Check specific key
GET rate_limit:publish:/api/v2/publish:user_123

# Output: "20" (number of requests made)
```

### Solutions

**Solution 1: Wait for Reset**
```javascript
// Frontend: Calculate wait time
const resetTime = parseInt(response.headers.get('X-RateLimit-Reset'));
const now = Math.floor(Date.now() / 1000);
const waitSeconds = resetTime - now;

console.log(`Rate limit resets in ${waitSeconds} seconds`);
```

**Solution 2: Clear Rate Limit (Development Only)**
```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Delete all rate limit keys
KEYS *rate_limit* | xargs redis-cli DEL

# Or delete for specific endpoint
DEL rate_limit:publish:/api/v2/publish:user_123
```

**Solution 3: Increase Rate Limits (Backend)**
```python
# In app/api/v2/endpoints/publishing.py

@router.post("/publish")
@limiter.limit("50/hour")  # Increase from 20 to 50
async def publish_content(...):
    ...
```

**Solution 4: Implement Exponential Backoff**
```javascript
// Frontend: Retry with backoff
async function publishWithRetry(data, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch('/api/v2/publish', {
        method: 'POST',
        body: JSON.stringify(data)
      });
      
      if (response.status === 429) {
        const resetTime = response.headers.get('X-RateLimit-Reset');
        const waitMs = (parseInt(resetTime) * 1000) - Date.now();
        console.log(`Waiting ${waitMs}ms for rate limit reset...`);
        await new Promise(resolve => setTimeout(resolve, waitMs));
        continue;
      }
      
      return await response.json();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
    }
  }
}
```

---

## 3. OAuth Token Expired

### Symptom
```json
{
  "platform": "linkedin",
  "success": false,
  "error": "OAuth token expired"
}
```

### Diagnosis

**Check Token Expiration**:
```sql
-- In PostgreSQL
SELECT 
  platform,
  expires_at,
  expires_at < NOW() as is_expired,
  NOW() - expires_at as expired_since
FROM social_accounts
WHERE user_id = 'user_123';
```

**Check Token in Database**:
```sql
SELECT 
  platform,
  LENGTH(access_token) as token_length,
  is_active
FROM social_accounts
WHERE user_id = 'user_123';
```

### Solutions

**Solution 1: Re-authenticate**
```javascript
// Frontend: Redirect to OAuth flow
window.location.href = `/api/oauth/linkedin/authorize?user_id=${userId}`;
```

**Solution 2: Refresh Token (If Available)**
```python
# Backend: Implement token refresh
async def refresh_linkedin_token(social_account):
    response = await httpx.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data={
            "grant_type": "refresh_token",
            "refresh_token": social_account.refresh_token,
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "client_secret": settings.LINKEDIN_CLIENT_SECRET
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        social_account.access_token = data["access_token"]
        social_account.expires_at = datetime.now() + timedelta(seconds=data["expires_in"])
        db.commit()
```

**Solution 3: Automatic Re-auth Prompt**
```javascript
// Frontend: Detect expired token and prompt
if (error.includes("OAuth token expired")) {
  const shouldReauth = confirm(
    `Your ${platform} connection has expired. Reconnect now?`
  );
  
  if (shouldReauth) {
    window.location.href = `/api/oauth/${platform}/authorize`;
  }
}
```

**Solution 4: Pre-publish Token Check**
```python
# Backend: Validate tokens before publishing
def validate_social_account(account):
    if account.expires_at < datetime.now():
        raise HTTPException(
            status_code=401,
            detail=f"OAuth token expired for {account.platform}. Please re-authenticate."
        )
```

---

## 4. Frontend Components Not Loading

### Symptom
Publishing components don't render or show blank screen.

### Diagnosis

**Check Browser Console**:
```
F12 → Console Tab
Look for:
- JavaScript errors
- Failed API requests
- React errors
```

**Check Network Tab**:
```
F12 → Network Tab
Look for:
- Failed API calls (red)
- 401/403 errors (auth issues)
- 404 errors (wrong endpoints)
```

**Check Clerk Authentication**:
```javascript
// In browser console
console.log(window.Clerk.user);
console.log(window.Clerk.session);
```

### Solutions

**Solution 1: Check Component Imports**
```typescript
// Verify import paths are correct
import PublishNowButton from '@/components/publishing/PublishNowButton';
import SchedulePostModal from '@/components/publishing/SchedulePostModal';

// Not:
import PublishNowButton from 'components/publishing/PublishNowButton'; // ❌
```

**Solution 2: Verify API URL**
```typescript
// Check environment variable
console.log(process.env.NEXT_PUBLIC_API_URL);

// Should be: http://localhost:8000

// In .env.local:
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Solution 3: Check Clerk Provider**
```tsx
// In app/layout.tsx
import { ClerkProvider } from '@clerk/nextjs';

export default function RootLayout({ children }) {
  return (
    <ClerkProvider>
      {children}
    </ClerkProvider>
  );
}
```

**Solution 4: Verify Dependencies**
```bash
cd frontend

# Check if packages are installed
npm list @clerk/nextjs lucide-react

# Reinstall if missing
npm install
```

**Solution 5: Clear Next.js Cache**
```bash
cd frontend

# Delete cache
rm -rf .next

# Rebuild
npm run dev
```

---

## 5. Database Connection Issues

### Symptom
```
sqlalchemy.exc.OperationalError: could not connect to server
```

### Diagnosis

**Check PostgreSQL Service**:
```bash
docker-compose ps postgres

# Should show: running
```

**Check Database Credentials**:
```bash
# In backend/.env
echo $DATABASE_URL

# Should be:
# postgresql://user:password@localhost:5432/ai_growth_manager
```

**Test Connection**:
```python
# In backend container
python -c "
from sqlalchemy import create_engine
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
conn = engine.connect()
print('Connected!')
conn.close()
"
```

### Solutions

**Solution 1: Restart Database**
```bash
docker-compose restart postgres
```

**Solution 2: Check Database Exists**
```bash
docker-compose exec postgres psql -U postgres -l

# Look for: ai_growth_manager
```

**Solution 3: Create Database**
```bash
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE ai_growth_manager;"
```

**Solution 4: Run Migrations**
```bash
cd backend
alembic upgrade head
```

**Solution 5: Check Connection Pool**
```python
# In Python console
from app.db.database import engine

pool = engine.pool
print(f"Pool size: {pool.size()}")
print(f"Checked out: {pool.checkedout()}")
print(f"Overflow: {pool.overflow()}")
print(f"Checkedin: {pool.checkedin()}")

# If all connections checked out:
# Increase pool size in app/db/database.py
```

---

## 6. Celery Task Stuck in "queued" Status

### Symptom
ScheduledPost status shows "queued" but never changes to "publishing" or "published".

### Diagnosis

**Check Task Status**:
```python
from celery.result import AsyncResult
from app.core.celery_app import celery_app

result = AsyncResult(task_id, app=celery_app)
print(f"State: {result.state}")
print(f"Info: {result.info}")
```

**Check Celery Queue**:
```bash
docker-compose exec celery_worker celery -A app.core.celery_app inspect active

# Shows currently executing tasks
```

**Check for Stuck Tasks**:
```bash
docker-compose exec celery_worker celery -A app.core.celery_app inspect reserved

# Shows tasks waiting in queue
```

### Solutions

**Solution 1: Revoke Stuck Task**
```python
from celery.result import AsyncResult
from app.core.celery_app import celery_app

result = AsyncResult(task_id, app=celery_app)
result.revoke(terminate=True)
```

**Solution 2: Purge Queue**
```bash
docker-compose exec celery_worker celery -A app.core.celery_app purge

# WARNING: This deletes ALL queued tasks
```

**Solution 3: Restart Worker with Purge**
```bash
docker-compose stop celery_worker
docker-compose exec redis redis-cli FLUSHDB
docker-compose start celery_worker
```

**Solution 4: Increase Worker Concurrency**
```bash
# In docker-compose.yml
celery_worker:
  command: celery -A app.core.celery_app worker --loglevel=info --concurrency=4

# Default is 1, increase to 4
```

---

## 7. Image Upload Issues

### Symptom
Posts with images fail to publish.

### Diagnosis

**Check File Size**:
```javascript
// Frontend: Check before upload
if (file.size > 5 * 1024 * 1024) { // 5MB
  alert('File too large. Max 5MB.');
}
```

**Check File Type**:
```javascript
const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
if (!allowedTypes.includes(file.type)) {
  alert('Invalid file type. Use JPEG, PNG, or GIF.');
}
```

### Solutions

**Solution 1: Compress Images**
```javascript
// Frontend: Compress before upload
async function compressImage(file) {
  const img = await createImageBitmap(file);
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  // Resize to max 1920x1080
  const maxWidth = 1920;
  const maxHeight = 1080;
  let { width, height } = img;
  
  if (width > maxWidth || height > maxHeight) {
    const ratio = Math.min(maxWidth / width, maxHeight / height);
    width *= ratio;
    height *= ratio;
  }
  
  canvas.width = width;
  canvas.height = height;
  ctx.drawImage(img, 0, 0, width, height);
  
  return new Promise(resolve => {
    canvas.toBlob(resolve, 'image/jpeg', 0.8);
  });
}
```

**Solution 2: Use CDN for Images**
```python
# Backend: Upload to S3/CDN first
async def upload_image_to_cdn(image_data):
    # Upload to S3
    # Return CDN URL
    # Pass URL to publisher instead of raw data
    pass
```

---

## 8. Timezone Issues

### Symptom
Posts publish at wrong time or dates display incorrectly.

### Diagnosis

**Check Timezone Settings**:
```python
# Backend
from datetime import datetime
import pytz

print(f"Server time: {datetime.now()}")
print(f"UTC time: {datetime.utcnow()}")
print(f"Timezone: {pytz.timezone('UTC')}")
```

**Check Database Timestamps**:
```sql
SELECT 
  id,
  scheduled_for,
  scheduled_for AT TIME ZONE 'UTC' as utc_time,
  scheduled_for AT TIME ZONE 'America/Los_Angeles' as pst_time
FROM scheduled_posts;
```

### Solutions

**Solution 1: Always Use UTC**
```typescript
// Frontend: Convert to UTC before sending
const localTime = new Date('2025-10-20T09:00:00'); // User's local time
const utcTime = localTime.toISOString(); // Converts to UTC

// Send to API
fetch('/api/v2/schedule', {
  body: JSON.stringify({
    scheduled_for: utcTime, // "2025-10-20T16:00:00Z" (if PST)
  })
});
```

**Solution 2: Display in User's Timezone**
```typescript
// Frontend: Convert from UTC to local for display
const utcTime = "2025-10-20T16:00:00Z";
const localTime = new Date(utcTime);

console.log(localTime.toLocaleString()); // "10/20/2025, 9:00:00 AM" (PST)
```

**Solution 3: Store User Timezone**
```sql
-- Add timezone column
ALTER TABLE users ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC';

-- Use for display
SELECT 
  scheduled_for AT TIME ZONE timezone as local_time
FROM scheduled_posts
JOIN users ON scheduled_posts.user_id = users.id;
```

---

## 9. Memory Issues

### Symptom
```
MemoryError: Unable to allocate memory
```

### Diagnosis

**Check Memory Usage**:
```bash
# Docker containers
docker stats

# Look for high memory usage in:
# - celery_worker
# - backend
# - postgres
```

**Check Connection Pool**:
```python
from app.db.database import engine

pool = engine.pool
print(f"Size: {pool.size()}")
print(f"Checked out: {pool.checkedout()}")
```

### Solutions

**Solution 1: Increase Docker Memory**
```bash
# In Docker Desktop
# Settings → Resources → Memory → 4GB (or higher)
```

**Solution 2: Reduce Connection Pool**
```python
# In app/db/database.py
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,        # Reduce from 10
    max_overflow=10     # Reduce from 20
)
```

**Solution 3: Enable Query Caching**
```python
# Cache expensive queries
from app.core.query_cache import analytics_cache

@analytics_cache.cached(ttl=300)
def get_analytics(business_id: int):
    # Expensive query
    return results
```

**Solution 4: Add Pagination**
```python
# Instead of loading all posts
posts = db.query(PublishedPost).all()  # ❌

# Use pagination
posts = db.query(PublishedPost).limit(50).offset(0).all()  # ✅
```

---

## 10. Platform-Specific Issues

### LinkedIn

**Issue**: Posts not appearing on profile
**Solution**: Use UGC Posts API (person URN) instead of Share API

**Issue**: Threading not working
**Solution**: Check post character count > 3000 and verify threading logic

### Twitter

**Issue**: Thread replies not linking
**Solution**: Verify `in_reply_to_tweet_id` is set correctly

**Issue**: Character count off
**Solution**: URLs count as 23 characters regardless of actual length

### Facebook

**Issue**: Missing page_id
**Solution**: Add `page_id` to `platform_params`:
```json
{
  "platform_params": {
    "facebook": {
      "page_id": "123456789"
    }
  }
}
```

### Instagram

**Issue**: Posts failing
**Solution**: Ensure `instagram_account_id` is provided and account is business account

---

## Logging and Debugging

### Enable Debug Logging

**Backend**:
```python
# In app/core/config.py
DEBUG = True

# In app/db/database.py
engine = create_engine(..., echo=True)  # SQL logging
```

**Celery**:
```bash
# In docker-compose.yml
celery_worker:
  command: celery -A app.core.celery_app worker --loglevel=debug
```

**Frontend**:
```typescript
// Add to components
console.log('Publishing:', { content, platforms, businessId });
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f celery_worker
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 celery_worker
```

---

## Quick Reference

### Health Checks

```bash
# Check all services
docker-compose ps

# Check API health
curl http://localhost:8000/health

# Check Redis
docker-compose exec redis redis-cli PING

# Check PostgreSQL
docker-compose exec postgres pg_isready

# Check Celery
docker-compose exec celery_worker celery -A app.core.celery_app inspect ping
```

### Common Commands

```bash
# Restart everything
docker-compose restart

# Rebuild and restart
docker-compose up -d --build

# View logs
docker-compose logs -f

# Clear Redis
docker-compose exec redis redis-cli FLUSHDB

# Run migrations
cd backend && alembic upgrade head

# Test publishing
curl -X POST http://localhost:8000/api/v2/publish \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"content":"test","platforms":["linkedin"]}'
```

---

## Getting Help

1. **Check Logs First**: Most issues show up in logs
2. **Search Error Message**: Google the exact error message
3. **Check GitHub Issues**: See if others have same problem
4. **Ask for Help**: Provide logs, error messages, and steps to reproduce

---

**Last Updated**: October 14, 2025
