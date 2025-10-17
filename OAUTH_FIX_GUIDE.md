# OAuth Token Expiration - Complete Fix Guide

## Problem
- Twitter tokens expire after 2 hours
- Cloudflare tunnels change URLs frequently
- This breaks OAuth callbacks

## Best Solutions (Choose One)

### ✅ Solution 1: Deploy Backend (RECOMMENDED)
**Deploy to Railway.app (Free)**

1. Push code to GitHub
2. Go to https://railway.app
3. Sign in with GitHub
4. Click "New Project" → "Deploy from GitHub repo"
5. Select your repo
6. Add environment variables from `.env`
7. Deploy!

**You'll get a permanent URL like:** `https://your-app.railway.app`

**Then update OAuth providers:**
- Twitter: `https://your-app.railway.app/api/v1/oauth/twitter/callback`
- Meta: `https://your-app.railway.app/api/v1/oauth/meta/callback`
- LinkedIn: `https://your-app.railway.app/api/v1/oauth/linkedin/callback`

### 💰 Solution 2: ngrok Paid ($8/month)
**Get permanent subdomain**

1. Sign up at https://ngrok.com
2. Upgrade to paid plan
3. Get permanent URL: `https://your-app.ngrok.io`
4. Run: `ngrok http 8003 --subdomain=your-app`
5. Update OAuth providers once

### 🔧 Solution 3: Manual Token Refresh (Development Only)
**For testing without deployment:**

1. **Keep one terminal running cloudflared:**
   ```bash
   cloudflared tunnel --url http://localhost:8003
   ```

2. **When URL changes, update `.env` and restart backend:**
   ```bash
   # Update TWITTER_REDIRECT_URI, META_REDIRECT_URI, LINKEDIN_REDIRECT_URI
   # Then restart backend
   ```

3. **Update OAuth providers with new URL**

4. **Disconnect and reconnect each platform in Settings**

## Token Management

### Twitter Token Lifecycle
- **Expires:** 2 hours after connection
- **Refresh:** Available (we store refresh_token)
- **Manual:** Disconnect → Reconnect to get fresh token

### Meta Token Lifecycle
- **Expires:** 60 days
- **Refresh:** Auto-refreshed by platform
- **Page Token:** Never expires

### LinkedIn Token Lifecycle
- **Expires:** 60 days
- **Refresh:** No refresh available
- **Manual:** Must reconnect after expiration

## Quick Fix for Expired Token

1. Go to **Settings → Social Accounts**
2. Click **Disconnect** on expired platform
3. Click **Connect** to get fresh token
4. Authorize on platform
5. Test publishing immediately

## Production Checklist

- [ ] Deploy backend to Railway/Render/Fly.io
- [ ] Add all environment variables
- [ ] Update OAuth redirect URIs in all providers
- [ ] Test OAuth flow with production URL
- [ ] Implement token refresh for Twitter
- [ ] Set up monitoring for token expiration
- [ ] Add user notifications for expiring tokens

## Support

If tunnel keeps changing:
1. Stop using free Cloudflare tunnels
2. Deploy to production (Railway recommended)
3. Or use ngrok paid plan

For token expiration:
1. Implement automatic token refresh (in roadmap)
2. For now, reconnect manually when expired
3. Production deployment will be more stable
