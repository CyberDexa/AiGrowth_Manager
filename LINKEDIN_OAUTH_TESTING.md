# LinkedIn OAuth - Testing Guide

## ❌ What You're Doing Wrong

You're accessing the callback URL directly:
```
https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback
```

**This will always fail!** The callback URL expects LinkedIn to send it with a `code` parameter, like:
```
https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback?code=XXX&state=YYY
```

## ✅ How to Test OAuth Properly

### Method 1: Test Through Your App (Recommended)

1. Make sure your frontend is running: `npm run dev`
2. Go to http://localhost:3000/dashboard/settings
3. Click **Social Connections** tab
4. Click **Connect** button on LinkedIn card
5. This will:
   - Call your backend to get authorization URL
   - Redirect you to LinkedIn
   - LinkedIn redirects back with code
   - Backend processes the code
   - You get redirected back to settings

### Method 2: Test Authorization URL Directly

You can test if the authorization URL generation works:

**1. Get Your Business ID**

Go to your database or check the URL when you're on dashboard. It's usually `1` for your first business.

**2. Call the Authorization Endpoint**

Open this URL in your browser (replace `YOUR_BUSINESS_ID` with actual ID):

```
https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/authorize?business_id=1
```

You need to be authenticated, so this might not work from browser directly. Use the app instead.

### Method 3: Test with cURL

```bash
# Step 1: Get authorization URL
curl -X GET "https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/authorize?business_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# You'll get back something like:
# {
#   "authorization_url": "https://www.linkedin.com/oauth/v2/authorization?...",
#   "state": "abc123...",
#   "platform": "linkedin",
#   "business_id": 1
# }

# Step 2: Visit the authorization_url in your browser
# Step 3: LinkedIn will redirect back to callback with code
```

## 🔍 Debugging - Check If Configuration Is Correct

### Test 1: Verify Environment Variables Are Set

Check if Render has the variables:

1. Go to https://dashboard.render.com
2. Click your backend service
3. Go to **Environment** tab
4. Verify these exist:
   - `LINKEDIN_CLIENT_ID` (your LinkedIn app client ID)
   - `LINKEDIN_CLIENT_SECRET` (your LinkedIn app client secret)
   - `LINKEDIN_REDIRECT_URI=https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback`

### Test 2: Check Backend Logs

1. Go to https://dashboard.render.com
2. Click your backend service
3. Go to **Logs** tab
4. Try to connect LinkedIn from your app
5. Look for log messages like:
   ```
   Generated LinkedIn authorization URL with state: abc123...
   ```

### Test 3: Verify LinkedIn App Settings

1. Go to https://www.linkedin.com/developers/apps
2. Click your app
3. Go to **Auth** tab
4. Under **OAuth 2.0 settings** → **Redirect URLs**
5. Verify it contains:
   ```
   https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback
   ```

## 📋 Complete Test Procedure

### Step 1: Verify Frontend Configuration

Check that your frontend is pointing to the right backend:

**File:** `frontend/.env.local`
```bash
NEXT_PUBLIC_API_URL=https://ai-growth-manager.onrender.com
```

Or check the code directly to see what API URL it's using.

### Step 2: Test the Full Flow

1. **Start Fresh:**
   - Clear browser cookies for your app
   - Go to http://localhost:3000
   - Sign in to your account

2. **Go to Settings:**
   - Navigate to http://localhost:3000/dashboard/settings
   - Click **Social Connections** tab

3. **Click Connect LinkedIn:**
   - Click the **Connect** button on LinkedIn card
   - Open browser DevTools (F12) → **Network** tab to monitor requests

4. **Watch What Happens:**
   
   **Expected Flow:**
   
   a. **Frontend calls backend:**
   ```
   GET https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/authorize?business_id=1
   ```
   
   b. **Backend responds with:**
   ```json
   {
     "authorization_url": "https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=77ftqu4rb7v7r2&redirect_uri=https%3A%2F%2Fai-growth-manager.onrender.com%2Fapi%2Fv1%2Foauth%2Flinkedin%2Fcallback&scope=openid+profile+email+w_member_social&state=...",
     "state": "...",
     "platform": "linkedin",
     "business_id": 1
   }
   ```
   
   c. **Frontend redirects you to LinkedIn:**
   - You see LinkedIn login page
   - You enter credentials
   - LinkedIn asks for permissions
   
   d. **You authorize the app**
   
   e. **LinkedIn redirects back:**
   ```
   https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback?code=AQT...&state=...
   ```
   
   f. **Backend processes the callback:**
   - Exchanges code for access token
   - Stores token in database
   - Redirects you back to settings
   
   g. **You're back at settings:**
   ```
   http://localhost:3000/dashboard/settings?tab=social&success=linkedin
   ```
   
   h. **LinkedIn shows as connected** ✅

