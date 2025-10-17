# 🧪 Week 3 Day 4: OAuth Testing Guide

**Date**: October 17, 2025  
**Goal**: Test all OAuth integrations end-to-end  
**Time**: 2-3 hours  
**Status**: READY TO TEST! 🚀

---

## ✅ Pre-Test Checklist - ALL RUNNING!

- ✅ **Backend**: Running on `http://localhost:8003`
- ✅ **Frontend**: Running on `http://localhost:3000`
- ✅ **Localtunnel**: Active at `https://aigrowth.loca.lt`
- ✅ **All credentials**: Loaded in backend

---

## 🎯 Testing Plan

### Test 1: Twitter OAuth ⏱️ 15 minutes
### Test 2: Facebook OAuth ⏱️ 15 minutes
### Test 3: Instagram OAuth ⏱️ 15 minutes (Optional)
### Test 4: LinkedIn OAuth ⏱️ 5 minutes (When approved)
### Test 5: Multi-Platform Post ⏱️ 30 minutes
### Test 6: Error Handling ⏱️ 15 minutes

---

## 🐦 Test 1: Twitter OAuth (15 min)

### Step 1: Access the Application
1. Open browser
2. Go to: `http://localhost:3000`
3. Sign in to your account (if not already)

### Step 2: Navigate to Settings
1. Click on your profile/avatar (top right)
2. Select **"Settings"** from dropdown
3. Or go directly to: `http://localhost:3000/dashboard/settings`

### Step 3: Find Social Accounts Section
1. Look for **"Social Accounts"** or **"Connected Accounts"**
2. You should see options for:
   - Twitter/X
   - LinkedIn
   - Facebook
   - Instagram

### Step 4: Connect Twitter
1. Click **"Connect Twitter"** button
2. You'll be redirected to Twitter authorization page
3. Review the permissions requested
4. Click **"Authorize app"**

**Expected Result**: 
- ✅ Redirected back to your dashboard
- ✅ Twitter shows as "Connected" with green checkmark
- ✅ Your Twitter username displayed

**If it fails**:
- Check backend logs for errors
- Verify localtunnel is running: `https://aigrowth.loca.lt`
- Ensure Twitter redirect URI is: `https://aigrowth.loca.lt/api/oauth/twitter/callback`

### Step 5: Test Twitter Posting
1. Go to **Content** or **Dashboard**
2. Click **"Create Post"** or **"New Content"**
3. Write a test message: "Testing AI Growth Manager! 🚀 #automation"
4. Select **Twitter** as the platform
5. Click **"Publish Now"**

**Expected Result**:
- ✅ Success message displayed
- ✅ Post appears on your Twitter timeline
- ✅ Backend logs show successful API call

**Screenshot for Documentation**: ✅ Take a screenshot of successful Twitter post

---

## 📘 Test 2: Facebook OAuth (15 min)

### Step 1: Navigate to Social Accounts
1. Still in Settings → Social Accounts
2. Find **"Connect Facebook"** button

### Step 2: Connect Facebook
1. Click **"Connect Facebook"**
2. Redirected to Facebook authorization
3. **Important**: Select the Facebook Pages you want to manage
4. Review permissions
5. Click **"Continue"** or **"Authorize"**

**Expected Result**:
- ✅ Redirected back to dashboard
- ✅ Facebook shows as "Connected"
- ✅ Your Facebook Page name(s) displayed

**Note**: You must be an admin of at least one Facebook Page to connect

### Step 3: Test Facebook Posting
1. Go to **Create Post**
2. Write: "Testing AI Growth Manager on Facebook! 🎉"
3. Select **Facebook** as platform
4. If you have multiple Pages, select which one
5. Click **"Publish Now"**

**Expected Result**:
- ✅ Success message
- ✅ Post appears on your Facebook Page
- ✅ Visible to page followers

**Screenshot for Documentation**: ✅ Take screenshot of Facebook post

---

## 📸 Test 3: Instagram OAuth (15 min) - OPTIONAL

