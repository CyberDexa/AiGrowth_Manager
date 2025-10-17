# Session 13 Kickoff: Analytics & Insights 📊

## 🎯 Session Overview

**Goal**: Build comprehensive analytics system to track post performance, engagement metrics, and provide actionable insights for content strategy optimization.

**Status**: Ready to Start  
**Estimated Time**: 6-8 hours  
**Complexity**: High (Platform API integrations, data aggregation, chart components)

---

## 📋 What We're Building

### Core Features
1. **Post Performance Metrics** - Fetch likes, comments, shares, impressions from each platform
2. **Engagement Analytics** - Calculate engagement rates, growth trends, best performing content
3. **Platform Comparison** - Compare performance across LinkedIn, Twitter, Facebook, Instagram
4. **Time-Based Insights** - Best time to post, day-of-week analysis, posting frequency
5. **Content Analysis** - Top performing content types, hashtag analysis, content length correlation
6. **Analytics Dashboard** - Visual charts and graphs with interactive filters
7. **Export Reports** - Download analytics as CSV, PDF for client reporting

### User Stories
- As a user, I want to see how my posts are performing across all platforms
- As a user, I want to know the best time to post for maximum engagement
- As a user, I want to compare performance between different content types
- As a user, I want to export analytics reports for my clients
- As a user, I want to track engagement trends over time

---

## 🏗️ Architecture Design

### Database Schema

#### `post_analytics` Table (New)
```sql
CREATE TABLE post_analytics (
    id SERIAL PRIMARY KEY,
    published_post_id INTEGER NOT NULL REFERENCES published_posts(id) ON DELETE CASCADE,
    business_id INTEGER NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    platform VARCHAR(20) NOT NULL,
    
    -- Engagement Metrics
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    reactions_count INTEGER DEFAULT 0,  -- Facebook reactions
    retweets_count INTEGER DEFAULT 0,   -- Twitter specific
    quote_tweets_count INTEGER DEFAULT 0, -- Twitter specific
    
    -- Reach Metrics
    impressions INTEGER DEFAULT 0,
    reach INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    
    -- Video Metrics (optional)
    video_views INTEGER DEFAULT 0,
    video_watch_time INTEGER DEFAULT 0,  -- seconds
    
    -- Calculated Metrics
    engagement_rate DECIMAL(5,2) DEFAULT 0.0,  -- (likes+comments+shares)/impressions * 100
    click_through_rate DECIMAL(5,2) DEFAULT 0.0,  -- clicks/impressions * 100
    
    -- Metadata
    fetched_at TIMESTAMP NOT NULL,
    platform_post_id VARCHAR(255),  -- Platform's internal post ID
    platform_post_url TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_post_analytics_post_id ON post_analytics(published_post_id);
CREATE INDEX idx_post_analytics_business_id ON post_analytics(business_id);
CREATE INDEX idx_post_analytics_platform ON post_analytics(platform);
CREATE INDEX idx_post_analytics_fetched_at ON post_analytics(fetched_at);
```

#### `analytics_summaries` Table (New)
```sql
CREATE TABLE analytics_summaries (
    id SERIAL PRIMARY KEY,
    business_id INTEGER NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    platform VARCHAR(20) NOT NULL,
    
    -- Time Period
    period_type VARCHAR(20) NOT NULL,  -- daily, weekly, monthly
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Summary Metrics
    total_posts INTEGER DEFAULT 0,
    total_likes INTEGER DEFAULT 0,
    total_comments INTEGER DEFAULT 0,
    total_shares INTEGER DEFAULT 0,
    total_impressions INTEGER DEFAULT 0,
    total_reach INTEGER DEFAULT 0,
    total_clicks INTEGER DEFAULT 0,
    
    -- Calculated Metrics
    avg_engagement_rate DECIMAL(5,2) DEFAULT 0.0,
    avg_impressions INTEGER DEFAULT 0,
    follower_growth INTEGER DEFAULT 0,
    
    -- Best Performing
    best_post_id INTEGER REFERENCES published_posts(id),
    best_post_engagement_rate DECIMAL(5,2),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_analytics_summaries_business ON analytics_summaries(business_id);
CREATE INDEX idx_analytics_summaries_period ON analytics_summaries(period_start, period_end);
```

---

## 🔌 Platform API Integration

### LinkedIn Analytics API
**Endpoint**: `GET /rest/organizationPageStatistics`

**Metrics Available**:
- Impressions (organic, paid, total)
- Clicks
- Engagement (likes, comments, shares)
- Follower metrics

**Rate Limits**: 500 requests/day per token