### Step 3: If It Fails, Check These

**Error: "Authorization URL not found"**
- Backend not running or not reachable
- Check Render logs for errors
- Verify backend URL is correct

**Error: "redirect_uri_mismatch" from LinkedIn**
- Redirect URI in Render doesn't match LinkedIn app settings
- Double-check both are EXACTLY the same
- No typos, extra spaces, or trailing slashes

**Error: "invalid_client"**
- Wrong Client ID or Client Secret in Render
- Verify credentials match LinkedIn app

**Error: "Field required" on callback**
- You're accessing callback URL directly (don't do this)
- OR LinkedIn can't reach your callback URL
- Verify redirect URI is correct and accessible

## 🎯 Quick Diagnostic Script

Save this as `test_linkedin_oauth.py` in your backend directory:

```python
#!/usr/bin/env python3
"""Test LinkedIn OAuth configuration"""
import os
from app.services.oauth_linkedin import linkedin_oauth

print("=" * 60)
print("LinkedIn OAuth Configuration Test")
print("=" * 60)
print()

# Check configuration
print("1. Configuration Check:")
print(f"   Client ID: {linkedin_oauth.client_id}")
print(f"   Client Secret: {'***' + linkedin_oauth.client_secret[-4:] if linkedin_oauth.client_secret else 'NOT SET'}")
print(f"   Redirect URI: {linkedin_oauth.redirect_uri}")
print()

# Generate authorization URL
print("2. Generate Authorization URL:")
auth_url, state = linkedin_oauth.get_authorization_url()
print(f"   State: {state}")
print(f"   URL: {auth_url[:100]}...")
print()

# Check if URL is valid
if "client_id=" in auth_url and "redirect_uri=" in auth_url:
    print("✅ Authorization URL looks valid!")
else:
    print("❌ Authorization URL might be invalid")

print()
print("=" * 60)
print("Next Steps:")
print("1. Copy the authorization URL above")
print("2. Paste it in your browser")
print("3. Login to LinkedIn")
print("4. Authorize the app")
print("5. You'll be redirected to callback URL with code")
print("=" * 60)
```

Run it:
```bash
cd backend
python test_linkedin_oauth.py
```

## 🚨 Common Mistakes

### ❌ DON'T: Test callback URL directly
```
https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback
```
This will always fail because there's no `code` parameter.

### ✅ DO: Test through the authorize endpoint
```
https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/authorize?business_id=1
```
Or better yet, use your app's UI.

### ❌ DON'T: Use http:// for production
```
http://ai-growth-manager.onrender.com/...
```
Render uses HTTPS, so should your redirect URI.

### ✅ DO: Use https:// for Render
```
https://ai-growth-manager.onrender.com/...
```

## 📊 Checklist

Before testing, verify:

- [ ] `LINKEDIN_REDIRECT_URI` in Render = `https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback`
- [ ] Redirect URL in LinkedIn app = `https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback`
- [ ] Both match EXACTLY (no trailing slash, same protocol, same path)
- [ ] `LINKEDIN_CLIENT_ID` is set in Render
- [ ] `LINKEDIN_CLIENT_SECRET` is set in Render
- [ ] Backend is deployed and running on Render
- [ ] Frontend `NEXT_PUBLIC_API_URL` points to Render backend

Then test through the app, NOT by accessing callback URL directly.

## 📝 Expected Success Flow

```
User clicks "Connect LinkedIn"
    ↓
Frontend: GET /api/v1/oauth/linkedin/authorize?business_id=1
    ↓
Backend: Returns authorization_url
    ↓
Frontend: window.location.href = authorization_url
    ↓
User lands on LinkedIn login page
    ↓
User logs in and authorizes app
    ↓
LinkedIn: Redirects to callback URL with code
    GET /api/v1/oauth/linkedin/callback?code=XXX&state=YYY
    ↓
Backend: Exchanges code for access token
    ↓
Backend: Stores token in database
    ↓
Backend: Redirects to frontend with success
    RedirectResponse → http://localhost:3000/dashboard/settings?success=linkedin
    ↓
Frontend: Shows "LinkedIn Connected" ✅
```

---

**Bottom Line:** Don't test the callback URL directly. Test through your app by clicking "Connect LinkedIn" button!
