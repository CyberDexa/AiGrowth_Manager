# OAuth Testing Ready - Complete Setup Guide

## ✅ Current Status

All OAuth infrastructure is configured and running. Ready for testing!

## 🌐 Active Tunnel URL

**Current Cloudflare Tunnel:** `https://boats-weekends-sat-handmade.trycloudflare.com`

⚠️ **IMPORTANT:** This URL is temporary and will change if the tunnel restarts!

## 📋 Service Status

| Service | Status | URL |
|---------|--------|-----|
| Backend | ✅ Running | http://localhost:8003 |
| Frontend | ✅ Running | http://localhost:3000 |
| Cloudflare Tunnel | ✅ Running | https://boats-weekends-sat-handmade.trycloudflare.com |
| Redis | ⚠️ Not running (using in-memory fallback) | - |

## 🔧 Backend Configuration

All redirect URIs are configured in `backend/.env`:

```bash
# Twitter OAuth
TWITTER_REDIRECT_URI=https://boats-weekends-sat-handmade.trycloudflare.com/api/v1/oauth/twitter/callback

# Meta (Facebook/Instagram) OAuth
META_REDIRECT_URI=https://boats-weekends-sat-handmade.trycloudflare.com/api/v1/oauth/meta/callback

# LinkedIn OAuth
LINKEDIN_REDIRECT_URI=https://boats-weekends-sat-handmade.trycloudflare.com/api/v1/oauth/linkedin/callback
```

## 🎯 NEXT STEPS: Update OAuth Provider Settings

You must update the redirect URIs in each OAuth provider's settings to match the current tunnel URL.

### 1. Meta (Facebook/Instagram)

1. Go to: https://developers.facebook.com/apps/4284592478453354/fb-login/settings/
2. Find "Valid OAuth Redirect URIs"
3. Add or update to:
   ```
   https://boats-weekends-sat-handmade.trycloudflare.com/api/v1/oauth/meta/callback
   ```
4. Click "Save Changes"

### 2. Twitter

1. Go to: https://developer.twitter.com/en/portal/dashboard
2. Select your app "AI Growth Manager"
3. Go to "App settings" → "Authentication settings"
4. Update "Callback URI / Redirect URL" to:
   ```
   https://boats-weekends-sat-handmade.trycloudflare.com/api/v1/oauth/twitter/callback
   ```
5. Save changes

### 3. LinkedIn

1. Go to: https://www.linkedin.com/developers/apps
2. Select your app (Client ID: 77ftqu4rb7v7r2)
3. Go to "Auth" tab
4. Update "Redirect URLs" to:
   ```
   https://boats-weekends-sat-handmade.trycloudflare.com/api/v1/oauth/linkedin/callback
   ```
5. Save changes

## 🧪 Testing OAuth Flows

After updating all provider settings:

### 1. Test Twitter OAuth

1. Open http://localhost:3000 in your browser
2. Log in with Clerk
3. Go to "Settings" → "Social Accounts"
4. Click "Connect" next to Twitter
5. **Expected:** Redirected to Twitter authorization page
6. **Expected:** After authorizing, redirected back to your app with success message

### 2. Test Meta OAuth

1. In the same "Social Accounts" section
2. Click "Connect" next to Facebook / Instagram
3. **Expected:** Redirected to Facebook authorization page
4. **Expected:** After authorizing, redirected back to your app
5. **Expected:** Can select Facebook Pages and Instagram accounts

### 3. Test LinkedIn OAuth

1. Click "Connect" next to LinkedIn
2. **Expected:** Redirected to LinkedIn authorization page
3. **Expected:** After authorizing, redirected back to your app
4. **Note:** "Share on LinkedIn" permission may require approval

## 🔍 Troubleshooting

### If OAuth redirect fails:

1. **Check tunnel is running:**
   ```bash
   curl https://boats-weekends-sat-handmade.trycloudflare.com/health
   ```
   Should return: `{"status":"healthy","environment":"development"}`

2. **Verify backend is running:**
   ```bash
   curl http://localhost:8003/health
   ```
   Should return: `{"status":"healthy","environment":"development"}`

3. **Check redirect URI matches exactly:**
   - Provider settings must match backend .env EXACTLY
   - Including `https://`, domain, and `/api/v1/oauth/{platform}/callback`

4. **Check browser console for errors:**
   - Open browser DevTools (F12)
   - Look for failed requests or error messages

### If tunnel URL changed (tunnel restarted):

1. Get new tunnel URL from terminal where cloudflared is running
2. Update all 3 redirect URIs in `backend/.env`
3. Restart backend:
   ```bash
   cd backend
   ./venv/bin/uvicorn app.main:app --reload --port 8003
   ```
4. Update all 3 OAuth provider settings with new URL

## 📊 What Happens During OAuth Flow

1. **User clicks "Connect" button**
   - Frontend calls: `GET /api/v1/oauth/{platform}/authorize?business_id={id}`
   - Backend returns: `{"authorization_url": "https://..."}`
   - Frontend redirects user to authorization_url

2. **User authorizes on platform (Twitter/Meta/LinkedIn)**
   - Platform redirects to: `https://boats-weekends-sat-handmade.trycloudflare.com/api/v1/oauth/{platform}/callback?code=...&state=...`

3. **Backend handles callback**
   - Validates state (CSRF protection)
   - Exchanges code for access token
   - Stores tokens in database
   - Redirects to frontend success page

4. **Frontend shows success**
   - Account connected
   - Can now create/schedule posts

## 🔐 Security Notes

1. **State Parameter:** Used for CSRF protection, validated on callback
2. **PKCE (Twitter only):** Additional security layer for Twitter OAuth 2.0
3. **Token Storage:** Access tokens encrypted in database
4. **Tunnel Security:** Cloudflare tunnel is public but backend validates requests

## 📝 Testing Checklist

- [ ] Updated Meta redirect URI in Facebook Developer Console
- [ ] Updated Twitter redirect URI in Twitter Developer Portal
- [ ] Updated LinkedIn redirect URI in LinkedIn Developers
- [ ] Tested Twitter OAuth flow end-to-end
- [ ] Tested Meta OAuth flow end-to-end
- [ ] Tested LinkedIn OAuth flow end-to-end
- [ ] Verified tokens stored in database
- [ ] Can create posts on connected platforms

## 🚀 After Successful Testing

Once all OAuth flows work:

1. **Week 3 Day 5:** Multi-platform posting
2. **Week 4:** Analytics integration
3. **Production Deployment:** Use named Cloudflare tunnel or Ngrok

## 🆘 Need Help?

If you encounter issues:

1. Check logs in terminal where backend is running
2. Check browser console for frontend errors
3. Verify redirect URIs match EXACTLY
4. Ensure tunnel is still running
5. Test backend OAuth endpoint directly:
   ```bash
   curl "http://localhost:8003/api/v1/oauth/twitter/authorize?business_id=test-123"
   ```

---

**Last Updated:** 2025-10-17  
**Tunnel URL:** https://boats-weekends-sat-handmade.trycloudflare.com  
**Status:** Ready for testing ✅
