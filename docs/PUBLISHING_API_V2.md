# Publishing API v2 Documentation

## Overview

The Publishing API v2 provides endpoints for publishing content to social media platforms (LinkedIn, Twitter, Facebook, Instagram) both immediately and scheduled for future dates.

**Base URL**: `http://localhost:8000` (development) or your production URL

**API Version**: v2

**Last Updated**: October 14, 2025

---

## Authentication

All endpoints require Bearer token authentication using Clerk JWT tokens.

**Header**:
```
Authorization: Bearer <clerk_jwt_token>
```

**Example**:
```bash
curl -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..." \
     http://localhost:8000/api/v2/publish
```

---

## Rate Limits

Rate limits are enforced using SlowAPI with Redis backend:

| Endpoint | Limit | Window | Scope |
|----------|-------|--------|-------|
| `POST /api/v2/publish` | 20 requests | 1 hour | Per user |
| `POST /api/v2/publish/multi-platform` | 10 requests | 1 hour | Per user |
| `POST /api/v2/schedule` | 50 requests | 1 hour | Per user |
| `DELETE /api/v2/schedule/{post_id}` | 100 requests | 1 hour | Per user |
| `GET /api/v2/scheduled` | 100 requests | 1 minute | Per user |

**Rate Limit Headers**:
```
X-RateLimit-Limit: 20
X-RateLimit-Remaining: 15
X-RateLimit-Reset: 1634567890
```

When rate limit is exceeded:
```json
{
  "detail": "Rate limit exceeded: 20 per 1 hour"
}
```
**Status Code**: `429 Too Many Requests`

---

## Endpoints

### 1. Publish Now

Publish content immediately to one or more social media platforms.

**Endpoint**: `POST /api/v2/publish`

**Rate Limit**: 20 requests/hour per user

**Request Body**:
```json
{
  "content": "Check out our new product launch! 🚀",
  "platforms": ["linkedin", "twitter"],
  "platform_params": {
    "facebook": {
      "page_id": "123456789"
    },
    "instagram": {
      "instagram_account_id": "987654321"
    }
  }
}
```

**Request Fields**:
- `content` (string, required): The post content to publish
- `platforms` (array, required): List of platforms to publish to
  - Valid values: `"linkedin"`, `"twitter"`, `"facebook"`, `"instagram"`
- `platform_params` (object, optional): Platform-specific parameters
  - Facebook: `page_id` (required for page posts)
  - Instagram: `instagram_account_id` (required)

**Response** (200 OK):
```json
{
  "success": true,
  "results": [
    {
      "platform": "linkedin",
      "success": true,
      "post_id": "urn:li:share:7123456789",
      "url": "https://www.linkedin.com/feed/update/urn:li:share:7123456789"
    },
    {
      "platform": "twitter",
      "success": true,
      "post_id": "1234567890123456789",
      "url": "https://twitter.com/user/status/1234567890123456789"
    }
  ],
  "published_post_ids": [101, 102]
}
```

**Response Fields**:
- `success` (boolean): Overall success status
- `results` (array): Array of publishing results per platform
  - `platform` (string): Platform name
  - `success` (boolean): Whether publishing succeeded
  - `post_id` (string): Platform's post ID
  - `url` (string, optional): Direct URL to the published post
  - `error` (string, optional): Error message if failed
- `published_post_ids` (array): Database IDs of created PublishedPost records

**Error Responses**:

**400 Bad Request** - Invalid request:
```json
{
  "detail": "No platforms specified"
}
```

**401 Unauthorized** - Missing or invalid auth token:
```json
{
  "detail": "Not authenticated"
}
```

**404 Not Found** - No social accounts connected:
```json
{
  "detail": "No social account found for platform: linkedin"
}
```

**500 Internal Server Error** - Server error:
```json
{
  "detail": "Failed to publish: <error_message>"
}
```

**Example cURL**:
```bash
curl -X POST "http://localhost:8000/api/v2/publish" \
  -H "Authorization: Bearer $CLERK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello world!",
    "platforms": ["linkedin", "twitter"]
  }'
```

---

### 2. Multi-Platform Publish

Alternative endpoint for publishing to multiple platforms with enhanced error handling.

**Endpoint**: `POST /api/v2/publish/multi-platform`

**Rate Limit**: 10 requests/hour per user

**Request/Response**: Same as `POST /api/v2/publish`

**Difference**: This endpoint is optimized for multi-platform publishing with better error recovery and partial success handling.

---

### 3. Schedule Post

Schedule content for future publishing to one or more platforms.

**Endpoint**: `POST /api/v2/schedule`