**Requirements**:
- Instagram account must be Business or Creator
- Must be linked to a Facebook Page
- You must be Page admin

### Step 1: Convert to Business Account (If Needed)
1. Open Instagram mobile app
2. Go to **Settings** → **Account**
3. Tap **"Switch to Professional Account"**
4. Choose **"Business"**
5. Connect to your Facebook Page
6. Complete setup

### Step 2: Connect Instagram
1. In your dashboard Settings → Social Accounts
2. Click **"Connect Instagram"**
3. Redirected to Facebook/Instagram authorization
4. Select your Instagram Business account
5. Review permissions
6. Click **"Continue"**

**Expected Result**:
- ✅ Instagram shows as "Connected"
- ✅ Your Instagram username displayed

### Step 3: Test Instagram Posting
1. Go to **Create Post**
2. **IMPORTANT**: Upload an image (required for Instagram)
3. Write caption: "Testing AI Growth Manager! 🎨 #automation #ai"
4. Select **Instagram** as platform
5. Click **"Publish Now"**

**Expected Result**:
- ✅ Success message
- ✅ Post appears on your Instagram feed
- ✅ Image and caption visible

**Note**: Instagram requires images for feed posts

**Screenshot for Documentation**: ✅ Take screenshot of Instagram post

---

## 💼 Test 4: LinkedIn OAuth (5 min) - PENDING APPROVAL

### Current Status:
- ✅ LinkedIn app configured
- ⏳ "Share on LinkedIn" access pending (24-72 hours)
- 📧 Check email for approval notification

### When Approved:
1. Go to Settings → Social Accounts
2. Click **"Connect LinkedIn"**
3. Authorize with your LinkedIn account
4. Test posting similar to other platforms

**Expected Result** (when approved):
- ✅ LinkedIn shows as "Connected"
- ✅ Can post to LinkedIn personal profile or company pages

---

## 🚀 Test 5: Multi-Platform Post (30 min)

### Goal: Post to Multiple Platforms Simultaneously

### Step 1: Create Multi-Platform Content
1. Go to **Create Post** or **Content**
2. Write a versatile message:
   ```
   🚀 Big announcement! 
   
   We're excited to share our new AI-powered social media management platform.
   
   ✨ AI content generation
   📊 Multi-platform posting
   📈 Analytics & insights
   
   #AI #SocialMedia #Automation #Tech
   ```

### Step 2: Select Multiple Platforms
1. Check boxes for: **Twitter**, **Facebook**, (Instagram if ready)
2. Preview how it looks on each platform
3. Make any platform-specific adjustments if needed

### Step 3: Publish
1. Click **"Publish Now"**
2. Wait for confirmation

**Expected Result**:
- ✅ Success message for each platform
- ✅ Post appears on all selected platforms
- ✅ Same content, properly formatted for each platform

### Step 4: Verify on Each Platform
1. Open Twitter → Check your timeline ✅
2. Open Facebook → Check your Page ✅
3. Open Instagram → Check your feed ✅ (if included)

**Screenshot for Documentation**: ✅ Take screenshots from each platform

---

## 🔍 Test 6: Error Handling (15 min)

### Test 6A: Disconnection & Reconnection
1. In Settings, click **"Disconnect"** on one platform
2. Verify it shows as disconnected
3. Reconnect the platform
4. Verify it works again

**Expected Result**:
- ✅ Clean disconnection
- ✅ No errors
- ✅ Successful reconnection

### Test 6B: Invalid Post
1. Try to post without any content
2. Try to post to Instagram without an image

**Expected Result**:
- ✅ Validation errors displayed
- ✅ Helpful error messages
- ✅ No backend crashes

### Test 6C: Expired Token Simulation
(This will happen naturally over time, but you can note the behavior)

**Expected Result** (when tokens expire):
- ✅ User notified to reconnect
- ✅ Clear re-authorization flow
- ✅ No data loss

---

## 📊 Testing Results Template

### Twitter OAuth Test
- [ ] Connection successful
- [ ] Posting successful
- [ ] Error handling works
- **Issues**: _None_ or _[describe]_

