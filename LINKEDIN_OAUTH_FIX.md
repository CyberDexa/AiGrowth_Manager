# LinkedIn OAuth Connection Fix

## 🐛 Error You're Seeing

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["query", "code"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

## 🔍 Root Cause

The error occurs because LinkedIn is redirecting to the wrong callback URL. Your backend `.env` file has an old Cloudflare tunnel URL:

```
LINKEDIN_REDIRECT_URI=https://colour-decades-pendant-introducing.trycloudflare.com/api/v1/oauth/linkedin/callback
```

This tunnel is no longer active, so LinkedIn can't properly redirect back with the authorization `code`.

## ✅ Solution

You need to update the redirect URI in **two places**:

### 1. Backend Environment Variable

Update your backend `.env` file (or Render environment variables) to use your Render URL:

```bash
LINKEDIN_REDIRECT_URI=https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback
```

### 2. LinkedIn Developer Console

You **must also** update the redirect URI in your LinkedIn app settings:

1. Go to https://www.linkedin.com/developers/apps
2. Select your app (or create one if you haven't)
3. Go to **Auth** tab
4. Under **OAuth 2.0 settings**, find **Redirect URLs**
5. Add or update to:
   ```
   https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback
   ```
6. Click **Update**

### 3. For Local Development (Optional)

If you also want to test locally, you can add a local redirect URL:

**In LinkedIn Developer Console:**
```
http://localhost:8000/api/v1/oauth/linkedin/callback
```

**In your local `.env`:**
```bash
LINKEDIN_REDIRECT_URI=http://localhost:8000/api/v1/oauth/linkedin/callback
```

## 📋 Step-by-Step Fix

### Step 1: Update Render Environment Variables

1. Go to https://dashboard.render.com
2. Click on your **backend service** (`ai-growth-manager`)
3. Go to **Environment** tab
4. Find `LINKEDIN_REDIRECT_URI` or add it
5. Set value to: `https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback`
6. Click **Save Changes**
7. Wait for backend to redeploy (~2 minutes)

### Step 2: Update LinkedIn Developer Console

1. Visit https://www.linkedin.com/developers/apps
2. Sign in with your LinkedIn account
3. Click on your app or **Create app** if you don't have one:
   - **App name**: AI Growth Manager
   - **LinkedIn Page**: Select your company page or create one
   - **App logo**: Upload any logo
   - **Legal agreement**: Check the box
4. Once created, go to **Auth** tab
5. Scroll to **OAuth 2.0 settings**
6. Under **Redirect URLs**, click **+ Add redirect URL**
7. Enter: `https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback`
8. Click **Add**
9. Click **Update** to save

### Step 3: Verify Credentials

Make sure these environment variables are set in Render:

```bash
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_REDIRECT_URI=https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback
```

### Step 4: Test the Connection

1. Wait for Render backend to finish deploying
2. Go to your app: http://localhost:3000/dashboard/settings
3. Click **Social Connections** tab
4. Click **Connect** on LinkedIn
5. You should be redirected to LinkedIn login
6. After authorizing, you'll be redirected back to settings with success message

## 🔍 OAuth Flow Explained

1. **User clicks "Connect LinkedIn"**
   - Frontend calls: `GET /api/v1/oauth/linkedin/authorize?business_id=1`
   - Backend returns authorization URL

2. **User redirected to LinkedIn**
   - URL: `https://www.linkedin.com/oauth/v2/authorization?...`
   - User logs in and authorizes app

3. **LinkedIn redirects back**
   - Redirect to: `https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback?code=XXX&state=YYY`
   - This is where your error happens - LinkedIn can't find this URL because it's pointing to the wrong domain

4. **Backend receives callback**
   - Backend exchanges `code` for `access_token`
   - Stores token in database
   - Redirects user back to frontend with success

## ⚠️ Important Notes

### Redirect URI Must Match EXACTLY

The redirect URI in your code **must exactly match** what's configured in LinkedIn:
- Protocol: `https://` (not `http://` in production)
- Domain: `ai-growth-manager.onrender.com`
- Path: `/api/v1/oauth/linkedin/callback`
- No trailing slash
- No extra query parameters

### Multiple Redirect URIs

LinkedIn allows multiple redirect URIs. You can have:
- Production: `https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback`
- Local: `http://localhost:8000/api/v1/oauth/linkedin/callback`

Just switch the `LINKEDIN_REDIRECT_URI` environment variable depending on where you're testing.

### LinkedIn App Verification

LinkedIn may require app verification for certain scopes. Basic profile access should work without verification.

## 🚨 Common Errors

### Error: "redirect_uri_mismatch"
**Cause:** Redirect URI doesn't match what's configured in LinkedIn  
**Fix:** Double-check spelling, protocol (http vs https), domain, and path

### Error: "Field required" (your current error)
**Cause:** LinkedIn can't reach your callback URL  
**Fix:** Update redirect URI to point to active backend

### Error: "invalid_client"
**Cause:** Wrong Client ID or Client Secret  
**Fix:** Verify credentials in Render environment variables match LinkedIn app

### Error: "access_denied"
**Cause:** User declined authorization  
**Fix:** This is normal - user chose not to connect

## ✅ Expected Result

After fixing:

1. Click "Connect LinkedIn" in settings
2. Redirected to LinkedIn login
3. LinkedIn shows authorization prompt
4. After authorizing, redirected back to your app
5. See green "Connected" status on LinkedIn card
6. LinkedIn account listed with your name/email

## 📝 Quick Reference

**Current (broken) redirect URI:**
```
https://colour-decades-pendant-introducing.trycloudflare.com/api/v1/oauth/linkedin/callback
```

**New (working) redirect URI:**
```
https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback
```

**Environment variable to update:**
```bash
LINKEDIN_REDIRECT_URI=https://ai-growth-manager.onrender.com/api/v1/oauth/linkedin/callback
```

---

**Next Steps:**
1. Update Render environment variable
2. Update LinkedIn Developer Console
3. Wait for redeploy
4. Test connection

Let me know if you encounter any other errors!