**Sample Response**:
```json
{
  "impressionCount": 1234,
  "clickCount": 45,
  "likeCount": 78,
  "commentCount": 12,
  "shareCount": 5,
  "engagementRate": 7.7
}
```

### Twitter Analytics API
**Endpoint**: `GET /2/tweets/:id/metrics`

**Metrics Available**:
- Impressions
- Retweets
- Likes
- Replies
- Quote tweets
- URL clicks

**Rate Limits**: 300 requests/15 minutes

**Sample Response**:
```json
{
  "public_metrics": {
    "retweet_count": 12,
    "reply_count": 5,
    "like_count": 45,
    "quote_count": 2,
    "impression_count": 567
  }
}
```

### Facebook/Instagram Graph API
**Endpoint**: `GET /{post-id}/insights`

**Metrics Available**:
- Reach
- Impressions
- Engagement (reactions, comments, shares)
- Video views
- Post clicks

**Rate Limits**: 200 calls/hour per user

**Sample Response**:
```json
{
  "data": [
    {
      "name": "post_impressions",
      "values": [{"value": 1234}]
    },
    {
      "name": "post_engaged_users",
      "values": [{"value": 89}]
    }
  ]
}
```

---

## 🎨 Frontend Design

### Analytics Dashboard Layout
```
┌─────────────────────────────────────────────────────────────┐
│ Analytics Dashboard                                  [Export]│
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Filters: [All Platforms ▼] [Last 30 Days ▼] [Apply]        │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│ │ 1.2K    │ │ 345     │ │ 89      │ │ 5.8%    │           │
│ │ Posts   │ │ Likes   │ │ Comments│ │ Eng Rate│           │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Engagement Over Time                                        │
│ ┌───────────────────────────────────────────────────────┐  │
│ │     📈 Line Chart                                     │  │
│ │                                                       │  │
│ │  Eng │                                                │  │
│ │  Rate│      ╱╲        ╱╲                             │  │
│ │      │    ╱    ╲    ╱    ╲                           │  │
│ │      │  ╱        ╲╱        ╲                         │  │
│ │      └────────────────────────────────────────────   │  │
│ │       Jan   Feb   Mar   Apr   May   Jun              │  │
│ └───────────────────────────────────────────────────────┘  │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Platform Breakdown              Top Performing Posts        │
│ ┌─────────────────────┐        ┌──────────────────────┐   │
│ │  🔵 LinkedIn  45%   │        │ 1. "How to scale..." │   │
│ │  🔷 Twitter   30%   │        │    ❤️ 234  💬 45    │   │
│ │  🟦 Facebook  15%   │        │                      │   │
│ │  🟪 Instagram 10%   │        │ 2. "Top 5 tips..."   │   │
│ └─────────────────────┘        │    ❤️ 189  💬 32    │   │
│                                 └──────────────────────┘   │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Best Times to Post                                          │
│ ┌───────────────────────────────────────────────────────┐  │
│ │ Monday    ████████░░ 8.2% avg engagement              │  │
│ │ Tuesday   ██████████ 9.5% avg engagement  ⭐          │  │
│ │ Wednesday ████████░░ 8.0% avg engagement              │  │
│ │ Thursday  █████████░ 8.8% avg engagement              │  │
│ │ Friday    ███████░░░ 7.1% avg engagement              │  │
│ └───────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Chart Components Needed
1. **LineChart** - Engagement trends over time
2. **BarChart** - Platform comparison, best posting times
3. **PieChart** - Platform distribution
4. **MetricCard** - Summary statistics
5. **TopPostsTable** - Best performing content list

---

## 📂 File Structure

### Backend Files to Create
```
backend/
├── app/
│   ├── services/
│   │   ├── analytics_linkedin.py      # LinkedIn analytics fetcher
│   │   ├── analytics_twitter.py       # Twitter analytics fetcher
│   │   ├── analytics_meta.py          # Facebook/Instagram analytics fetcher
│   │   ├── analytics_aggregator.py    # Aggregates data from all platforms
│   │   └── analytics_calculator.py    # Calculates engagement rates, trends
│   ├── api/
│   │   └── analytics.py (UPDATE)      # Analytics endpoints
│   ├── models/
│   │   ├── post_analytics.py          # PostAnalytics model
│   │   └── analytics_summary.py       # AnalyticsSummary model
│   ├── schemas/
│   │   └── analytics.py (UPDATE)      # Analytics request/response schemas
│   └── tasks/
│       └── fetch_analytics.py         # Background task for periodic fetching
└── alembic/
    └── versions/
        └── {timestamp}_add_analytics_tables.py
