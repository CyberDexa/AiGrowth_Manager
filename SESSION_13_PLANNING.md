# ⏰ Session 13 Planning: Automated Scheduled Posting

**Status**: Planning Phase  
**Prerequisite**: Sessions 11-12 Complete  
**Estimated Duration**: 3-4 hours

---

## 🎯 OBJECTIVES

Enable users to schedule posts for future publishing with automated background job execution.

### Core Features
1. ✅ **Schedule Posts** - Set future publish date/time
2. ✅ **Background Jobs** - Celery or APScheduler
3. ✅ **Calendar View** - Visual scheduling interface
4. ✅ **Bulk Scheduling** - Schedule multiple posts
5. ✅ **Timezone Support** - User timezone handling
6. ✅ **Edit Scheduled** - Modify scheduled posts
7. ✅ **Queue Management** - View/manage scheduled posts

---

## 🏗️ ARCHITECTURE

### Background Job Options

**Option A: Celery + Redis**
- Pros: Industry standard, scalable, reliable
- Cons: More setup (Redis + Celery worker)
- Best for: Production

**Option B: APScheduler**
- Pros: Simple, Python-native, no external deps
- Cons: Single-process (doesn't scale)
- Best for: MVP

**Option C: Cloud Functions (AWS Lambda/Vercel)**
- Pros: Serverless, no infrastructure
- Cons: Cold starts, vendor lock-in
- Best for: Production (alternative)

### Scheduled Job Flow

```
┌─────────────────────────────────────────────────┐
│         SCHEDULED POSTING FLOW                  │
│                                                 │
│  1. User schedules post for Oct 15, 2pm        │
│       ↓                                         │
│  2. Backend creates published_post             │
│     • status: "scheduled"                      │
│     • scheduled_for: "2025-10-15T14:00:00Z"   │
│       ↓                                         │
│  3. Background worker checks every minute      │
│       ↓                                         │
│  4. At 2pm on Oct 15:                          │
│     • Worker finds scheduled post              │
│     • Calls publishing service                 │
│     • Posts to social platform                 │
│     • Updates status to "published"            │
│       ↓                                         │
│  5. Post appears on social media               │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 📁 FILE STRUCTURE

### Backend
```
backend/
├── app/
│   ├── services/
│   │   └── scheduler.py           ← NEW: Scheduling service
│   │
│   ├── api/
│   │   └── schedule.py            ← NEW: Scheduling endpoints
│   │
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── celery_app.py          ← NEW: Celery config
│   │   └── tasks.py               ← NEW: Celery tasks
│   │
│   └── utils/
│       └── timezone.py            ← NEW: Timezone helpers
```

### Frontend
```
frontend/
├── app/
│   ├── dashboard/
│   │   ├── schedule/
│   │   │   ├── page.tsx           ← NEW: Calendar view
│   │   │   └── components/
│   │   │       ├── Calendar.tsx   ← NEW: Calendar UI
│   │   │       └── ScheduleItem.tsx
│   │   │
│   │   └── content/
│   │       └── components/
│   │           └── ScheduleModal.tsx  ← NEW: Schedule picker
```

---

## 🔨 IMPLEMENTATION PHASES

### Phase 1: Background Worker Setup (60 mins)
- [ ] Install Celery + Redis (or APScheduler)
- [ ] Create Celery app configuration
- [ ] Create publish task
- [ ] Test task execution

### Phase 2: Scheduling Service (60 mins)
- [ ] Create scheduling service
- [ ] Add timezone conversion
- [ ] Create scheduled post
- [ ] Query due posts
- [ ] Update post status

### Phase 3: Calendar UI (90 mins)
- [ ] Create calendar component
- [ ] Show scheduled posts on calendar
- [ ] Drag-and-drop scheduling
- [ ] Edit scheduled posts
- [ ] Delete scheduled posts

### Phase 4: Bulk Scheduling (30 mins)
- [ ] Select multiple posts
- [ ] Schedule all at once
- [ ] Suggest optimal times (AI)
- [ ] Distribute across week

---

## 📊 API ENDPOINTS

**POST /api/v1/schedule/create**
- Schedule a post
- Body: `{ "content_id": 1, "scheduled_for": "2025-10-15T14:00:00Z" }`

**GET /api/v1/schedule/list**
- List scheduled posts
- Query: `business_id`, `from_date`, `to_date`

**PUT /api/v1/schedule/{id}**
- Update scheduled post
- Body: `{ "scheduled_for": "2025-10-15T15:00:00Z" }`

**DELETE /api/v1/schedule/{id}**
- Cancel scheduled post

**POST /api/v1/schedule/bulk**
- Schedule multiple posts
- Body: `{ "post_ids": [1,2,3], "schedule_pattern": "daily" }`

---

## 🧪 TESTING

- [ ] Schedule post for 1 minute future
- [ ] Verify auto-publish works
- [ ] View calendar with scheduled posts
- [ ] Edit scheduled post
- [ ] Cancel scheduled post
- [ ] Bulk schedule 10 posts
- [ ] Test timezone conversion

---

## 🎨 UI MOCKUP

### Calendar View
```
┌─────────────────────────────────────────────────┐
│  October 2025                          [Today]  │
├─────────────────────────────────────────────────┤
│  Mon   Tue   Wed   Thu   Fri   Sat   Sun       │
├─────────────────────────────────────────────────┤
│        1     2     3     4     5     6          │
│                         📱2pm                    │
│                                                 │
│  7     8     9     10    11    12    13         │
│        📱9am 📱3pm       📱11am                  │
│                                                 │
│  14    15    16    17    18    19    20         │
│        📱2pm                                     │
│        📷4pm                                     │
│                                                 │
│  21    22    23    24    25    26    27         │
│                                                 │
└─────────────────────────────────────────────────┘

📱 = Scheduled post
📷 = Instagram post
```

---

## 📚 RESOURCES

- **Celery**: https://docs.celeryq.dev/
- **APScheduler**: https://apscheduler.readthedocs.io/
- **React Calendar**: https://github.com/wojtekmaj/react-calendar
- **Timezone.js**: https://momentjs.com/timezone/

---

## ⚡ PERFORMANCE CONSIDERATIONS

**Worker Scaling**:
- Start with 1 worker (APScheduler)
- Scale to multiple workers (Celery)
- Use Redis for distributed locking

**Job Frequency**:
- Check every 1 minute (good enough)
- Or use exact scheduling (cron-like)

**Error Handling**:
- Retry failed posts (3 attempts)
- Notify user of failures
- Queue dead-letter for manual review

---

**Estimated Time**: 3-4 hours  
**Complexity**: Medium-High  
**Priority**: High (key feature for automation)
