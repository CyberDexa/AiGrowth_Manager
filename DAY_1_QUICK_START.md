# Day 1 Quick Start Guide 🚀

**Date**: October 14, 2025  
**Goal**: Get all API credentials for social media platforms

---

## 🎯 What You're Doing Today

Setting up developer accounts on 3 platforms:
1. **Meta** (Facebook + Instagram)
2. **Twitter** (X)
3. **LinkedIn**

**Total Time**: ~3-4 hours  
**Outcome**: All API credentials saved in `backend/.env`

---

## 📋 Quick Checklist

```
Morning (2 hours):
[ ] Meta Developer Account    → Get App ID + App Secret
[ ] Twitter Developer Account → Get 5 credentials + Request Elevated Access

Afternoon (2 hours):
[ ] LinkedIn Developer Account → Get Client ID + Client Secret
[ ] Update backend/.env        → Add all credentials
[ ] Restart backend server     → Test configuration
```

---

## 🚀 Step-by-Step Process

### Step 1: Meta Developer Account (45-60 min)

**Go to**: https://developers.facebook.com

**What to do**:
1. Log in with your Facebook account
2. Click "Create App"
3. Choose "Business" type
4. App name: **AI Growth Manager**
5. Add your email
6. Click "Create App"

**Add Products**:
- Click "+ Add Product"
- Add "Facebook Login" → Set Up
- Add "Instagram Graph API" → Set Up

**Get Credentials**:
- Go to Settings → Basic
- Copy **App ID**: `_______________`
- Click "Show" and copy **App Secret**: `_______________`

**Configure OAuth**:
- Go to Facebook Login → Settings
- Add Valid OAuth Redirect URI:
  ```
  http://localhost:8000/api/oauth/meta/callback
  ```
- Save Changes

**Create Test Users** (for development):
- Go to Roles → Test Users
- Click "Add" → Create 2-3 test users
- Save their credentials

✅ **Done!** Save credentials temporarily in a text file.

---

### Step 2: Twitter Developer Account (45-60 min)

**Go to**: https://developer.twitter.com

**Apply for Account**:
1. Click "Sign up" or "Apply"
2. Choose account type (Individual/Hobbyist)
3. Answer questions:
   - Use case: Social media management tool
   - Will you make content available to government? **No**
4. Accept terms and submit

**⚠️ CRITICAL: Request Elevated Access**
- Go to Developer Portal
- Click "Elevated" under your access level
- Fill out application:
  - Describe use case: "OAuth authentication for social media scheduling"
  - Estimated API calls: 100-500/day
- Submit request
- **Note**: This can take 1-2 weeks! Apply today.

**Create Project + App**:
1. Go to Projects & Apps
2. Click "Create Project"
   - Name: **AI Growth Manager**
   - Use case: Making a bot
   - Description: Social media scheduling platform
3. Create App in project
   - App name: **AI Growth Manager App**

**Set Up Authentication**:
1. Go to your app → Settings
2. Click "Set up" under User authentication settings
3. Enable **OAuth 1.0a** ✓
4. App permissions: **Read and Write**
5. Callback URL:
   ```
   http://localhost:8000/api/oauth/twitter/callback
   ```
6. Website URL: `http://localhost:8000`

**Get Credentials** (Keys and tokens tab):
- **API Key**: `_______________`
- **API Secret**: `_______________`
- **Bearer Token**: `_______________`
- **Access Token**: `_______________`
- **Access Token Secret**: `_______________`

✅ **Done!** Save all 5 credentials.

---

### Step 3: LinkedIn Developer Account (60-90 min)

