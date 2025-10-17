# 🎯 Week 3 Day 3: Meta OAuth Setup - Quick Start

**Date**: October 17, 2025  
**Goal**: Complete Meta (Facebook/Instagram) OAuth configuration  
**Time**: 20-30 minutes  
**Status**: Ready to begin

---

## ✅ What You Already Have

1. **Meta App Created** ✅ (Oct 17 - Recreated)
   - App Name: "AI Growth Manager"
   - App ID: `4284592478453354`
   - App Secret: `4d236810aab33cf822fa89e9490f1303`
   - Credentials in `backend/.env` ✅

2. **Previous OAuth Setups** ✅
   - Twitter OAuth complete (Day 1)
   - LinkedIn OAuth complete (Day 2, pending approval)

---

## 🚀 Today's Checklist

### Step 1: Add Facebook Login Product (5 min)
- [ ] Go to [Meta Developers](https://developers.facebook.com/apps/4284592478453354)
- [ ] Click **"Add Products"** → **"Facebook Login"** → **"Set Up"**
- [ ] Go to **"Facebook Login"** → **"Settings"**
- [ ] Add OAuth Redirect URI: `https://aigrowth.loca.lt/api/oauth/meta/callback`
- [ ] Enable **Client OAuth Login** and **Web OAuth Login**
- [ ] Click **"Save Changes"**

### Step 2: Add Instagram Graph API (5 min)
- [ ] Click **"Add Products"** → **"Instagram Graph API"** → **"Set Up"**
- [ ] Connect your Instagram Business account
- [ ] If needed, convert personal Instagram to Business account

### Step 3: Configure App Settings (5 min)
- [ ] Go to **"Settings"** → **"Basic"**
- [ ] Add **App Domain**: `aigrowth.loca.lt` and `localhost`
- [ ] Add **Platform**: Website → `https://aigrowth.loca.lt`
- [ ] Add **Privacy Policy URL**: `https://aigrowth.loca.lt/privacy`
- [ ] Click **"Save Changes"**

### Step 4: Request Permissions (Optional - Can do later)
- [ ] Go to **"App Review"** → **"Permissions and Features"**
- [ ] Request: `pages_manage_posts`, `pages_read_engagement`, `instagram_content_publish`
- [ ] Use the use case description from the guide
- [ ] **Note**: Can test in Development Mode without approval!

### Step 5: Start Servers & Test (15 min)
- [ ] Start localtunnel: `lt --port 8003 --subdomain aigrowth`
- [ ] Start backend: `cd backend && ./venv/bin/python -m uvicorn app.main:app --reload --port 8003`
- [ ] Start frontend: `cd frontend && npm run dev`
- [ ] Test Facebook OAuth flow
- [ ] Test Instagram OAuth flow
- [ ] Publish test post to Facebook
- [ ] Publish test post to Instagram

---

## 📖 Full Documentation

For detailed instructions, see:
**`docs/WEEK3_DAY3_META_SETUP.md`**

---

## 🎯 Success Criteria

By end of today, you should have:
- ✅ Facebook Login product added
- ✅ Instagram Graph API product added
- ✅ OAuth redirect URI configured
- ✅ Successfully connected Facebook account
- ✅ Successfully connected Instagram account
- ✅ Published test post to Facebook
- ✅ Published test post to Instagram

---

## 💡 Quick Tips

1. **Development Mode**: No permission approval needed for testing with your own accounts!
2. **Instagram**: Must use Business or Creator account (not personal)
3. **Test Users**: You can add friends as testers in **"Roles"** → **"Roles"**
4. **Rate Limits**: 200 API calls/hour (generous for testing)

---

## 🚦 Current Status

```
✅ Week 3 Day 1 - Twitter OAuth: COMPLETE
✅ Week 3 Day 2 - LinkedIn OAuth: COMPLETE (pending approval)
🔄 Week 3 Day 3 - Meta OAuth: IN PROGRESS
⏳ Week 3 Day 4 - Test All Platforms: PENDING
⏳ Week 3 Day 5 - Multi-Platform Features: PENDING
```

**Progress**: 40% complete → Goal: 60% by end of today!

---

## ⚡ Next Steps After Meta

1. Wait for LinkedIn approval (24-72 hours)
2. Test all three OAuth flows end-to-end
3. Implement multi-platform content scheduling
4. Build analytics dashboard

---

## 🆘 Need Help?

- **Full Guide**: `docs/WEEK3_DAY3_META_SETUP.md`
- **Troubleshooting**: See guide's troubleshooting section
- **Meta Docs**: [developers.facebook.com](https://developers.facebook.com)

---

**Let's get started!** 🚀

**Open this URL now:**
```
https://developers.facebook.com/apps/4284592478453354
```