**Rate Limit**: 50 requests/hour per user

**Request Body**:
```json
{
  "content": "Happy New Year 2026! 🎉",
  "platforms": ["linkedin", "twitter", "facebook"],
  "scheduled_for": "2026-01-01T00:00:00Z",
  "platform_params": {
    "facebook": {
      "page_id": "123456789"
    }
  }
}
```

**Request Fields**:
- `content` (string, required): Post content
- `platforms` (array, required): Platforms to publish to
- `scheduled_for` (string, required): ISO 8601 datetime (UTC)
  - Must be in the future
  - Format: `YYYY-MM-DDTHH:MM:SSZ`
- `platform_params` (object, optional): Platform-specific parameters

**Response** (200 OK):
```json
{
  "success": true,
  "scheduled_post_id": 45,
  "celery_task_id": "abc123-def456-ghi789",
  "scheduled_for": "2026-01-01T00:00:00Z",
  "platforms": ["linkedin", "twitter", "facebook"]
}
```

**Response Fields**:
- `success` (boolean): Whether scheduling succeeded
- `scheduled_post_id` (integer): Database ID of ScheduledPost record
- `celery_task_id` (string): Celery task ID for tracking
- `scheduled_for` (string): Confirmed scheduled datetime
- `platforms` (array): Platforms the post will be published to

**Error Responses**:

**400 Bad Request** - Invalid datetime:
```json
{
  "detail": "scheduled_for must be in the future"
}
```

**Example cURL**:
```bash
curl -X POST "http://localhost:8000/api/v2/schedule" \
  -H "Authorization: Bearer $CLERK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Scheduled post content",
    "platforms": ["linkedin"],
    "scheduled_for": "2025-10-20T10:00:00Z"
  }'
```

---

### 4. List Scheduled Posts

Get all scheduled posts for a business.

**Endpoint**: `GET /api/v2/scheduled`

**Rate Limit**: 100 requests/minute per user

**Query Parameters**:
- `business_id` (integer, required): Business ID to filter by

**Example Request**:
```
GET /api/v2/scheduled?business_id=1
```

**Response** (200 OK):
```json
{
  "scheduled_posts": [
    {
      "id": 45,
      "content_text": "Happy New Year 2026! 🎉",
      "platforms": ["linkedin", "twitter"],
      "scheduled_for": "2026-01-01T00:00:00Z",
      "status": "pending",
      "celery_task_id": "abc123-def456-ghi789",
      "created_at": "2025-10-14T12:00:00Z"
    },
    {
      "id": 46,
      "content_text": "Weekend vibes 🌴",
      "platforms": ["instagram", "facebook"],
      "scheduled_for": "2025-10-19T09:00:00Z",
      "status": "queued",
      "celery_task_id": "xyz789-abc123-def456",
      "created_at": "2025-10-14T13:30:00Z"
    }
  ]
}
```

**Response Fields**:
- `scheduled_posts` (array): List of scheduled posts
  - `id` (integer): Scheduled post ID
  - `content_text` (string): Post content
  - `platforms` (array): Target platforms
  - `scheduled_for` (string): Scheduled datetime (ISO 8601)
  - `status` (string): Current status
    - `"pending"`: Waiting to be published
    - `"queued"`: Celery task queued
    - `"publishing"`: Currently publishing
    - `"published"`: Successfully published
    - `"cancelled"`: Cancelled by user
    - `"failed"`: Publishing failed
  - `celery_task_id` (string): Celery task ID
  - `created_at` (string): When post was scheduled

**Example cURL**:
```bash
curl "http://localhost:8000/api/v2/scheduled?business_id=1" \
  -H "Authorization: Bearer $CLERK_TOKEN"
```

---

### 5. Cancel Scheduled Post

Cancel a scheduled post before it's published.

**Endpoint**: `DELETE /api/v2/schedule/{post_id}`

**Rate Limit**: 100 requests/hour per user

**Path Parameters**:
- `post_id` (integer): ID of the scheduled post to cancel

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Scheduled post cancelled successfully",
  "post_id": 45
}
```

**Error Responses**:

**404 Not Found** - Post doesn't exist:
```json
{
  "detail": "Scheduled post not found"
}
```

**400 Bad Request** - Post already published:
```json
{
  "detail": "Cannot cancel post with status: published"
}
```

**Example cURL**:
```bash
curl -X DELETE "http://localhost:8000/api/v2/schedule/45" \
  -H "Authorization: Bearer $CLERK_TOKEN"
