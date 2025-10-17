# Week 3 Day 1: Quick Start Checklist

## Twitter Developer Account Setup - Action Items

### 📋 Before You Start
- [ ] Have your Twitter/X account ready
- [ ] Email address accessible for verification
- [ ] 30-40 minutes of focused time
- [ ] Backend and frontend running locally

---

## ⚡ Quick Steps

### Step 1: Create Developer Account (5-10 min)
- [ ] Go to https://developer.twitter.com
- [ ] Sign up with your Twitter account
- [ ] Complete basic information form
- [ ] Verify your email

### Step 2: Apply for Elevated Access (10-15 min)
- [ ] Navigate to Products → Twitter API v2
- [ ] Click "Apply for Elevated Access"
- [ ] Fill out detailed application (use sample answers from guide)
- [ ] Submit application
- [ ] ⏰ Wait 1-2 days for approval (check email)

### Step 3: Create App (After Approval - 5 min)
- [ ] Log into Developer Portal
- [ ] Create new app: "AI Growth Manager"
- [ ] Select Production environment
- [ ] Configure permissions: Read + Write

### Step 4: Configure OAuth 2.0 (5 min)
- [ ] Enable OAuth 2.0 in app settings
- [ ] Add callback URLs:
  - `http://localhost:8003/api/oauth/twitter/callback`
  - `http://localhost:3000/dashboard/social-accounts`
- [ ] Set website URL: `http://localhost:3000`

### Step 5: Get Credentials (2 min)
- [ ] Generate OAuth 2.0 Client ID and Secret
- [ ] **SAVE IMMEDIATELY** - you won't see the secret again!
- [ ] Store in password manager or secure location

### Step 6: Update Backend (2 min)
- [ ] Open `backend/.env`
- [ ] Add:
  ```bash
  TWITTER_CLIENT_ID=your_client_id_here
  TWITTER_CLIENT_SECRET=your_client_secret_here
  ```
- [ ] Save file
- [ ] Restart backend server

### Step 7: Test Integration (5 min)
- [ ] Open http://localhost:3000
- [ ] Go to Dashboard → Social Accounts
- [ ] Click "Connect Twitter Account"
- [ ] Authorize the app
- [ ] Verify account shows as connected
- [ ] Try publishing a test tweet

---

## 🎯 Success Criteria

You're done when:
- ✅ Twitter Developer Account created and approved for Elevated Access
- ✅ App created with OAuth 2.0 configured
- ✅ Client ID and Secret added to backend .env
- ✅ Can connect Twitter account through frontend
- ✅ Can publish test tweet successfully

---

## ⚠️ Common Issues

**"Callback URL mismatch"**
→ Add exact URL with correct port: `http://localhost:8003/api/oauth/twitter/callback`

**"Invalid client credentials"**
→ Check for typos in .env file, ensure no extra spaces, restart backend

**"403 Forbidden when posting"**
→ Ensure app has "Read and Write" permissions, try reconnecting account

**"Waiting for Elevated Access approval"**
→ Normal! Takes 1-2 business days. Use this time to prepare other integrations.

---

## 📚 Full Documentation

See `WEEK3_DAY1_TWITTER_SETUP.md` for:
- Detailed step-by-step instructions
- Sample application answers
- Security best practices
- API rate limits
- Troubleshooting guide

---

## 🚀 Next Steps After Completion

1. **Test thoroughly** - Post several tweets, verify analytics
2. **Document your credentials** - Store securely for production
3. **Week 3 Day 2** - LinkedIn API Setup
4. **Week 3 Day 3** - Meta (Facebook/Instagram) Setup

---

**Estimated Active Time**: 30-40 minutes
**Waiting Time**: 1-2 days for Elevated Access approval

**Current Status**: Ready to start!

Go to https://developer.twitter.com to begin! 🚀
