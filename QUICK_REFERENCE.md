# Publishing System Quick Reference

## 🚀 Quick Start

### Publish Immediately
```bash
curl -X POST "http://localhost:8000/api/v2/publish" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello world!",
    "platforms": ["linkedin", "twitter"]
  }'
```

### Schedule a Post
```bash
curl -X POST "http://localhost:8000/api/v2/schedule" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Scheduled post",
    "platforms": ["linkedin"],
    "scheduled_for": "2025-10-20T10:00:00Z"
  }'
```

### List Scheduled Posts
```bash
curl "http://localhost:8000/api/v2/scheduled?business_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Cancel Scheduled Post
```bash
curl -X DELETE "http://localhost:8000/api/v2/schedule/123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📱 Frontend Components

### PublishNowButton
```tsx
import PublishNowButton from '@/components/publishing/PublishNowButton';

<PublishNowButton
  content="Post content"
  platforms={['linkedin', 'twitter']}
  businessId={1}
  onSuccess={(results) => console.log('Published!', results)}
  variant="primary"
  size="md"
/>
```

### SchedulePostModal
```tsx
import SchedulePostModal from '@/components/publishing/SchedulePostModal';

<SchedulePostModal
  isOpen={true}
  onClose={() => setOpen(false)}
  content="Post content"
  platforms={['linkedin']}
  businessId={1}
  onScheduled={(id) => console.log('Scheduled:', id)}
/>
```

### Scheduled Posts Page
```
Navigate to: /dashboard/scheduled
```

---

## 🔧 Common Commands

### Check Services
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f celery_worker
docker-compose logs -f backend
```

### Restart Services
```bash
# All
docker-compose restart

# Specific
docker-compose restart celery_worker celery_beat
```

### Database Migrations
```bash
cd backend
alembic upgrade head
alembic revision -m "description"
```

### Clear Redis Cache
```bash
docker-compose exec redis redis-cli FLUSHDB
```

---

## 🐛 Troubleshooting

### Posts Not Publishing
```bash
# Check Celery services
docker-compose ps celery_worker celery_beat

# View worker logs
docker-compose logs -f celery_worker

# Restart if needed
docker-compose restart celery_worker celery_beat
```

### Rate Limited (429 Error)
```bash
# Wait for reset (check X-RateLimit-Reset header)
# OR clear cache (dev only)
docker-compose exec redis redis-cli FLUSHDB
```

### OAuth Token Expired
```javascript
// Redirect to re-authenticate
window.location.href = `/api/oauth/${platform}/authorize`;
```

### Frontend Not Loading
```bash
# Check API URL
echo $NEXT_PUBLIC_API_URL

# Clear Next.js cache
cd frontend
rm -rf .next
npm run dev
```

### Database Connection Issues
```bash
# Restart database
docker-compose restart postgres

# Check database exists
docker-compose exec postgres psql -U postgres -l

# Run migrations
cd backend && alembic upgrade head
```

---

## 📊 Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /publish | 20 | 1 hour |
| POST /publish/multi-platform | 10 | 1 hour |
| POST /schedule | 50 | 1 hour |
| GET /scheduled | 100 | 1 minute |
| DELETE /schedule/{id} | 100 | 1 hour |

---

## 🔑 Environment Variables

### Backend (.env)
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379/0
CLERK_SECRET_KEY=sk_test_...
LINKEDIN_CLIENT_ID=...
LINKEDIN_CLIENT_SECRET=...
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
META_APP_ID=...
META_APP_SECRET=...
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
```

---

## 📈 Performance Metrics

- **Query Time**: ~10-20ms (with indexes)
- **Connection Overhead**: ~5ms (with pooling)
- **Cache Hit Rate**: 80% (analytics queries)
- **API Response**: ~30ms (excluding external APIs)

---

## 🏗️ Architecture

```
Frontend → API Endpoints → Publishers → Platforms
              ↓
         Database + Redis
              ↓
    Celery (for scheduled posts)
```

---

## 📁 Key Files