```

### Frontend Files to Create
```
frontend/
├── app/
│   ├── dashboard/
│   │   └── analytics/
│   │       ├── page.tsx               # Analytics dashboard page
│   │       └── components/
│   │           ├── MetricCard.tsx     # Summary metric display
│   │           ├── LineChart.tsx      # Line chart component
│   │           ├── BarChart.tsx       # Bar chart component
│   │           ├── PieChart.tsx       # Pie chart component
│   │           ├── TopPostsTable.tsx  # Top posts list
│   │           ├── PlatformFilter.tsx # Filter by platform
│   │           ├── DateRangeFilter.tsx # Date range picker
│   │           └── ExportButton.tsx   # Export to CSV/PDF
│   └── components/
│       └── charts/
│           └── ChartWrapper.tsx       # Reusable chart container
└── lib/
    ├── analytics.ts                   # Analytics API client
    └── chartConfig.ts                 # Chart.js configuration
```

---

## 🛠️ Implementation Plan

### Phase 1: Database & Models (1.5 hours)
**Tasks**:
1. Create Alembic migration for `post_analytics` and `analytics_summaries` tables
2. Create SQLAlchemy models (`PostAnalytics`, `AnalyticsSummary`)
3. Create Pydantic schemas for analytics data
4. Add relationships to existing models (`PublishedPost`, `Business`)

**Deliverables**:
- Migration file with analytics tables
- 2 new model files
- Updated schemas with analytics types

### Phase 2: Platform Analytics Services (2 hours)
**Tasks**:
1. Create LinkedIn analytics fetcher service
2. Create Twitter analytics fetcher service
3. Create Meta (Facebook/Instagram) analytics fetcher service
4. Create analytics aggregator to combine platform data
5. Create calculator service for engagement rates, trends

**Key Methods**:
```python
# analytics_linkedin.py
async def fetch_post_analytics(post_id: str, access_token: str) -> Dict
async def fetch_page_insights(page_id: str, access_token: str) -> Dict

# analytics_twitter.py
async def fetch_tweet_metrics(tweet_id: str, access_token: str) -> Dict
async def fetch_account_analytics(user_id: str, access_token: str) -> Dict

# analytics_meta.py
async def fetch_post_insights(post_id: str, access_token: str) -> Dict
async def fetch_page_insights(page_id: str, access_token: str) -> Dict

# analytics_aggregator.py
async def aggregate_post_analytics(published_post_id: int) -> PostAnalytics
async def generate_summary(business_id: int, period: str) -> AnalyticsSummary

# analytics_calculator.py
def calculate_engagement_rate(likes, comments, shares, impressions) -> float
def calculate_growth_rate(current, previous) -> float
def find_best_posting_times(analytics_list: List) -> Dict
```

**Deliverables**:
- 5 service files with platform API integrations
- Error handling for API failures
- Rate limit management

### Phase 3: API Endpoints (1.5 hours)
**Tasks**:
1. Create endpoint to fetch analytics for single post
2. Create endpoint to fetch analytics for date range
3. Create endpoint for platform comparison
4. Create endpoint for best posting times
5. Create endpoint for top performing posts
6. Create endpoint to trigger analytics refresh
7. Create endpoint to export analytics (CSV)

**Endpoints**:
```python
GET  /api/v1/analytics/posts/{post_id}              # Single post analytics
GET  /api/v1/analytics/overview?business_id={id}    # Dashboard overview
GET  /api/v1/analytics/trends?business_id={id}      # Engagement trends
GET  /api/v1/analytics/platform-comparison          # Compare platforms
GET  /api/v1/analytics/best-times?platform={name}   # Best posting times
GET  /api/v1/analytics/top-posts?limit={n}          # Top performing posts
POST /api/v1/analytics/refresh?post_id={id}         # Refresh analytics
GET  /api/v1/analytics/export?format=csv            # Export to CSV/PDF
```

**Deliverables**:
- 8 new API endpoints
- Request validation with Pydantic
- Response formatting with proper schemas

### Phase 4: Frontend Dashboard (2.5 hours)
**Tasks**:
1. Install Chart.js or Recharts library
2. Create analytics dashboard page structure
3. Create MetricCard component for summary stats
4. Create LineChart component for trends
5. Create BarChart component for comparisons
6. Create PieChart component for distribution
7. Create TopPostsTable component
8. Create filter components (platform, date range)
9. Create export button with download functionality
10. Connect components to analytics API

**Components**:
```typescript
// MetricCard.tsx
interface MetricCardProps {
  title: string;
  value: number | string;
  change?: number;  // percentage change
  icon: React.ReactNode;
  color?: string;
}

