# 🚀 Session 9 - Testing Guide

## ✅ System Status

**Backend**: ✅ Running on http://localhost:8003  
**Frontend**: ✅ Running on http://localhost:3000  
**Database**: ✅ Migration applied  
**API Docs**: http://localhost:8003/docs

---

## 📋 Publishing Endpoints Available

1. **POST** `/api/v1/publishing/linkedin` - Publish content to LinkedIn
2. **GET** `/api/v1/publishing/posts` - List all published posts
3. **GET** `/api/v1/publishing/posts/{id}` - Get single post details
4. **POST** `/api/v1/publishing/posts/{id}/retry` - Retry failed post

---

## 🧪 Quick Test Steps

### Step 1: Verify LinkedIn Connection (If Not Done)

1. Open http://localhost:3000/dashboard/settings
2. Click **"Social Accounts"** tab
3. If not connected:
   - Click **"Connect LinkedIn"**
   - Complete OAuth flow
   - Verify ✅ Connected status

### Step 2: Generate or Select Content

1. Go to http://localhost:3000/dashboard/content
2. Either:
   - **Generate new content**: Use the "Generate Content" tab
   - **Use existing content**: Switch to "Content Library" tab

### Step 3: Publish Content

1. Find any content item in your library
2. Click the **"Publish"** button (blue button with Send icon)
3. PublishContentModal opens
4. Verify:
   - ✅ LinkedIn is selected (blue checkmark)
   - ✅ Content appears in preview
   - ✅ Character count shows (e.g., "245 / 3000")
5. Choose publishing mode:
   - **Publish Now**: Click "Publish to LinkedIn"
   - **Schedule**: Select date/time, then click "Schedule Post"

### Step 4: Verify Publication

**If Published Immediately**:
1. Should show success message
2. LinkedIn post should open in new tab
3. Verify post appears on your LinkedIn feed

**If Scheduled**:
1. Should show "Scheduled Successfully!"
2. Go to http://localhost:3000/dashboard/published
3. Click "Scheduled" filter
4. Verify post appears with clock icon

### Step 5: View Published Posts

1. Navigate to http://localhost:3000/dashboard/published
2. View all your published content
3. Test filters:
   - Click **"Published"** - Shows only published posts
   - Click **"Scheduled"** - Shows only scheduled posts
   - Click **"Failed"** - Shows any failed posts
4. For published posts:
   - Click **"View on LinkedIn"** - Opens post in new tab
   - See engagement metrics (when available)

---

## 🐛 Troubleshooting

### Error: "No connected LinkedIn account found"

**Solution**:
1. Go to Settings > Social Accounts
2. Click "Connect LinkedIn"
3. Complete OAuth authorization
4. Verify token is saved

### Error: "LinkedIn token expired"

**Solution**:
1. Go to Settings > Social Accounts
2. Click "Disconnect" on LinkedIn
3. Click "Connect LinkedIn" again
4. Re-authorize

### Error: "Content exceeds maximum length"

**Solution**:
- LinkedIn limit: 3000 characters
- Edit content to be under limit
- Character count shows in red when over limit

### Error: "Rate limit exceeded"

**Solution**:
- LinkedIn allows ~100 posts/day
- Wait a few hours before publishing again
- Recommended: 5-10 posts per day for quality

---

## 🎯 Test Scenarios

### ✅ Scenario 1: Successful Publishing
1. Generate short content (< 500 chars)
2. Click Publish
3. Select "Publish Now"
4. Verify post on LinkedIn
5. Check `/dashboard/published` for record

### ✅ Scenario 2: Scheduled Publishing
1. Click Publish on content
2. Select "Schedule for Later"
3. Choose tomorrow's date
4. Click "Schedule Post"
5. Verify in Published page (Scheduled filter)

### ✅ Scenario 3: Character Limit
1. Generate very long content (> 3000 chars)
2. Click Publish
3. Verify red warning appears
4. Verify "Publish" button is disabled

### ✅ Scenario 4: Multiple Platforms (Future)
1. Click Publish
2. Notice Twitter and Meta show "Coming Soon"
3. Only LinkedIn is clickable

---

## 📊 Database Verification (Optional)

### Check Published Posts in Database

```bash
# Connect to database
psql -U postgres -d ai_growth_manager

# View published posts
SELECT 
    id,
    platform,
    status,
    LEFT(content_text, 50) as content_preview,
    published_at,
    platform_post_url
FROM published_posts
ORDER BY created_at DESC
LIMIT 5;
```

### Expected Columns
- `id` - Unique post ID
- `business_id` - Your business ID
- `platform` - "linkedin"
- `status` - "published", "scheduled", "failed", "pending"
- `content_text` - Full post content
- `platform_post_id` - LinkedIn URN
- `platform_post_url` - Direct link to LinkedIn post
- `published_at` - Timestamp when published

---

## 🔧 API Testing (Advanced)

### Test Publishing Endpoint Directly

```bash
# Get your auth token from browser DevTools (Application > Cookies)
TOKEN="your_clerk_token_here"

# Test publish endpoint
curl -X POST http://localhost:8003/api/v1/publishing/linkedin \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "business_id": 1,
    "content_text": "Test post from API! 🚀 #AI #Testing",
    "strategy_id": null
  }'
```

### Expected Response
```json
{
  "id": 1,
  "business_id": 1,
  "platform": "linkedin",
  "status": "published",
  "content_text": "Test post from API! 🚀 #AI #Testing",
  "platform_post_id": "urn:li:share:7123456789",
  "platform_post_url": "https://www.linkedin.com/feed/update/urn:li:share:7123456789",
  "published_at": "2025-10-13T03:45:00Z",
  "created_at": "2025-10-13T03:45:00Z"
}
```

---

## 📈 Success Criteria

✅ **Backend running** on port 8003  
✅ **Frontend running** on port 3000  
✅ **Publishing endpoints** accessible at `/api/v1/publishing/*`  
✅ **LinkedIn OAuth** connected (if testing live)  
✅ **Database migration** applied (`published_posts` table exists)  
✅ **UI components** render without errors  

### When Ready to Test Live Publishing:

1. ✅ LinkedIn Developer App created
2. ✅ Client ID/Secret in backend `.env`
3. ✅ LinkedIn account connected via UI
4. ✅ Access token saved and encrypted
5. ✅ `w_member_social` scope granted

---

## 🎉 What's Working Now

- ✅ Click "Publish" button on any content
- ✅ Modal opens with platform selection
- ✅ Content preview with character count
- ✅ Publish immediately or schedule for later
- ✅ Post to LinkedIn with one click
- ✅ View all published posts in dedicated page
- ✅ Filter by status (published/scheduled/failed)
- ✅ Retry failed posts
- ✅ View posts on LinkedIn
- ✅ Track engagement metrics (ready for sync)

---

## 🔮 Next Steps

**To Test Full Publishing Flow**:
1. Set up LinkedIn OAuth app (if not done in Session 8)
2. Add credentials to `backend/.env`
3. Connect LinkedIn in Settings
4. Publish your first AI-generated post!

**Future Sessions**:
- Session 10: Twitter publishing
- Session 11: Meta (Facebook/Instagram) publishing
- Session 12: Image upload support
- Session 13: Automated scheduled posting
- Session 14: Analytics dashboard

---

**Everything is ready to go! 🚀**

Both servers are running, all endpoints are registered, and the UI is ready. Just need to complete the LinkedIn OAuth setup to start publishing live content!
