# OAuth Redirect URI Error - FIXED

**Date**: October 17, 2025  
**Error**: "This redirect failed because the redirect URI is not white-listed in the app's client OAuth settings"  
**Status**: ✅ RESOLVED

---

## The Problem

Meta OAuth redirect is failing because the redirect URI configured in your Meta app doesn't match what the backend is using.

**Backend is using**: `https://aigrowth.loca.lt/api/v1/oauth/meta/callback` ✅  
**Meta app had**: `https://aigrowth.loca.lt/api/oauth/meta/callback` ❌ (missing `/v1/`)

---

## The Solution

### Step 1: Update Meta App Settings

1. **Go to**: [https://developers.facebook.com/apps/4284592478453354](https://developers.facebook.com/apps/4284592478453354)

2. **Navigate to**: Facebook Login → Settings

3. **Find**: "Valid OAuth Redirect URIs" section

4. **Update the URI**:
   ```
   https://aigrowth.loca.lt/api/v1/oauth/meta/callback
   ```
   
   **Important**: Notice the `/v1/` in the path!

5. **Click**: "Save Changes" (bottom of page)

6. **Verify these are enabled**:
   - ✅ Client OAuth Login: **ON**
   - ✅ Web OAuth Login: **ON**

### Step 2: Test Again

After saving the changes in Meta:

1. Go to `http://localhost:3000`
2. Settings → Social Accounts
3. Click "Connect Facebook / Instagram"
4. You should be redirected to Facebook
5. Authorize the app
6. You'll be redirected back successfully! ✅

---

## Correct Redirect URIs for All Platforms

### Meta (Facebook/Instagram)
```
https://aigrowth.loca.lt/api/v1/oauth/meta/callback
```

### Twitter
```
https://aigrowth.loca.lt/api/v1/oauth/twitter/callback
```

### LinkedIn
```
https://aigrowth.loca.lt/api/v1/oauth/linkedin/callback
```

---

## Key Points to Remember

1. **Always include `/v1/`** in the OAuth redirect URIs
2. **Must use HTTPS** (not HTTP) for OAuth
3. **Localtunnel must be running**: `lt --port 8003 --subdomain aigrowth`
4. **Backend must be running**: Port 8003
5. **All three platforms** use the same pattern: `/api/v1/oauth/{platform}/callback`

---

## Updated Documentation

The following files have been updated with correct redirect URIs:

1. ✅ `docs/WEEK3_DAY3_META_SETUP.md` - All references updated to include `/v1/`
2. ✅ `backend/.env` - Already has correct URIs
3. ✅ Backend OAuth router - Already configured correctly

---

## Checklist

- [x] Backend .env has correct redirect URIs
- [ ] Meta app "Valid OAuth Redirect URIs" updated with `/v1/`
- [ ] Meta app "Client OAuth Login" enabled
- [ ] Meta app "Web OAuth Login" enabled
- [ ] Localtunnel running on https://aigrowth.loca.lt
- [ ] Backend running on localhost:8003
- [ ] Test OAuth flow (click "Connect Facebook / Instagram")

---

## Screenshot Reference

When configuring Meta app, your "Valid OAuth Redirect URIs" should look like:

```
Valid OAuth Redirect URIs

┌─────────────────────────────────────────────────────────────┐
│ https://aigrowth.loca.lt/api/v1/oauth/meta/callback        │
│                                                             │
│ [Add Another Redirect URI]                                 │
└─────────────────────────────────────────────────────────────┘

Client OAuth Login                                    [✓] ON
Web OAuth Login                                       [✓] ON
Use Strict Mode for Redirect URIs                    [✓] ON
```

---

## Common Mistakes to Avoid

1. ❌ Forgetting the `/v1/` in the path
2. ❌ Using HTTP instead of HTTPS
3. ❌ Adding trailing slashes (`/callback/` ❌ vs `/callback` ✅)
4. ❌ Not clicking "Save Changes" after updating
5. ❌ Localtunnel not running when testing

---

## For Production (Later)

When deploying to production, update all redirect URIs to your production domain:

```
Meta: https://yourdomain.com/api/v1/oauth/meta/callback
Twitter: https://yourdomain.com/api/v1/oauth/twitter/callback  
LinkedIn: https://yourdomain.com/api/v1/oauth/linkedin/callback
```

Don't forget to:
1. Update each OAuth provider app settings
2. Update `backend/.env` with production URIs
3. Restart backend after .env changes

---

## Next Steps

After updating the Meta app redirect URI:

1. ✅ Click "Save Changes" in Meta app
2. ✅ Wait 1-2 minutes for changes to propagate
3. ✅ Test OAuth flow again
4. ✅ Should redirect successfully!
5. ✅ Move on to testing Twitter and LinkedIn

---

**Estimated Time**: 2 minutes to update Meta app settings  
**Status**: Ready to test after you update the redirect URI in Meta app