// LineChart.tsx
interface LineChartProps {
  data: Array<{date: string; value: number}>;
  title: string;
  yAxisLabel: string;
}

// TopPostsTable.tsx
interface TopPostsTableProps {
  posts: Array<PostAnalytics>;
  onPostClick?: (postId: number) => void;
}
```

**Deliverables**:
- Analytics dashboard page
- 7 reusable chart/display components
- Filter and export functionality

### Phase 5: Background Tasks (Optional - 30 min)
**Tasks**:
1. Create Celery task for periodic analytics fetching
2. Schedule daily analytics refresh for all recent posts
3. Add task to update analytics summaries

**Deliverables**:
- Background task configuration
- Scheduled jobs for automation

### Phase 6: Testing & Documentation (30 min)
**Tasks**:
1. Test analytics fetching from each platform
2. Test dashboard with sample data
3. Test export functionality
4. Create comprehensive documentation
5. Update SESSION_13_COMPLETE.md

**Deliverables**:
- Testing guide
- API documentation
- Session completion summary

---

## 📊 Sample Data Structure

### Post Analytics Response
```json
{
  "post_id": 123,
  "platform": "linkedin",
  "content_text": "How to scale your business...",
  "published_at": "2025-01-15T10:00:00Z",
  "analytics": {
    "likes_count": 234,
    "comments_count": 45,
    "shares_count": 12,
    "impressions": 5678,
    "reach": 4521,
    "clicks": 89,
    "engagement_rate": 5.12,
    "click_through_rate": 1.57
  },
  "fetched_at": "2025-01-16T08:00:00Z"
}
```

### Overview Response
```json
{
  "period": {
    "start": "2025-01-01",
    "end": "2025-01-31"
  },
  "summary": {
    "total_posts": 45,
    "total_likes": 1234,
    "total_comments": 234,
    "total_shares": 89,
    "total_impressions": 45678,
    "avg_engagement_rate": 6.8
  },
  "by_platform": {
    "linkedin": {
      "posts": 20,
      "avg_engagement_rate": 7.2
    },
    "twitter": {
      "posts": 15,
      "avg_engagement_rate": 6.5
    },
    "facebook": {
      "posts": 7,
      "avg_engagement_rate": 5.9
    },
    "instagram": {
      "posts": 3,
      "avg_engagement_rate": 8.1
    }
  },
  "trends": [
    {"date": "2025-01-01", "engagement_rate": 5.2},
    {"date": "2025-01-02", "engagement_rate": 6.1},
    {"date": "2025-01-03", "engagement_rate": 7.8}
  ],
  "best_times": {
    "day_of_week": "Tuesday",
    "hour_of_day": 14
  },
  "top_posts": [
    {
      "id": 456,
      "content_preview": "How to scale...",
      "platform": "linkedin",
      "engagement_rate": 12.3,
      "likes": 234
    }
  ]
}
```

---

## 🎨 Chart Library Decision

### Option 1: Chart.js + react-chartjs-2
**Pros**:
- Lightweight (11KB gzipped)
- Simple API
- Good documentation
- Responsive by default

**Cons**:
- Less features than alternatives
- Manual responsive handling needed

### Option 2: Recharts ⭐ **RECOMMENDED**
**Pros**:
- Built for React (composable components)
- Excellent TypeScript support
- Responsive out of the box
- Beautiful default styling
- Easy to customize

**Cons**:
- Larger bundle size (95KB)
- Learning curve for complex charts

### Decision: **Recharts**
Better developer experience, React-first design, and excellent TypeScript support make it ideal for our use case.

**Installation**:
```bash
npm install recharts
npm install --save-dev @types/recharts
```

---

## 🔐 Security Considerations

### API Security
1. **Rate Limiting**: Implement rate limits on analytics endpoints to prevent abuse
2. **Data Privacy**: Only return analytics for posts owned by authenticated business
3. **Token Security**: Store platform access tokens encrypted in database
4. **API Key Rotation**: Handle expired tokens gracefully, prompt re-authentication

### Data Storage
1. **Retention Policy**: Keep detailed analytics for 90 days, summaries for 1 year
2. **Data Minimization**: Only fetch necessary metrics from platform APIs
3. **Anonymization**: Remove personal data from exported reports

---

## 💰 Cost Analysis

### Platform API Costs
- **LinkedIn**: Free (within rate limits: 500 req/day)
- **Twitter**: Free Basic tier (300 req/15min), $100/mo for v2 API access
- **Facebook/Instagram**: Free (within rate limits: 200 calls/hour)
- **Total**: $0-100/month depending on Twitter usage

### Storage Costs
- **Analytics Records**: ~500 bytes per record
- **Monthly Storage**: 10,000 posts × 500 bytes = 5MB
- **Annual Storage**: 60MB (negligible)

### Computation Costs
- **Background Tasks**: Minimal CPU usage for aggregation
- **Real-time Calculations**: Fast with proper indexing

**Estimated Monthly Cost**: $0-100 (only Twitter API if needed)

---

## 📈 Success Metrics

### Technical Metrics
- [ ] All 4 platform analytics APIs integrated
- [ ] Analytics dashboard loading time < 2 seconds
- [ ] Chart rendering smooth (60fps)
- [ ] Export generates reports in < 5 seconds
- [ ] Background tasks run without failures

### Business Metrics
- [ ] Users view analytics dashboard at least once per week
- [ ] Average session time on analytics page > 3 minutes
- [ ] 40%+ users export reports monthly
- [ ] Analytics insights lead to 20%+ engagement improvement

---

## 🚀 Getting Started

### Prerequisites
```bash
# Backend running on port 8003
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8003

