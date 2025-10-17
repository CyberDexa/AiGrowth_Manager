# Background Analytics Scheduler - Quick Start Guide

## Overview
The analytics scheduler automatically syncs social media analytics data from LinkedIn, Twitter, and Meta (Facebook/Instagram) on a regular schedule.

## Features
- ✅ **Automatic Hourly Sync**: Syncs all businesses every hour at :00
- ✅ **Manual Trigger**: On-demand sync via API endpoint
- ✅ **Per-Business Scheduling**: Custom sync schedules for individual businesses
- ✅ **Job Management**: View, add, and remove scheduled jobs
- ✅ **Graceful Shutdown**: Waits for running jobs before stopping

## Quick Commands

### Check Scheduler Status
```bash
curl http://localhost:8003/api/v1/scheduler/status
```

### Trigger Manual Sync (All Businesses)
```bash
curl -X POST http://localhost:8003/api/v1/scheduler/trigger-sync
```

### Trigger Manual Sync (Single Business)
```bash
curl -X POST "http://localhost:8003/api/v1/scheduler/trigger-sync?business_id=1"
```

### List All Scheduled Jobs
```bash
curl http://localhost:8003/api/v1/scheduler/jobs
```

### Schedule Business Sync (Every 24 hours)
```bash
curl -X POST "http://localhost:8003/api/v1/scheduler/business/1/schedule?interval_hours=24"
```

### Remove Business Sync Schedule
```bash
curl -X DELETE http://localhost:8003/api/v1/scheduler/business/1/schedule
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/scheduler/status` | Get scheduler status and active jobs |
| GET | `/api/v1/scheduler/jobs` | List all scheduled jobs |
| POST | `/api/v1/scheduler/trigger-sync` | Trigger immediate sync |
| POST | `/api/v1/scheduler/business/{id}/schedule` | Add recurring sync for business |
| DELETE | `/api/v1/scheduler/business/{id}/schedule` | Remove business sync schedule |

## Monitoring

### View Logs
```bash
# In development (terminal where uvicorn is running)
# Look for these log messages:

INFO - Starting background scheduler
INFO - Added job: Sync all businesses (hourly at :00)
INFO - Background scheduler started successfully
INFO - Starting scheduled analytics sync for all businesses
INFO - Business 1 sync complete: 45/50 posts synced
INFO - Scheduled analytics sync complete: 145/200 posts synced, 5 failures in 120.45s
```

### Check Next Run Time
```bash
# The status endpoint shows when each job will run next
curl http://localhost:8003/api/v1/scheduler/status | jq '.status.jobs[0].next_run_time'
```

## Configuration

### Default Schedule
- **Frequency**: Every hour at :00 (e.g., 13:00, 14:00, 15:00)
- **Timezone**: UTC
- **Posts per Platform**: 100 (to respect rate limits)

### Customizing Schedule
Edit `app/scheduler.py`:

```python
# Change sync frequency (currently hourly)
scheduler.add_job(
    func=sync_all_businesses_job,
    trigger=CronTrigger(minute=0),  # Change this trigger
    id='sync_all_businesses',
    name='Sync Analytics for All Businesses',
    replace_existing=True
)

# Examples:
# Every 30 minutes: CronTrigger(minute='0,30')
# Every 6 hours: CronTrigger(hour='0,6,12,18', minute=0)
# Daily at 2 AM: CronTrigger(hour=2, minute=0)
# Business hours only: CronTrigger(hour='9-17', minute=0)
```

## Troubleshooting

### Scheduler Not Starting
**Symptom**: No logs about scheduler starting  
**Solution**:
1. Check if APScheduler is installed: `pip list | grep APScheduler`
2. Check logs for errors during startup
3. Verify database connection is working

### Jobs Not Running
**Symptom**: Scheduler running but jobs not executing  
**Check**:
```bash
curl http://localhost:8003/api/v1/scheduler/status
```
Verify `"running": true` and jobs have `next_run_time`

**Common Issues**:
- Clock skew (check server time matches UTC)
- Jobs paused/removed accidentally
- Application restarted (jobs reschedule on next hour)

### Sync Failures
**Symptom**: Jobs run but posts fail to sync  
**Check**:
1. Social account tokens are valid
2. Platform API rate limits not exceeded
3. Posts have valid `platform_post_id`

**View Errors**:
```bash
# Check analytics endpoint for error details
curl "http://localhost:8003/api/v1/analytics/refresh?business_id=1"
```

### High Memory/CPU Usage
**Symptom**: Server resources spike during sync  
**Solutions**:
- Reduce sync frequency (e.g., every 2 hours instead of hourly)
- Lower posts per platform limit (default: 100)
- Add more restrictive rate limits in fetchers

## Testing

### Run Tests
```bash
cd backend
source venv/bin/activate
pytest tests/ -v --cov
```

### Test Scheduler Manually
```python
# In Python shell
from app.scheduler import sync_all_businesses_job

# Run sync job once
sync_all_businesses_job()
```

## Production Deployment

### Prerequisites
- [ ] APScheduler installed (`pip install apscheduler==3.10.4`)
- [ ] Database accessible
- [ ] Social account tokens configured
- [ ] Logging configured

### Startup Checklist
1. Start application: `uvicorn app.main:app --host 0.0.0.0 --port 8003`
2. Verify scheduler started: Check logs for "Background scheduler started"
3. Check status endpoint: `curl http://localhost:8003/api/v1/scheduler/status`
4. Verify jobs scheduled: Should show at least 1 job
5. Wait for first run (next :00 of the hour)
6. Monitor logs during first sync

### Monitoring in Production
- Set up alerts for sync failures
- Monitor sync job duration (should be < 5 minutes for 10 businesses)
- Track rate limit errors
- Monitor database growth from analytics data

## Best Practices

### Rate Limiting
- Default: 100 posts per platform per sync
- Respects platform rate limits automatically
- Uses exponential backoff on errors

### Error Handling
- Individual post failures don't stop sync
- Failed syncs logged but don't crash scheduler
- Graceful degradation if platform unavailable

### Performance
- Sync runs in background thread (non-blocking)
- Database sessions properly closed
- Memory cleaned up after each job

## Advanced Usage

### Custom Sync Job
```python
from app.scheduler import scheduler, sync_business_job

# Add one-time job
scheduler.add_job(
    func=sync_business_job,
    args=[business_id],
    run_date='2025-10-13 15:30:00'  # Specific time
)
```

### Pause/Resume Scheduler
```python
from app.scheduler import scheduler

# Pause all jobs
scheduler.pause()

# Resume all jobs
scheduler.resume()
```

### Remove All Jobs
```python
from app.scheduler import scheduler

scheduler.remove_all_jobs()
```

## Support

### Documentation
- Full documentation: `SESSION_15_SUMMARY.md`
- API docs: http://localhost:8003/docs (when running)

### Logs
- Application logs contain all sync activity
- Look for keywords: "scheduler", "sync", "analytics"

### Common Questions

**Q: How often does it sync?**  
A: Every hour at :00 by default. Customizable via code or per-business scheduling.

**Q: Can I trigger sync manually?**  
A: Yes! Use `POST /api/v1/scheduler/trigger-sync` endpoint.

**Q: What happens if server restarts during sync?**  
A: Current job stops. Scheduler reschedules on next startup.

**Q: Does it respect API rate limits?**  
A: Yes! Each fetcher has built-in rate limit handling with exponential backoff.

**Q: How do I disable auto-sync?**  
A: Comment out `start_scheduler()` in `app/main.py` startup event.

---

**Version**: 1.0  
**Last Updated**: October 13, 2025  
**Session**: 15