```

---

## Publisher Features

### LinkedIn Publisher

**Features**:
- UGC Posts API v2
- Auto-threading for posts > 3000 characters
- Split on sentence boundaries
- Link to previous post in thread
- Supports images (future enhancement)

**Content Limits**:
- Single post: 3000 characters
- Thread posts: Split automatically

**Example Thread**:
```
Post 1: "This is a long LinkedIn post that will be automatically
        split into multiple posts..." (3000 chars)
        
Post 2: "Continuing from previous post... [rest of content]" 
        (link to Post 1)
```

### Twitter Publisher

**Features**:
- Twitter API v2
- Auto-threading for tweets > 280 characters
- Split on word boundaries
- Reply chain for threads
- Handles @mentions and hashtags correctly

**Content Limits**:
- Single tweet: 280 characters
- Thread tweets: Split automatically

**Example Thread**:
```
Tweet 1: "This is a Twitter thread about AI..." (280 chars)
Tweet 2: "The key to AI success is..." (reply to Tweet 1)
Tweet 3: "In conclusion..." (reply to Tweet 2)
```

### Meta Publisher (Facebook & Instagram)

**Features**:
- Facebook Graph API
- Instagram Graph API
- Page posts for Facebook
- Business account posts for Instagram
- Requires page_id and instagram_account_id

**Content Limits**:
- Facebook: 63,206 characters
- Instagram: 2,200 characters

**Platform Parameters**:
```json
{
  "facebook": {
    "page_id": "123456789"  // Required for page posts
  },
  "instagram": {
    "instagram_account_id": "987654321"  // Required
  }
}
```

---

## Scheduling System

### Celery Architecture

**Components**:
1. **Celery Beat**: Scheduler that monitors ScheduledPost table
2. **Celery Worker**: Executes publishing tasks
3. **Redis**: Message broker and result backend

**Flow**:
```
User schedules post
       ↓
ScheduledPost created in DB
       ↓
Celery task created with ETA
       ↓
Celery Beat monitors tasks
       ↓
At scheduled time → Worker executes task
       ↓
Publisher publishes to platforms
       ↓
Status updated to "published"
```

**Task Retry Policy**:
- Max retries: 3
- Retry delay: Exponential backoff
- Retry on: Rate limit errors, network errors

### Timezone Support

All timestamps are stored and processed in UTC. Frontend should convert to user's local timezone for display.

**Example**:
```javascript
// Schedule for 9 AM user's local time
const localTime = new Date('2025-10-20T09:00:00');
const utcTime = localTime.toISOString(); // "2025-10-20T16:00:00Z" (if PST)