# Frontend running on port 3000
cd frontend
npm run dev
```

### Environment Variables
```env
# Add to backend/.env (if needed)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here  # For v2 API
```

---

## 📚 Resources

### Platform API Documentation
- [LinkedIn Marketing API - Analytics](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/network-update-social-actions)
- [Twitter API v2 - Tweet Metrics](https://developer.twitter.com/en/docs/twitter-api/metrics)
- [Meta Graph API - Insights](https://developers.facebook.com/docs/graph-api/reference/insights)

### Chart Libraries
- [Recharts Documentation](https://recharts.org/en-US/)
- [Recharts Examples](https://recharts.org/en-US/examples)

### Background Tasks
- [Celery Documentation](https://docs.celeryproject.org/en/stable/)
- [APScheduler](https://apscheduler.readthedocs.io/) - Simpler alternative

---

## ✅ Session 13 Checklist

### Backend
- [ ] Create analytics tables migration
- [ ] Create PostAnalytics model
- [ ] Create AnalyticsSummary model
- [ ] Create analytics schemas
- [ ] Implement LinkedIn analytics fetcher
- [ ] Implement Twitter analytics fetcher
- [ ] Implement Meta analytics fetcher
- [ ] Create analytics aggregator service
- [ ] Create analytics calculator service
- [ ] Create 8 analytics API endpoints
- [ ] Add error handling and logging

### Frontend
- [ ] Install Recharts library
- [ ] Create analytics dashboard page
- [ ] Create MetricCard component
- [ ] Create LineChart component
- [ ] Create BarChart component
- [ ] Create PieChart component
- [ ] Create TopPostsTable component
- [ ] Create PlatformFilter component
- [ ] Create DateRangeFilter component
- [ ] Create ExportButton component
- [ ] Connect to analytics API
- [ ] Add loading states
- [ ] Add error handling

### Testing
- [ ] Test analytics fetch from LinkedIn
- [ ] Test analytics fetch from Twitter
- [ ] Test analytics fetch from Meta
- [ ] Test dashboard with sample data
- [ ] Test all chart components
- [ ] Test filters functionality
- [ ] Test export to CSV
- [ ] Test mobile responsiveness

### Documentation
- [ ] Create API endpoint documentation
- [ ] Create testing guide
- [ ] Create SESSION_13_COMPLETE.md
- [ ] Create SESSION_13_SUMMARY.md
- [ ] Update main README

---

## 🎯 Expected Outcomes

After Session 13, users will be able to:
1. ✅ View comprehensive analytics for all published posts
2. ✅ See engagement trends over time with interactive charts
3. ✅ Compare performance across different platforms
4. ✅ Identify best times and days to post
5. ✅ Export analytics reports for clients
6. ✅ Make data-driven decisions about content strategy

---

## 🔄 Next Steps After Session 13

**Session 14: Advanced Features**
- Content calendar view
- Bulk content upload
- Team collaboration
- White-label branding
- Custom webhooks

---

## 📝 Notes

- Focus on core analytics first, advanced features can be added later
- Use mock data for initial frontend development
- Consider caching analytics data to reduce API calls
- Platform APIs have different update frequencies (LinkedIn: 24hrs, Twitter: real-time)
- Some metrics may not be available without business/professional accounts

---

**Ready to start Session 13!** 🚀

Let's build an analytics dashboard that provides real insights and helps users optimize their social media strategy!
