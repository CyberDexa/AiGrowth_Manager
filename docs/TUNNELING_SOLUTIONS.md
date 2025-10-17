# OAuth Tunneling Solutions for Development

**Problem**: Localtunnel shows a security page that blocks OAuth callbacks from Facebook, Twitter, and LinkedIn.

**Your Tunnel Password**: `80.40.7.103` (your public IP)

---

## Solution 1: Ngrok (Best Option - Paid) ⭐

**Pros**:
- No security pages blocking OAuth
- More reliable than localtunnel
- Better performance
- Persistent URLs available

**Setup**:
1. Sign up at [https://ngrok.com](https://ngrok.com)
2. Get your auth token from dashboard
3. Install auth token:
   ```bash
   ngrok authtoken YOUR_AUTH_TOKEN
   ```
4. Start tunnel:
   ```bash
   ngrok http 8003
   ```
5. You'll get a URL like: `https://abc123.ngrok.io`
6. Update all OAuth redirect URIs with this new URL

**Cost**: Free tier available (limited), Pro is $8/month

---

## Solution 2: Cloudflare Tunnel (Free & Best)

**Pros**:
- Completely free
- No security pages
- Very reliable
- No sign-up needed for basic use

**Setup**:
1. Install cloudflared:
   ```bash
   brew install cloudflare/cloudflare/cloudflared
   ```
2. Start tunnel:
   ```bash
   cloudflared tunnel --url http://localhost:8003
   ```
3. You'll get a URL like: `https://abc-def-123.trycloudflare.com`
4. Update all OAuth redirect URIs with this new URL

**Cost**: FREE ✅

---

## Solution 3: Bore.pub (Free Alternative)

**Pros**:
- Completely free
- No account needed
- No security pages

**Setup**:
1. Install bore:
   ```bash
   brew install bore-cli
   ```
2. Start tunnel:
   ```bash
   bore local 8003 --to bore.pub
   ```
3. You'll get a URL like: `https://abc123.bore.pub`
4. Update all OAuth redirect URIs with this new URL

**Cost**: FREE ✅

---

## Solution 4: Use Localtunnel with Bypass Header (Current - Not Recommended)

**Problem**: OAuth providers can't bypass the security page

**Workaround**: Unfortunately, OAuth providers (Facebook, Twitter, LinkedIn) send standard browser requests which trigger the security page. There's no way to add custom headers to their requests.

**Conclusion**: ❌ Not viable for OAuth development

---

## Recommended: Use Cloudflare Tunnel (Free)

### Step-by-Step Setup:

1. **Install cloudflared** (if not installed):
   ```bash
   brew install cloudflare/cloudflare/cloudflared
   ```

2. **Stop localtunnel**:
   ```bash
   pkill -f "lt --port"
   ```

3. **Start Cloudflare tunnel**:
   ```bash
   cloudflared tunnel --url http://localhost:8003
   ```

4. **You'll see output like**:
   ```
   Your quick Tunnel has been created! Visit it at:
   https://abc-def-123.trycloudflare.com
   ```

5. **Copy the URL** (example: `https://abc-def-123.trycloudflare.com`)

6. **Update backend/.env**:
   ```bash
   META_REDIRECT_URI=https://abc-def-123.trycloudflare.com/api/v1/oauth/meta/callback
   TWITTER_REDIRECT_URI=https://abc-def-123.trycloudflare.com/api/v1/oauth/twitter/callback
   LINKEDIN_REDIRECT_URI=https://abc-def-123.trycloudflare.com/api/v1/oauth/linkedin/callback
   ```

7. **Restart backend**:
   ```bash
   cd backend
   pkill -9 -f "uvicorn app.main:app"
   ./venv/bin/python -m uvicorn app.main:app --reload --port 8003
   ```

8. **Update OAuth Provider Settings**:

   **Meta (Facebook)**:
   - Go to: https://developers.facebook.com/apps/4284592478453354/fb-login/settings/
   - Update "Valid OAuth Redirect URIs" to:
     ```
     https://abc-def-123.trycloudflare.com/api/v1/oauth/meta/callback
     ```
   - Save Changes

   **Twitter**:
   - Go to: https://developer.twitter.com/en/portal/projects-and-apps
   - Update callback URL to:
     ```
     https://abc-def-123.trycloudflare.com/api/v1/oauth/twitter/callback
     ```

   **LinkedIn**:
   - Go to: https://www.linkedin.com/developers/apps
   - Update redirect URL to:
     ```
     https://abc-def-123.trycloudflare.com/api/v1/oauth/linkedin/callback
     ```

9. **Test OAuth flows** - Should work without security pages! ✅

---

## Quick Command to Switch to Cloudflare

Run these commands in sequence:

```bash
# 1. Install cloudflared (if not installed)
brew install cloudflare/cloudflare/cloudflared

# 2. Stop localtunnel
pkill -f "lt --port" 2>/dev/null

# 3. Start Cloudflare tunnel
cloudflared tunnel --url http://localhost:8003
```

Then update your OAuth provider settings with the new Cloudflare URL.

---

## Comparison Table

| Service | Free | Security Page | Reliability | Speed | Setup Time |
|---------|------|---------------|-------------|-------|------------|
| **Cloudflare Tunnel** | ✅ Yes | ❌ No | ⭐⭐⭐⭐⭐ | ⚡ Fast | 2 min |
| **Ngrok (Free)** | ⚠️ Limited | ❌ No | ⭐⭐⭐⭐ | ⚡ Fast | 5 min |
| **Bore.pub** | ✅ Yes | ❌ No | ⭐⭐⭐ | 🐢 Slow | 2 min |
| **Localtunnel** | ✅ Yes | ✅ YES (BLOCKS OAUTH) | ⭐⭐ | 🐢 Slow | 1 min |

---

## Recommended Action

**Use Cloudflare Tunnel** - it's free, fast, and has no security pages that block OAuth.

---

## After Switching Tunnel Service

Remember to update these locations:

1. ✅ `backend/.env` - All three redirect URIs
2. ✅ Meta Developer Console - Valid OAuth Redirect URIs
3. ✅ Twitter Developer Portal - Callback URLs
4. ✅ LinkedIn Developer Portal - Redirect URLs
5. ✅ Restart backend server
6. ✅ Test OAuth flows

---

## Need Help?

If you run into issues:
1. Make sure the tunnel is running and accessible
2. Verify redirect URIs match exactly (including `/api/v1/oauth/`)
3. Check backend logs for errors
4. Test the tunnel URL in your browser first