// Send to API
fetch('/api/v2/schedule', {
  body: JSON.stringify({
    scheduled_for: utcTime,
    // ...
  })
});
```

---

## Error Handling

### Common Error Patterns

**1. Authentication Errors**
```json
{
  "detail": "Not authenticated"
}
```
**Solution**: Refresh Clerk token and retry

**2. Rate Limit Errors**
```json
{
  "detail": "Rate limit exceeded: 20 per 1 hour"
}
```
**Solution**: Wait until X-RateLimit-Reset timestamp

**3. Platform Errors**
```json
{
  "platform": "linkedin",
  "success": false,
  "error": "OAuth token expired"
}
```
**Solution**: Re-authenticate with platform

**4. Validation Errors**
```json
{
  "detail": [
    {
      "loc": ["body", "platforms"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
**Solution**: Fix request body according to schema

### Partial Success

For multi-platform publishing, some platforms may succeed while others fail:

```json
{
  "success": true,  // Overall success if ANY platform succeeded
  "results": [
    {
      "platform": "linkedin",
      "success": true,
      "post_id": "urn:li:share:123"
    },
    {
      "platform": "twitter",
      "success": false,
      "error": "OAuth token expired"
    }
  ]
}
```

**Handling**: Check individual platform results and inform user.

---

## Best Practices

### 1. Content Optimization

**Character Limits**:
- Respect platform limits to avoid truncation
- Use publisher auto-threading for long content
- Test with maximum length content

**Platform-Specific**:
```javascript
const contentLimits = {
  linkedin: 3000,   // Single post
  twitter: 280,     // Single tweet
  facebook: 63206,  // Very long
  instagram: 2200   // Medium length
};

// Check before publishing
if (content.length > contentLimits[platform]) {
  console.warn(`Content will be split into thread`);
}
```

### 2. Error Recovery

**Retry Failed Posts**:
```javascript
async function publishWithRetry(content, platforms, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch('/api/v2/publish', {
        method: 'POST',
        body: JSON.stringify({ content, platforms })
      });
      
      if (response.ok) return await response.json();
      
      if (response.status === 429) {
        // Rate limit - wait and retry
        const resetTime = response.headers.get('X-RateLimit-Reset');
        await waitUntil(resetTime);
        continue;
      }
      
      throw new Error(`HTTP ${response.status}`);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await sleep(Math.pow(2, i) * 1000); // Exponential backoff
    }
  }
}
```

### 3. Scheduled Post Management

**Check Status Before Operations**:
```javascript
// Don't try to cancel published posts
if (post.status === 'published' || post.status === 'publishing') {
  alert('Cannot cancel - post already published');
  return;
}

// Warn about imminent posts
const timeUntil = new Date(post.scheduled_for) - new Date();
if (timeUntil < 5 * 60 * 1000) { // 5 minutes
  if (!confirm('This post will publish in less than 5 minutes. Cancel?')) {
    return;
  }
}
```

### 4. Rate Limit Management

**Track Limits Client-Side**:
```javascript
class RateLimitTracker {
  constructor() {
    this.limits = {};
  }
  
  updateFromHeaders(endpoint, headers) {
    this.limits[endpoint] = {
      limit: parseInt(headers.get('X-RateLimit-Limit')),
      remaining: parseInt(headers.get('X-RateLimit-Remaining')),
      reset: parseInt(headers.get('X-RateLimit-Reset'))
    };
  }
  
  canMakeRequest(endpoint) {
    const limit = this.limits[endpoint];
    if (!limit) return true;
    
    if (limit.remaining === 0) {
      const now = Date.now() / 1000;
      return now >= limit.reset;
    }
    
    return true;
  }
  
  getWaitTime(endpoint) {
    const limit = this.limits[endpoint];
    if (!limit || limit.remaining > 0) return 0;
    
    const now = Date.now() / 1000;
    return Math.max(0, limit.reset - now);
  }
}
```

---

## Testing

### Manual Testing

**1. Test Publish Now**:
```bash
# Test single platform
curl -X POST "http://localhost:8000/api/v2/publish" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Test post from API",
    "platforms": ["linkedin"]
  }'

# Test multi-platform
curl -X POST "http://localhost:8000/api/v2/publish" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Test post to all platforms",
    "platforms": ["linkedin", "twitter", "facebook"]
  }'
```

**2. Test Scheduling**:
```bash
# Schedule for 5 minutes from now
FUTURE_TIME=$(date -u -v+5M +"%Y-%m-%dT%H:%M:%SZ")

curl -X POST "http://localhost:8000/api/v2/schedule" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"content\": \"Scheduled test post\",
    \"platforms\": [\"linkedin\"],
    \"scheduled_for\": \"$FUTURE_TIME\"
  }"
```

**3. Test List & Cancel**:
```bash
# List scheduled posts
curl "http://localhost:8000/api/v2/scheduled?business_id=1" \
  -H "Authorization: Bearer $TOKEN"

# Cancel a post
curl -X DELETE "http://localhost:8000/api/v2/schedule/45" \
  -H "Authorization: Bearer $TOKEN"
```

### Automated Testing

See `backend/tests/test_publishing_e2e.py` for comprehensive test suite.

---

## Troubleshooting

See [TROUBLESHOOTING_PUBLISHING.md](./TROUBLESHOOTING_PUBLISHING.md) for detailed troubleshooting guide.

**Quick Fixes**:

**Posts Not Publishing**:
1. Check Celery worker is running: `docker-compose ps celery_worker`
2. Check Celery beat is running: `docker-compose ps celery_beat`
3. View worker logs: `docker-compose logs -f celery_worker`

**Rate Limit Issues**:
1. Check remaining requests in response headers
2. Wait until reset time
3. Consider implementing exponential backoff

**Authentication Errors**:
1. Verify Clerk token is valid
2. Check OAuth tokens haven't expired
3. Re-authenticate with platforms if needed

---

## Version History

### v2 (October 2025)
- ✅ Initial release
- ✅ Multi-platform publishing
- ✅ Scheduled posts with Celery
- ✅ Rate limiting with Redis
- ✅ Auto-threading for LinkedIn and Twitter

### Planned Features
- 🔄 Image/media upload support
- 🔄 Post analytics and insights
- 🔄 Bulk scheduling
- 🔄 Content calendar integration
- 🔄 AI-powered content suggestions

---

## Support

For issues or questions:
1. Check [TROUBLESHOOTING_PUBLISHING.md](./TROUBLESHOOTING_PUBLISHING.md)
2. Review test files in `backend/tests/`
3. Check Celery logs for scheduling issues
4. Verify OAuth tokens are valid

---

**Last Updated**: October 14, 2025  
**API Version**: v2  
**Maintained By**: AI Growth Manager Team
