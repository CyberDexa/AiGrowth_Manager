# OAuth Redirect URIs - Render Update Guide

## 🎯 Issue

All OAuth redirect URIs in your backend `.env` file are pointing to an inactive Cloudflare tunnel:
```
https://colour-decades-pendant-introducing.trycloudflare.com
```

This needs to be updated to your Render backend URL:
```
https://ai-growth-manager.onrender.com
```

## ✅ Updated Environment Variables

Copy these **exact values** to update in Render:

```bash
# Twitter OAuth
TWITTER_REDIRECT_URI=https://ai-growth-manager.onrender.com/api/v1/oauth/twitter/callback

# Meta (Facebook/Instagram) OAuth
META_REDIRECT_URI=https://ai-growth-manager.onrender.com/api/v1/oauth/meta/callback

# LinkedIn OAuth
LINKEDIN_REDIRECT_URI=https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback
```

## 📋 How to Update in Render

### Method 1: Render Dashboard (Recommended)

1. Go to https://dashboard.render.com
2. Click on your **backend service** (`ai-growth-manager`)
3. Click **Environment** tab on the left
4. Find each variable or click **Add Environment Variable**:

   **For Twitter:**
   - Key: `TWITTER_REDIRECT_URI`
   - Value: `https://ai-growth-manager.onrender.com/api/v1/oauth/twitter/callback`

   **For Meta:**
   - Key: `META_REDIRECT_URI`
   - Value: `https://ai-growth-manager.onrender.com/api/v1/oauth/meta/callback`

   **For LinkedIn:**
   - Key: `LINKEDIN_REDIRECT_URI`
   - Value: `https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback`

5. Click **Save Changes**
6. Render will automatically redeploy (~2-3 minutes)

### Method 2: Blueprint File (Alternative)

If you're using `render.yaml`:

```yaml
services:
  - type: web
    name: ai-growth-manager
    env: python
    envVars:
      - key: TWITTER_REDIRECT_URI
        value: https://ai-growth-manager.onrender.com/api/v1/oauth/twitter/callback
      - key: META_REDIRECT_URI
        value: https://ai-growth-manager.onrender.com/api/v1/oauth/meta/callback
      - key: LINKEDIN_REDIRECT_URI
        value: https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback
```

## 🔧 Update OAuth Provider Consoles

After updating Render, you **MUST** also update each OAuth provider's developer console:

### LinkedIn Developer Console

1. Go to https://www.linkedin.com/developers/apps
2. Select your app
3. Go to **Auth** tab
4. Under **OAuth 2.0 settings** → **Redirect URLs**
5. Add: `https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback`
6. Click **Update**

### Twitter Developer Portal

1. Go to https://developer.twitter.com/en/portal/dashboard
2. Select your app
3. Go to **User authentication settings** or **App settings**
4. Under **Callback URI / Redirect URL**
5. Add: `https://ai-growth-manager.onrender.com/api/v1/oauth/twitter/callback`
6. Click **Save**

### Meta (Facebook) Developer Console

1. Go to https://developers.facebook.com/apps
2. Select your app
3. Go to **Facebook Login** → **Settings**
4. Under **Valid OAuth Redirect URIs**
5. Add: `https://ai-growth-manager.onrender.com/api/v1/oauth/meta/callback`
6. Click **Save Changes**

## 🧪 Local Development (Optional)

If you want to test OAuth locally, add these to your **local** `.env` file:

```bash
# For local testing (backend on port 8000)
TWITTER_REDIRECT_URI=http://localhost:8000/api/v1/oauth/twitter/callback
META_REDIRECT_URI=http://localhost:8000/api/v1/oauth/meta/callback
LINKEDIN_REDIRECT_URI=http://localhost:8000/api/v1/oauth/linkedin/callback
```

Then add these URLs to each provider's developer console as well (they support multiple redirect URIs).

## ✅ Verification Checklist

After updating everything:

- [ ] Updated `TWITTER_REDIRECT_URI` in Render
- [ ] Updated `META_REDIRECT_URI` in Render
- [ ] Updated `LINKEDIN_REDIRECT_URI` in Render
- [ ] Waited for Render to redeploy (~3 min)
- [ ] Updated LinkedIn Developer Console
- [ ] Updated Twitter Developer Portal
- [ ] Updated Meta Developer Console
- [ ] Tested LinkedIn connection in app
- [ ] Tested Twitter connection in app
- [ ] Tested Meta connection in app

## 🔍 How to Test

1. Wait for Render backend to finish deploying
2. Go to http://localhost:3000/dashboard/settings
3. Click **Social Connections** tab
4. Try connecting each platform:
   - Click **Connect** on LinkedIn
   - Should redirect to LinkedIn login
   - After authorizing, should redirect back with success
   - Repeat for Twitter and Meta

## 🚨 Common Errors

### Error: "redirect_uri_mismatch"
**Cause:** URL in code doesn't match URL in developer console  
**Fix:** Verify exact match (protocol, domain, path, no typos)

### Error: "Field required" (code missing)
**Cause:** Provider can't reach callback URL  
**Fix:** Verify redirect URI is correct and backend is running

### Error: "invalid_client"
**Cause:** Wrong Client ID or Client Secret  
**Fix:** Verify credentials in Render match developer console

## 📊 Current vs New URLs

| Provider | Old (Broken) | New (Working) |
|----------|-------------|---------------|
| LinkedIn | `https://colour-decades-pendant...cloudflare.com/api/v1/oauth/linkedin/callback` | `https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback` |
| Twitter | `https://colour-decades-pendant...cloudflare.com/api/v1/oauth/twitter/callback` | `https://ai-growth-manager.onrender.com/api/v1/oauth/twitter/callback` |
| Meta | `https://colour-decades-pendant...cloudflare.com/api/v1/oauth/meta/callback` | `https://ai-growth-manager.onrender.com/api/v1/oauth/meta/callback` |

## ⚡ Quick Copy-Paste for Render

```
TWITTER_REDIRECT_URI=https://ai-growth-manager.onrender.com/api/v1/oauth/twitter/callback
META_REDIRECT_URI=https://ai-growth-manager.onrender.com/api/v1/oauth/meta/callback
LINKEDIN_REDIRECT_URI=https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback
```

## 📝 Summary

**What's Wrong:**  
Old Cloudflare tunnel URLs that no longer work

**What to Do:**  
1. Update 3 environment variables in Render
2. Update 3 redirect URIs in developer consoles
3. Wait for deployment
4. Test connections

**Expected Result:**  
OAuth connections work properly, users can connect social accounts

---

**Next Action:** Update the environment variables in Render, then update each OAuth provider's developer console!
