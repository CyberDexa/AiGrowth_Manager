# 🧪 Session 10 Testing Quick Reference

**Date**: October 13, 2025  
**Feature**: Twitter/X Publishing Integration  
**Status**: Ready for Testing

---

## 🚀 QUICK START

### 1. Prerequisites Setup (5 minutes)

**Twitter Developer Portal**:
1. Go to: https://developer.twitter.com/
2. Create a Project and App
3. Enable OAuth 2.0
4. Set Redirect URI: `http://localhost:8003/api/v1/social/twitter/callback`
5. Request Scopes: `tweet.read`, `tweet.write`, `users.read`, `offline.access`
6. Copy **Client ID** (no secret needed for PKCE!)

**Backend .env**:
```bash
cd backend
nano .env

# Add these lines:
TWITTER_CLIENT_ID=your_client_id_here
TWITTER_CLIENT_SECRET=your_optional_secret_here
TWITTER_REDIRECT_URI=http://localhost:8003/api/v1/social/twitter/callback
```

**Restart Backend**:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
```

---

## 🧪 TEST CHECKLIST

### ✅ Test 1: Verify Endpoints (30 seconds)

```bash
# Check Twitter endpoints are registered
curl -s http://localhost:8003/openapi.json | python3 -c "import sys, json; data=json.load(sys.stdin); paths=[p for p in data['paths'].keys() if 'twitter' in p.lower()]; print('\n'.join(sorted(paths)))"
```

**Expected Output**:
```
/api/v1/publishing/twitter
/api/v1/social/twitter/auth
/api/v1/social/twitter/callback
/api/v1/social/twitter/disconnect
```

---

### ✅ Test 2: Connect Twitter Account (2 minutes)

**Steps**:
1. Open: http://localhost:3000/dashboard/settings
2. Click **Social Accounts** tab
3. Find **Twitter / X** card
4. Click **"Connect Twitter"** button
5. Authorize on Twitter
6. Redirected back to Settings

**Expected Result**:
- ✅ Twitter Connected with @username
- Token expiry shown (~2 hours)

---

### ✅ Test 3: Post Single Tweet (1 minute)

**Steps**:
1. Go to: http://localhost:3000/dashboard/content
2. Find content < 280 chars
3. Click **"Publish"** → Select **Twitter**
4. Verify: `"245 / 280 characters"` (no warning)
5. Click **"Publish to Twitter"**

**Expected Result**:
- Success message
- Tweet on Twitter timeline
- Published posts page shows entry

**API Test**:
```bash
# Get your auth token from browser (Network tab)
TOKEN="your_clerk_token_here"

curl -X POST http://localhost:8003/api/v1/publishing/twitter \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": 1,
    "content_text": "Testing Twitter integration! 🚀 #AI #Automation"
  }'
```

---

### ✅ Test 4: Post Thread (2 minutes)

**Steps**:
1. Go to: http://localhost:3000/dashboard/content
2. Find content > 280 chars
3. Click **"Publish"** → Select **Twitter**
4. Verify: `"580 / 280 characters"` (red)
5. Verify: **"🐦 This will be posted as a 3-tweet thread"**
6. Click **"Publish to Twitter"**

**Expected Result**:
- Thread on Twitter (3 tweets)
- Tweet 1: `"... (1/3)"`
- Tweet 2: `"... (2/3)"`
- Tweet 3: `"... (3/3)"` with hashtags

---

### ✅ Test 5: Token Auto-Refresh (Optional)

**Simulate Expired Token**:
```sql
-- Connect to database
psql -U postgres -d ai_growth_manager

-- Set token expiry to past
UPDATE social_accounts 
SET token_expires_at = NOW() - INTERVAL '1 minute'
WHERE platform = 'twitter' AND id = 1;
```

**Test**:
1. Try to publish a tweet
2. Should work without error
3. Check backend logs: "Refreshing Twitter token"

**Verify**:
```sql
SELECT token_expires_at FROM social_accounts WHERE platform = 'twitter';
-- Should show ~2 hours from now
```

---

## 🐛 TROUBLESHOOTING

### Issue: "Twitter OAuth not yet implemented"

**Cause**: Backend not restarted after code changes  
**Fix**:
```bash
cd backend
pkill -f uvicorn
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
```

---

### Issue: "No connected Twitter account found"

**Cause**: Twitter OAuth flow not completed  
**Fix**:
1. Go to Settings → Social Accounts
2. Verify Twitter shows "Connected"
3. Check database:
```sql
SELECT * FROM social_accounts WHERE platform = 'twitter' AND is_active = true;
```

---

### Issue: "Invalid or expired state parameter"

**Cause**: PKCE state expired (10 min timeout) or backend restarted  
**Fix**: Start OAuth flow again from Settings page

---

### Issue: "Duplicate tweet"

**Cause**: Posted same content recently  
**Fix**: Wait 1 hour or modify content slightly

---

### Issue: "Rate limit exceeded"

**Cause**: Posted too many tweets (300 per 3 hours)  
**Fix**: Wait for rate limit reset (shown in error)

---

## 📊 DATABASE QUERIES

### Check Connected Accounts
```sql
SELECT id, platform, platform_username, is_active, token_expires_at 
FROM social_accounts 
WHERE platform = 'twitter';
```

### Check Published Tweets
```sql
SELECT id, platform, status, platform_post_url, published_at 
FROM published_posts 
WHERE platform = 'twitter' 
ORDER BY created_at DESC 
LIMIT 10;
```

### Check Thread Info
```sql
SELECT id, platform_post_id, platform_post_url, error_message 
FROM published_posts 
WHERE platform = 'twitter' 
AND error_message LIKE '%thread%';
```

---

## 🎯 SUCCESS INDICATORS

✅ **OAuth Working**:
- Twitter card shows "Connected"
- Username displayed
- Token expiry 2 hours from now

✅ **Publishing Working**:
- Tweets appear on timeline
- Published posts page shows entries
- Tweet URLs work

✅ **Thread Working**:
- Modal shows thread indicator
- Multiple tweets posted
- Tweets connected as replies
- Thread indicators: (1/N), (2/N), etc.

✅ **Token Refresh Working**:
- No manual reconnection needed after 2 hours
- Publishing continues working
- Token expiry updates automatically

---

## 🔗 USEFUL LINKS

- **Twitter Developer Portal**: https://developer.twitter.com/
- **Twitter API Docs**: https://developer.twitter.com/en/docs/twitter-api
- **PKCE Spec**: https://oauth.net/2/pkce/
- **Backend API Docs**: http://localhost:8003/docs
- **Frontend**: http://localhost:3000/dashboard

---

## 📝 NEXT STEPS

After testing Session 10:

1. **If Everything Works**: Proceed to Session 11 (Meta Integration or Analytics)
2. **If Issues Found**: Debug using troubleshooting section
3. **Production**: Follow checklist in SESSION_10_COMPLETE.md

---

**Quick Stats**:
- ⏱️ Setup Time: ~5 minutes
- 🧪 Testing Time: ~10 minutes
- 📊 Endpoints: 4
- 🐦 Features: OAuth + Single Tweets + Threads + Auto-Refresh

---

*Generated on October 13, 2025*  
*Quick Testing Reference for Session 10*