### Facebook OAuth Test
- [ ] Connection successful
- [ ] Page selection works
- [ ] Posting successful
- **Issues**: _None_ or _[describe]_

### Instagram OAuth Test (Optional)
- [ ] Business account connected
- [ ] Posting with image successful
- **Issues**: _None_ or _[describe]_

### LinkedIn OAuth Test (Pending)
- [ ] Waiting for approval
- [ ] Will test when approved
- **Expected**: _[date]_

### Multi-Platform Test
- [ ] Posted to multiple platforms simultaneously
- [ ] All platforms received post
- [ ] Formatting correct on each
- **Issues**: _None_ or _[describe]_

---

## 🐛 Common Issues & Solutions

### Issue: "Redirect URI Mismatch"
**Solution**:
- Ensure localtunnel is running
- Check OAuth redirect URLs in each platform's settings
- URLs must be exactly: `https://aigrowth.loca.lt/api/oauth/[platform]/callback`

### Issue: "Invalid Client Credentials"
**Solution**:
- Verify credentials in `backend/.env`
- Restart backend server
- Check for typos in App ID/Secret

### Issue: "Connection Timeout"
**Solution**:
- Check backend is running: `curl http://localhost:8003/health`
- Verify frontend is running: `http://localhost:3000`
- Ensure localtunnel is active: `https://aigrowth.loca.lt`

### Issue: "Instagram Can't Connect"
**Solution**:
- Verify Instagram is Business or Creator account
- Ensure linked to Facebook Page
- You must be Page admin

### Issue: "Posts Not Appearing"
**Solution**:
- Check backend logs for API errors
- Verify platform rate limits not exceeded
- Ensure content complies with platform policies

---

## 🎥 Documentation Checklist

### Screenshots to Capture:
- [ ] Twitter OAuth success screen
- [ ] Twitter post on timeline
- [ ] Facebook OAuth success screen
- [ ] Facebook post on Page
- [ ] Instagram OAuth success (if testing)
- [ ] Instagram post in feed (if testing)
- [ ] Multi-platform posting interface
- [ ] Success confirmation messages
- [ ] Dashboard with all platforms connected

### Videos to Record (Optional):
- [ ] Complete OAuth flow for one platform
- [ ] Creating and publishing multi-platform post
- [ ] Disconnecting and reconnecting account

---

## 📝 Testing Notes

### What to Document:
1. **Success Path**:
   - How long each OAuth flow took
   - Any confusing steps
   - User experience observations

2. **Edge Cases Found**:
   - Unexpected behavior
   - Unclear error messages
   - Performance issues

3. **Improvements Needed**:
   - UI/UX enhancements
   - Missing features
   - Better error handling

---

## ✅ Test Completion Criteria

### All Tests Pass When:
- ✅ Can connect all available platforms (Twitter, Facebook, Meta)
- ✅ Can post to each platform individually
- ✅ Can post to multiple platforms simultaneously
- ✅ Error messages are clear and helpful
- ✅ Disconnection/reconnection works smoothly
- ✅ No backend crashes or errors
- ✅ Posts appear correctly on all platforms

---

## 🎉 After Testing

### Success Checklist:
- [ ] All OAuth flows tested
- [ ] All platforms posting successfully
- [ ] Screenshots captured
- [ ] Issues documented
- [ ] Update project tracker to 80%
- [ ] Create testing summary document

### Next Steps (Day 5):
- Build content calendar UI
- Implement scheduled posting
- Add post preview feature
- Create analytics dashboard (Week 4)

---

## 🚀 Ready to Begin?

**Current Status**:
- ✅ Backend: Running
- ✅ Frontend: Running
- ✅ Localtunnel: Active
- ✅ Credentials: Loaded

**Start Here**:
1. Open browser: `http://localhost:3000`
2. Begin with Test 1: Twitter OAuth
3. Follow the guide step by step
4. Document everything!

---

**Good luck with testing!** 🎯

Let me know if you encounter any issues! 💪