**First: Create Company Page** (if you don't have one)
1. Go to: https://linkedin.com/company/setup/new
2. Company name: **AI Growth Manager**
3. Website: `http://localhost:8000` (temporary)
4. Industry: Software Development
5. Company size: 1-10 employees
6. Company type: Privately Held
7. Add logo (optional but recommended)
8. Click "Create page"

**Create Developer App**:
1. Go to: https://developer.linkedin.com
2. Click "Create app"
3. Fill in details:
   - App name: **AI Growth Manager**
   - LinkedIn Page: Select your company page
   - App logo: Upload logo
   - Legal agreement: Accept
4. Click "Create app"

**Request Marketing Developer Platform Access**:
1. In your app dashboard, go to "Products" tab
2. Find "Marketing Developer Platform"
3. Click "Request access"
4. Fill out form:
   - Use case: Social media scheduling and publishing
   - Expected monthly API calls: 1,000-5,000
5. Submit request
   - **Note**: May take a few days for approval

**Get Credentials**:
1. Go to "Auth" tab
2. Copy **Client ID**: `_______________`
3. Copy **Client Secret**: `_______________`

**Configure OAuth 2.0**:
1. Still in "Auth" tab
2. Add Redirect URL:
   ```
   http://localhost:8000/api/oauth/linkedin/callback
   ```
3. Save changes

✅ **Done!** Save Client ID and Secret.

---

### Step 4: Update Environment Variables (15-30 min)

**Open backend/.env file** and add:

```bash
# =============================================================================
# SOCIAL MEDIA API CREDENTIALS (Added Week 3 Day 1)
# =============================================================================

# Meta (Facebook/Instagram)
META_APP_ID=your_app_id_here
META_APP_SECRET=your_app_secret_here
META_REDIRECT_URI=http://localhost:8000/api/oauth/meta/callback

# Twitter (X)
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
TWITTER_REDIRECT_URI=http://localhost:8000/api/oauth/twitter/callback

# LinkedIn
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
LINKEDIN_REDIRECT_URI=http://localhost:8000/api/oauth/linkedin/callback
```

**Replace the placeholders** with your actual credentials.

**Restart Backend Server**:
```bash
# Stop the current server (Ctrl+C in the terminal)
# Then restart:
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
```

**Verify**:
```bash
# In another terminal, test the health endpoint:
curl http://localhost:8003/health

# Should return: {"status":"healthy"}
```

✅ **Done!** Backend configured with all credentials.

---

## 📝 Track Your Progress

Update `WEEK_3_PROGRESS.md` as you complete each task:

```markdown
## Day 1 Progress

### ✅ Completed Tasks
- [x] Meta Developer Account → App ID: abc123...
- [x] Twitter Developer Account → 5 credentials obtained
- [x] LinkedIn Developer Account → Client ID: xyz789...
- [x] Updated backend/.env
- [x] Restarted backend server

### ⏰ Time Spent
- Meta: 1 hour
- Twitter: 1 hour
- LinkedIn: 1.5 hours
- Setup: 30 minutes
**Total**: 4 hours

### 📚 Key Learnings
- Twitter Elevated Access takes 1-2 weeks
- LinkedIn requires company page first
- Meta has separate IDs for Facebook vs Instagram
```

---

## ⚠️ Important Reminders

### Twitter Elevated Access
- **Apply TODAY** - can take 1-2 weeks
- You can still create the app without it
- But OAuth won't work until approved
- Check status daily at: https://developer.twitter.com

### Test Accounts
- **Meta**: Use test users for development (not your personal account)
- **Twitter**: Use test account if available
- **LinkedIn**: May need to use personal profile initially

### Security
- **Never commit .env file** to git (already in .gitignore)
- Keep credentials secure
- Don't share API secrets publicly
- Consider using a password manager to store credentials

### Backup Your Credentials
Save all credentials in a secure location (password manager, encrypted file):
```
META_APP_ID=...
META_APP_SECRET=...
TWITTER_API_KEY=...
... (all credentials)
```

---

## 🎯 Success Criteria for Today

By end of day, you should have:
- [ ] 3 developer accounts created
- [ ] 8 credentials obtained (2 Meta + 5 Twitter + 2 LinkedIn + 1 LinkedIn company page)
- [ ] All credentials in backend/.env
- [ ] Backend server running with new config
- [ ] Twitter Elevated Access requested
- [ ] Progress tracked in WEEK_3_PROGRESS.md

---

## 🚨 Troubleshooting

### Meta Issues
**Problem**: Can't find "Create App" button  
**Solution**: Make sure you're logged into a Facebook account, then go to developers.facebook.com/apps

**Problem**: Instagram Graph API not available  
**Solution**: Add Facebook Login first, then Instagram Graph API will appear

### Twitter Issues
**Problem**: Can't request Elevated Access  
**Solution**: Complete your developer profile first (answer all questions)

**Problem**: OAuth 1.0a not working  
**Solution**: Elevated Access is REQUIRED for OAuth 1.0a - must wait for approval

### LinkedIn Issues
**Problem**: No company page to select  
**Solution**: Create a company page first at linkedin.com/company/setup/new

**Problem**: Marketing Developer Platform not available  
**Solution**: Request access first - may take a few days for approval

### General Issues
**Problem**: Backend won't start after adding credentials  
**Solution**: Check for typos in .env file, ensure no extra spaces or quotes

---

## 📞 Resources

### Documentation Links
- **Meta**: https://developers.facebook.com/docs
- **Twitter**: https://developer.twitter.com/en/docs
- **LinkedIn**: https://learn.microsoft.com/en-us/linkedin/

### Your Project Docs
- Full plan: `WEEK_3_PLANNING.md`
- Detailed log: `WEEK_3_DAY_1_LOG.md`
- Progress tracker: `WEEK_3_PROGRESS.md`
- Setup guide: `docs/developer_accounts_setup.md`

---

## 🎉 What's Next?

**Tomorrow (Day 2)**: OAuth Implementation
- Implement LinkedIn OAuth 2.0 flow
- Implement Twitter OAuth 1.0a flow
- Implement Meta OAuth 2.0 flow
- Test all authentication flows

**But first**: Complete today's tasks! 💪

---

## ⏰ Suggested Timeline

**9:00 AM - 10:00 AM**: Meta Developer Account  
**10:00 AM - 11:00 AM**: Twitter Developer Account  
*Break*  
**11:15 AM - 12:30 PM**: LinkedIn Developer Account  
*Lunch*  
**1:30 PM - 2:00 PM**: Update .env and restart backend  
**2:00 PM - 2:30 PM**: Update progress docs and celebrate! 🎉

---

**Remember**: This is foundational work. Taking time to do it right now will save hours of debugging later!

Let's build something amazing! 🚀
