# Using Render Backend - Quick Reference

## ✅ Current Configuration

**Frontend:** `http://localhost:3000`
**Backend:** `https://ai-growth-manager.onrender.com` (Render - Production)

Your `.env.local` is correctly configured to use Render.

---

## 🎯 What to Expect with Render Free Tier

### Cold Start Behavior

**First Request After Inactivity:**
- ⏱️ Takes **30-50 seconds** to respond
- 🌙 Backend "sleeps" after **15 minutes** of no activity
- 🔄 Every first request wakes it up (slow)
- ⚡ Subsequent requests are fast (~200-500ms)

### Visual Indicators

**When backend is waking up:**
- 🔴 Toast notification: "Unable to connect to backend"
- 🔴 Toast notification: "Backend is starting up. Please wait 30 seconds and refresh"
- ⏳ Loading spinners stay active
- 📄 Empty content lists

**When backend is awake:**
- ✅ Data loads normally
- ✅ Fast response times
- ✅ All features work

---

## 🚀 Backend Status Check

### Quick Status Check (in terminal):
```bash
curl https://ai-growth-manager.onrender.com/
```

**Expected response:**
```json
{"message":"AI Growth Manager API","version":"0.1.0","status":"operational"}
```

### If you get no response:
- Wait 30 seconds (cold start)
- Try again
- Check Render dashboard: https://dashboard.render.com/

---

## 🔧 How to Use Each Feature

### 1. **AI Strategy Generator** (NEW!)

**Steps:**
1. Go to **Dashboard → Strategies**
2. First time: Wait 30-60 seconds for backend to wake up
3. Click **"Generate Custom Strategy with AI"**
4. Fill in optional context
5. Click **"Generate Strategy"**
6. Wait 10-30 seconds for AI to generate
7. Strategy appears with executive summary, objectives, and content pillars

**Note:** AI generation uses OpenRouter API on backend - you don't need any API keys on frontend!

### 2. **Content Creation**

**Steps:**
1. Go to **Dashboard → Content**
2. Wait for backend to load (cold start if first request)
3. Create content normally

**If you see "Failed to load content":**
- Wait 30 seconds
- Refresh page
- Content will load once backend is awake

### 3. **Publishing & OAuth**

**Steps:**
1. Connect social accounts (Settings → Social Connections)
2. OAuth redirects to Render backend
3. Redirects back to your app

**Note:** OAuth redirect URLs in Render are already configured

---

## ⚡ Pro Tips for Render Backend

### 1. **Keep Backend Warm**
If you're actively developing, make a request every 10 minutes to keep it awake:

```bash
# Run this in a terminal:
while true; do curl -s https://ai-growth-manager.onrender.com/ > /dev/null; echo "Backend pinged at $(date)"; sleep 600; done
```

### 2. **Wake Up Before Testing**
Before testing a feature:
```bash
# Ping backend first
curl https://ai-growth-manager.onrender.com/
# Wait 5 seconds
# Then use the app
```

### 3. **Check Render Logs**
If something fails:
1. Go to https://dashboard.render.com/
2. Click your service
3. View logs to see errors

### 4. **Upgrade to Paid Plan** (Optional)
- $7/month removes cold starts
- Instant responses
- 24/7 availability

---

## 🐛 Common Issues & Solutions

### Issue 1: "Failed to fetch"
**Cause:** Cold start
**Solution:** Wait 30 seconds, refresh page

### Issue 2: "Backend is starting up"
**Cause:** First request after sleep
**Solution:** Wait and try again in 30 seconds

### Issue 3: Empty content lists
**Cause:** Backend hasn't responded yet
**Solution:** Refresh after cold start completes

### Issue 4: AI Strategy not generating
**Cause:** Backend might be asleep or OpenRouter API issue
**Solution:** 
1. Check Render logs
2. Verify OpenRouter API key is set on Render
3. Wait for cold start

### Issue 5: OAuth redirects fail
**Cause:** Redirect URLs not matching
**Solution:** Verify OAuth redirect URLs in LinkedIn/Twitter/Facebook developer consoles match:
```
https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback
https://ai-growth-manager.onrender.com/api/v1/oauth/twitter/callback
https://ai-growth-manager.onrender.com/api/v1/oauth/facebook/callback
```

---

## 📊 Backend Endpoints Available

All endpoints are at: `https://ai-growth-manager.onrender.com/api/v1/`

**Key endpoints:**
- `GET /` - Health check
- `POST /strategies/generate` - Generate AI strategy ⭐ NEW
- `GET /strategies/` - List strategies
- `GET /businesses/` - List businesses
- `POST /content/generate` - Generate content
- `GET /content/` - List content
- `POST /publishing/publish` - Publish to social
- `GET /analytics/summary` - Get analytics
- `POST /oauth/{platform}/authorize` - OAuth flow

---

## 🎯 Current Status

**✅ Backend is OPERATIONAL**

Last checked: Just now
Response time: Fast (backend is awake)
API Version: 0.1.0

**You're all set to use the app!** Just be patient with the first request after inactivity.

---

## 🔄 When to Switch to Local

Consider local backend if:
- ❌ Cold starts are too frustrating
- ❌ Need faster iteration
- ❌ Making backend code changes
- ❌ Want to see backend logs in real-time

For now, **Render is perfect** for frontend development and testing!

---

## 📝 Quick Commands

**Check if backend is awake:**
```bash
curl https://ai-growth-manager.onrender.com/
```

**Wake up backend:**
```bash
curl https://ai-growth-manager.onrender.com/ && echo "Backend pinged!"
```

**Test AI Strategy endpoint:**
```bash
# (Requires auth token - use the app instead)
```

---

**Last Updated:** October 20, 2025
**Backend Status:** ✅ Operational
**Configuration:** Render Production Backend