### Backend
- `app/api/v2/endpoints/publishing.py` - API endpoints
- `app/services/publishers/` - Platform publishers
- `app/core/celery_app.py` - Celery config
- `app/core/query_cache.py` - Query caching
- `app/db/database.py` - Connection pooling

### Frontend
- `components/publishing/PublishNowButton.tsx`
- `components/publishing/SchedulePostModal.tsx`
- `app/dashboard/scheduled/page.tsx`

### Documentation
- `docs/PUBLISHING_API_V2.md` - Complete API reference
- `docs/TROUBLESHOOTING_PUBLISHING.md` - Issue resolution
- `frontend/PUBLISHING_COMPONENTS_GUIDE.md` - Integration guide
- `SESSION_17_COMPLETE.md` - Full session summary

---

## 🧪 Testing

### Manual Testing
```bash
# Test publish
curl -X POST "http://localhost:8000/api/v2/publish" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"content":"test","platforms":["linkedin"]}'

# Test schedule
curl -X POST "http://localhost:8000/api/v2/schedule" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"content":"test","platforms":["linkedin"],"scheduled_for":"2025-10-20T10:00:00Z"}'
```

### Performance Testing
```bash
cd backend
python test_performance.py
```

---

## 🚦 Health Checks

```bash
# API health
curl http://localhost:8000/health

# Redis
docker-compose exec redis redis-cli PING

# PostgreSQL
docker-compose exec postgres pg_isready

# Celery
docker-compose exec celery_worker celery -A app.core.celery_app inspect ping
```

---

## 📚 Documentation Links

- **API Reference**: [docs/PUBLISHING_API_V2.md](./docs/PUBLISHING_API_V2.md)
- **Troubleshooting**: [docs/TROUBLESHOOTING_PUBLISHING.md](./docs/TROUBLESHOOTING_PUBLISHING.md)
- **Component Guide**: [frontend/PUBLISHING_COMPONENTS_GUIDE.md](./frontend/PUBLISHING_COMPONENTS_GUIDE.md)
- **Session Summary**: [SESSION_17_COMPLETE.md](./SESSION_17_COMPLETE.md)

---

## 🎯 Common Tasks

### Add New Platform
1. Create publisher in `app/services/publishers/`
2. Add to `PublishingService.publish_to_platform()`
3. Add OAuth flow in `app/api/oauth/`
4. Update frontend platform config

### Change Rate Limits
1. Edit `@limiter.limit()` in `app/api/v2/endpoints/publishing.py`
2. Restart backend

### Clear All Scheduled Posts
```sql
-- In PostgreSQL
DELETE FROM scheduled_posts WHERE status = 'pending';
```

### Export Published Posts
```sql
-- In PostgreSQL
COPY (
  SELECT * FROM published_posts 
  WHERE published_at >= '2025-10-01'
) TO '/tmp/posts.csv' CSV HEADER;
```

---

## ⚡ Performance Tips

1. **Use Query Cache**: Wrap expensive queries with `@cache.cached()`
2. **Batch Operations**: Publish to multiple platforms in one request
3. **Schedule Off-Peak**: Schedule posts for off-peak hours
4. **Monitor Limits**: Track rate limit headers
5. **Optimize Content**: Keep posts under platform limits to avoid threading

---

## 🔐 Security Best Practices

1. **Token Storage**: Never expose Clerk tokens in logs
2. **OAuth Tokens**: Store encrypted in database
3. **Rate Limiting**: Prevents abuse
4. **Redis State**: Auto-expires OAuth state (10 min TTL)
5. **HTTPS Only**: Use HTTPS in production

---

## 📞 Support

For issues:
1. Check [TROUBLESHOOTING_PUBLISHING.md](./docs/TROUBLESHOOTING_PUBLISHING.md)
2. Check logs: `docker-compose logs -f`
3. Search error message in documentation
4. Check GitHub issues

---

**Last Updated**: October 14, 2025  
**Version**: v2  
**Status**: Production Ready ✅
