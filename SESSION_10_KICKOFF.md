# 🐦 Session 10: Twitter/X Publishing Integration

**Date**: October 13, 2025  
**Previous Session**: Session 9 - Content Publishing (LinkedIn Complete)  
**Current Session Goal**: Add Twitter/X posting capability with OAuth 2.0 PKCE and API v2

---

## 🎯 OBJECTIVES

### Primary Goal
Enable users to publish AI-generated content to Twitter/X (now called X, but we'll use both names interchangeably) from the AI Growth Manager platform, supporting both single tweets and threads.

### Core Features to Build
1. ✅ **Twitter OAuth 2.0 with PKCE** - Secure authentication flow
2. ✅ **Twitter Publishing Service** - Post tweets via API v2
3. ✅ **Thread Support** - Post multi-tweet threads for longer content
4. ✅ **Twitter API Endpoints** - OAuth and publishing routes
5. ✅ **Frontend Integration** - Enable Twitter in UI
6. ✅ **Character Splitting** - Auto-split content > 280 chars into threads

### Success Metrics
- User can connect Twitter account with OAuth 2.0
- User can publish single tweets (≤280 chars)
- User can publish threads (>280 chars auto-split)
- Published tweets appear on Twitter timeline
- Tweet URLs are saved for reference

---

## 🏗️ ARCHITECTURE OVERVIEW

### Twitter API v2 vs LinkedIn UGC API

| Feature | LinkedIn | Twitter/X |
|---------|----------|-----------|
| **API Version** | UGC Posts v2 | API v2 |
| **OAuth Flow** | OAuth 2.0 (standard) | OAuth 2.0 with PKCE |
| **Character Limit** | 3,000 | 280 (premium: 4,000+) |
| **Refresh Tokens** | No | Yes! |
| **Thread Support** | No | Yes (reply chains) |
| **Scopes** | Fixed set | Granular permissions |

### System Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    USER JOURNEY                             │
│                                                              │
│  1. Connect Twitter account (OAuth 2.0 PKCE)                │
│  2. Generate content in Content section                     │
│  3. Click "Publish"                                         │
│  4. Select Twitter platform                                 │
│  5. Auto-detect: Single tweet or thread                     │
│  6. Preview with thread breakdown                           │
│  7. Click "Publish to Twitter"                              │
│  8. Content posts to Twitter                                │
│  9. Thread appears on Twitter timeline                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    TECHNICAL FLOW                           │
│                                                              │
│  Twitter OAuth Setup (PKCE)                                 │
│       ↓                                                      │
│  Generate code_verifier (random 128 chars)                  │
│       ↓                                                      │
│  Generate code_challenge (SHA256 hash)                      │
│       ↓                                                      │
│  Redirect to Twitter with challenge                         │
│       ↓                                                      │
│  User authorizes app                                        │
│       ↓                                                      │
│  Twitter redirects with authorization code                  │
│       ↓                                                      │
│  Exchange code + verifier for tokens                        │
│       ↓                                                      │
│  Store access_token + refresh_token (encrypted)             │
│                                                              │
│  ──────────────────────────────────────────                │
│                                                              │
│  Publishing Flow                                            │
│       ↓                                                      │
│  User clicks "Publish to Twitter"                           │
│       ↓                                                      │
│  Backend: Check content length                              │
│       ↓                                                      │
│  If ≤280 chars: Single tweet                                │
│  If >280 chars: Split into thread                           │
│       ↓                                                      │
│  POST to Twitter API v2 /tweets                             │
│       ↓                                                      │
│  For threads: POST each tweet as reply                      │
│       ↓                                                      │
│  Store tweet IDs and URLs                                   │
│       ↓                                                      │
│  Return success with first tweet URL                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 TWITTER OAUTH 2.0 WITH PKCE

### What is PKCE?

**PKCE** = Proof Key for Code Exchange

**Why Twitter Uses It**:
- More secure than standard OAuth 2.0
- Protects against authorization code interception
- Required for all Twitter API v2 OAuth flows

### PKCE Flow Steps

```python
# Step 1: Generate code_verifier (random string)
code_verifier = secrets.token_urlsafe(96)  # 128 characters
# Example: "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"

# Step 2: Generate code_challenge (SHA256 hash, base64-encoded)
import hashlib, base64
challenge = hashlib.sha256(code_verifier.encode()).digest()
code_challenge = base64.urlsafe_b64encode(challenge).decode().rstrip('=')
# Example: "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"

# Step 3: Store code_verifier in session/cache
redis.set(f"twitter_verifier:{state}", code_verifier, ex=600)

# Step 4: Redirect to Twitter with code_challenge
auth_url = (
    "https://twitter.com/i/oauth2/authorize?"
    f"response_type=code"
    f"&client_id={CLIENT_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&scope=tweet.read tweet.write users.read offline.access"
    f"&state={state}"
    f"&code_challenge={code_challenge}"
    f"&code_challenge_method=S256"
)

# Step 5: Twitter redirects back with code
# GET /callback?code=AUTHORIZATION_CODE&state=STATE

# Step 6: Exchange code for tokens WITH code_verifier
response = requests.post(
    "https://api.twitter.com/2/oauth2/token",
    data={
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier,  # ← Critical!
        "client_id": CLIENT_ID,
    },
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)

# Response includes REFRESH TOKEN!
{
    "access_token": "...",
    "refresh_token": "...",
    "expires_in": 7200,  # 2 hours
    "token_type": "bearer",
    "scope": "tweet.read tweet.write users.read offline.access"
}
```

### Twitter OAuth Scopes

| Scope | Permission | Needed For |
|-------|------------|------------|
| `tweet.read` | Read tweets | View user's tweets |
| `tweet.write` | Post tweets | **Required for publishing** |
| `users.read` | Read user info | Get username, profile |
| `offline.access` | Refresh tokens | **Long-term access** |

---

## 🐦 TWITTER API V2 INTEGRATION

### Tweet Posting Endpoint

**POST** `https://api.twitter.com/2/tweets`

**Headers**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Single Tweet Request**:
```json
{
  "text": "Hello Twitter! This is a test tweet from AI Growth Manager 🚀 #AI #SocialMedia"
}
```

**Response**:
```json
{
  "data": {
    "id": "1234567890123456789",
    "text": "Hello Twitter! This is a test tweet..."
  }
}
```

**Tweet URL**: `https://twitter.com/{username}/status/{tweet_id}`

### Thread Posting

**Thread** = Multiple tweets linked by replies

**Step 1: Post first tweet**
```json
POST /2/tweets
{
  "text": "Thread 1/3: This is the first tweet in our thread..."
}
Response: { "data": { "id": "111" } }
```

**Step 2: Post reply to first tweet**
```json
POST /2/tweets
{
  "text": "Thread 2/3: This is the second tweet...",
  "reply": {
    "in_reply_to_tweet_id": "111"
  }
}
Response: { "data": { "id": "222" } }
```

**Step 3: Post reply to second tweet**
```json
POST /2/tweets
{
  "text": "Thread 3/3: Final tweet in the thread!",
  "reply": {
    "in_reply_to_tweet_id": "222"
  }
}
Response: { "data": { "id": "333" } }
```

**Result**: Thread visible on Twitter: 111 → 222 → 333

### Character Limit Handling

**Standard Twitter Account**: 280 characters  
**Twitter Blue/Premium**: 4,000 - 25,000 characters

**Strategy for MVP**:
- Assume 280 character limit
- Auto-split content into threads
- Add thread indicators: "1/3", "2/3", "3/3"

**Smart Splitting Algorithm**:
```python
def split_into_tweets(content: str, max_chars: int = 280) -> list[str]:
    """
    Split content into tweet-sized chunks.
    - Split on sentence boundaries if possible
    - Add thread indicators
    - Preserve hashtags in last tweet
    """
    # Extract hashtags
    hashtags = extract_hashtags(content)
    content_without_hashtags = remove_hashtags(content)
    
    # Split into sentences
    sentences = split_sentences(content_without_hashtags)
    
    tweets = []
    current_tweet = ""
    
    for sentence in sentences:
        # Reserve space for " (X/Y)" indicator
        thread_indicator_space = 10
        
        if len(current_tweet) + len(sentence) + thread_indicator_space <= max_chars:
            current_tweet += sentence
        else:
            if current_tweet:
                tweets.append(current_tweet.strip())
            current_tweet = sentence
    
    if current_tweet:
        tweets.append(current_tweet.strip())
    
    # Add hashtags to last tweet
    if hashtags and tweets:
        last_tweet = tweets[-1]
        if len(last_tweet) + len(hashtags) + 3 <= max_chars:
            tweets[-1] = f"{last_tweet}\n\n{hashtags}"
    
    # Add thread indicators
    total = len(tweets)
    if total > 1:
        tweets = [f"{tweet} ({i+1}/{total})" for i, tweet in enumerate(tweets)]
    
    return tweets
```

---

## 📁 FILE STRUCTURE

### Backend Files to Create

```
backend/
├── app/
│   ├── services/
│   │   ├── oauth_twitter.py           ← NEW: Twitter OAuth 2.0 with PKCE
│   │   └── publishing_twitter.py      ← NEW: Twitter posting + threads
│   │
│   ├── api/
│   │   ├── social.py                  ← MODIFY: Add Twitter OAuth endpoints
│   │   └── publishing.py              ← MODIFY: Add Twitter publishing endpoint
│   │
│   └── core/
│       └── config.py                  ← MODIFY: Add Twitter credentials
```

### Frontend Files to Modify

```
frontend/
├── app/
│   ├── dashboard/
│   │   ├── strategies/components/
│   │   │   └── PublishContentModal.tsx    ← MODIFY: Enable Twitter
│   │   │
│   │   └── settings/components/
│   │       └── SocialConnections.tsx      ← MODIFY: Enable Twitter
```

---

## 🔨 IMPLEMENTATION PLAN

### Phase 1: Twitter OAuth Service (45 mins)

**Step 1.1: Add Twitter Config**
- Update `app/core/config.py` with Twitter credentials
- Add `TWITTER_CLIENT_ID`, `TWITTER_CLIENT_SECRET`
- Twitter redirect URI already exists from Session 8

**Step 1.2: Create OAuth Service**
- Create `app/services/oauth_twitter.py`
- Implement PKCE flow:
  - `generate_code_verifier()` - Random 128-char string
  - `generate_code_challenge()` - SHA256 hash
  - `get_authorization_url()` - Build OAuth URL with challenge
  - `exchange_code_for_token()` - Trade code + verifier for tokens
  - `refresh_access_token()` - Use refresh token for new access token
  - `get_user_profile()` - Fetch Twitter username

**Step 1.3: Add OAuth Endpoints**
- Update `app/api/social.py`
- Add `GET /social/twitter/auth` - Initiate OAuth
- Add `GET /social/twitter/callback` - Handle callback
- Add `POST /social/twitter/disconnect` - Disconnect account
- Store code_verifier in Redis/cache (or database for MVP)

### Phase 2: Twitter Publishing Service (45 mins)

**Step 2.1: Create Publishing Service**
- Create `app/services/publishing_twitter.py`
- Implement `post_to_twitter()` - Single tweet
- Implement `post_thread_to_twitter()` - Multi-tweet thread
- Implement `split_into_tweets()` - Smart content splitting
- Handle Twitter API errors (401, 429, 403)

**Step 2.2: Add Publishing Endpoint**
- Update `app/api/publishing.py`
- Add `POST /publishing/twitter` - Publish to Twitter
- Auto-detect single vs thread based on length
- Store all tweet IDs for threads

### Phase 3: Frontend Integration (30 mins)

**Step 3.1: Enable Twitter in Social Connections**
- Update `app/dashboard/settings/components/SocialConnections.tsx`
- Change `available: false` to `available: true` for Twitter
- Remove "Coming Soon" label

**Step 3.2: Enable Twitter in Publish Modal**
- Update `app/dashboard/strategies/components/PublishContentModal.tsx`
- Enable Twitter selection
- Show thread preview if content > 280 chars
- Update character counter for Twitter (280 vs 3000)

### Phase 4: Testing & Polish (30 mins)

**Step 4.1: Manual Testing**
- Connect Twitter account
- Post single tweet (< 280 chars)
- Post thread (> 280 chars)
- Verify on Twitter timeline
- Test disconnect/reconnect

**Step 4.2: Error Handling**
- Test expired token (should use refresh token)
- Test rate limiting
- Test disconnected account

**Step 4.3: Documentation**
- Create session summary
- Document Twitter OAuth setup
- Add testing guide

---

## 🧪 TESTING STRATEGY

### Unit Tests (Future)
```python
def test_split_into_tweets_short():
    content = "Short tweet"
    tweets = split_into_tweets(content)
    assert len(tweets) == 1
    assert tweets[0] == "Short tweet"

def test_split_into_tweets_long():
    content = "A" * 500  # 500 characters
    tweets = split_into_tweets(content, max_chars=280)
    assert len(tweets) == 2
    assert all(len(t) <= 280 for t in tweets)
    assert "(1/2)" in tweets[0]
    assert "(2/2)" in tweets[1]

def test_thread_posting():
    tweets = ["Tweet 1", "Tweet 2", "Tweet 3"]
    result = post_thread_to_twitter(account, tweets)
    assert len(result["tweet_ids"]) == 3
    assert result["thread_url"].endswith(result["tweet_ids"][0])
```

### Manual Testing Checklist

**Scenario 1: Connect Twitter Account**
- [ ] Click "Connect Twitter" in Settings
- [ ] Redirected to Twitter OAuth page
- [ ] Authorize app with correct scopes
- [ ] Redirected back to Settings
- [ ] See "✅ Twitter Connected" with username
- [ ] Verify access_token and refresh_token in database

**Scenario 2: Post Single Tweet**
- [ ] Generate content < 280 characters
- [ ] Click "Publish" → Select Twitter
- [ ] See character count: "245 / 280"
- [ ] Click "Publish to Twitter"
- [ ] See success message
- [ ] Verify tweet on Twitter timeline
- [ ] Verify tweet URL in database

**Scenario 3: Post Thread**
- [ ] Generate content > 280 characters (e.g., 600 chars)
- [ ] Click "Publish" → Select Twitter
- [ ] See preview showing thread breakdown
- [ ] See: "This will be posted as a 3-tweet thread"
- [ ] Click "Publish to Twitter"
- [ ] Verify thread on Twitter (3 connected tweets)
- [ ] Verify all tweet IDs saved

**Scenario 4: Token Refresh**
- [ ] Wait 2 hours (token expiry) or manually expire
- [ ] Try to publish content
- [ ] Backend auto-refreshes token
- [ ] Publishing succeeds without user action

---

## 💡 TWITTER API TIPS

### Character Counting

**Twitter counts characters differently**:
- URLs: Always count as 23 characters (regardless of actual length)
- Media: Don't count toward character limit
- Emojis: Count as 2 characters
- Newlines: Count as 1 character

**For MVP**: Use simple `len(text)` and assume no URLs

### Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /tweets | 300 tweets | 3 hours |
| POST /tweets (app) | 300 tweets | 3 hours |
| Token refresh | 50 requests | 15 min |

**Best Practice**: 
- Limit to 5-10 tweets per hour per user
- Show rate limit info in UI

### Common Errors

| Code | Error | Solution |
|------|-------|----------|
| 401 | Unauthorized | Refresh access token |
| 403 | Forbidden | Check scopes or account restrictions |
| 429 | Rate Limit | Show retry-after time |
| 400 | Duplicate | Tweet same content recently |

---

## 🚨 CHALLENGES & SOLUTIONS

### Challenge 1: PKCE State Management

**Problem**: code_verifier must be stored between OAuth redirect  
**Solution** (MVP): Store in database with state  
**Future**: Use Redis with TTL

```python
# Store before redirect
state = secrets.token_urlsafe(32)
code_verifier = secrets.token_urlsafe(96)

# Save to database
db.execute(
    "INSERT INTO oauth_state (state, code_verifier, business_id, created_at) "
    "VALUES (?, ?, ?, NOW())",
    (state, code_verifier, business_id)
)

# Retrieve in callback
verifier = db.execute(
    "SELECT code_verifier FROM oauth_state WHERE state = ?",
    (state,)
).fetchone()
```

### Challenge 2: Thread Continuity

**Problem**: If posting thread fails mid-way, partial thread remains  
**Solution**: 
- Save all tweet IDs as they're posted
- On error, save what was posted with status='partial'
- Allow user to delete partial threads
- Future: Implement rollback (delete posted tweets)

### Challenge 3: Character Limit Variations

**Problem**: Twitter Blue users have different limits  
**Solution** (MVP):
- Assume 280 characters for all users
- Future: Detect account type, adjust limit

### Challenge 4: Refresh Token Storage

**Problem**: Refresh tokens are sensitive, long-lived  
**Solution**:
- Encrypt refresh tokens (using existing encryption)
- Auto-refresh when access token expires
- Store expiry timestamp for proactive refresh

---

## 📈 SUCCESS CRITERIA

### Must Have (MVP)
- ✅ User can connect Twitter account via OAuth 2.0 PKCE
- ✅ User can post tweets ≤ 280 characters
- ✅ User can post threads (auto-split > 280 chars)
- ✅ Tweets appear on Twitter timeline
- ✅ Tweet URLs saved for reference
- ✅ Refresh tokens work (auto-refresh on expiry)
- ✅ Published posts page shows Twitter tweets

### Nice to Have (Future)
- ⏳ Media upload (images, videos, GIFs)
- ⏳ Twitter Blue character limit detection
- ⏳ Tweet editing (within 30 min window)
- ⏳ Quote tweets and retweets
- ⏳ Poll creation
- ⏳ Twitter Spaces announcements
- ⏳ Engagement metrics (likes, retweets, replies)

---

## 🔗 API ENDPOINTS SUMMARY

### OAuth Endpoints

**GET /api/v1/social/twitter/auth**
- Initiate OAuth flow with PKCE
- Query params: `business_id`
- Response: Redirect to Twitter

**GET /api/v1/social/twitter/callback**
- Handle OAuth callback
- Query params: `code`, `state`
- Response: Redirect to Settings with success/error

**POST /api/v1/social/twitter/disconnect**
- Disconnect Twitter account
- Body: `{ "business_id": 1 }`
- Response: `{ "message": "Disconnected" }`

### Publishing Endpoints

**POST /api/v1/publishing/twitter**
- Publish to Twitter (single or thread)
- Body: Same as LinkedIn
  ```json
  {
    "business_id": 1,
    "content_text": "Tweet content here...",
    "scheduled_for": null
  }
  ```
- Response:
  ```json
  {
    "id": 123,
    "platform": "twitter",
    "status": "published",
    "platform_post_id": "1234567890",  // First tweet ID
    "platform_post_url": "https://twitter.com/user/status/1234567890",
    "thread_tweet_ids": ["111", "222", "333"],  // All tweet IDs
    "published_at": "2025-10-13T04:00:00Z"
  }
  ```

---

## 📚 RESOURCES

### Twitter API Documentation
- **OAuth 2.0 PKCE**: https://developer.twitter.com/en/docs/authentication/oauth-2-0/authorization-code
- **API v2 Tweets**: https://developer.twitter.com/en/docs/twitter-api/tweets/manage-tweets/api-reference/post-tweets
- **Rate Limits**: https://developer.twitter.com/en/docs/twitter-api/rate-limits
- **Error Codes**: https://developer.twitter.com/en/support/twitter-api/error-troubleshooting

### Libraries
- **httpx**: Already installed (async HTTP client)
- **hashlib**: Built-in (for PKCE SHA256)
- **secrets**: Built-in (for code_verifier generation)

---

## 🎯 SESSION GOALS RECAP

By end of Session 10, we should have:

1. ✅ **Twitter OAuth 2.0 PKCE flow** working end-to-end
2. ✅ **Twitter publishing service** posting single tweets
3. ✅ **Thread support** for content > 280 characters
4. ✅ **Auto token refresh** using refresh tokens
5. ✅ **Frontend integration** with Twitter enabled
6. ✅ **Published posts tracking** for Twitter
7. ✅ **Session documentation** with Twitter setup guide

---

## 🚀 GETTING STARTED

### Prerequisites
- ✅ Session 9 complete (Publishing infrastructure ready)
- ✅ Backend and frontend servers running
- ✅ Database has published_posts table

### Twitter Developer Account Setup

**Required Before Coding**:
1. Go to https://developer.twitter.com/
2. Create Developer Account (if not done)
3. Create a new Project + App
4. Enable OAuth 2.0 in app settings
5. Set redirect URI: `http://localhost:8003/api/v1/social/twitter/callback`
6. Request scopes: `tweet.read`, `tweet.write`, `users.read`, `offline.access`
7. Get Client ID (no client secret needed for PKCE!)

### Environment Variables

```bash
# Add to backend/.env
TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_REDIRECT_URI=http://localhost:8003/api/v1/social/twitter/callback
```

**Note**: Twitter OAuth 2.0 PKCE doesn't use client secret!

---

## 🎨 UI MOCKUPS

### Thread Preview in Publish Modal

```
┌──────────────────────────────────────────────────────┐
│  Publish Content                               [X]   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Platform Selection                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ LinkedIn │  │ Twitter ✓│  │   Meta   │          │
│  │          │  │    ✓     │  │          │          │
│  └──────────┘  └──────────┘  └──────────┘          │
│                                                      │
│  Content Preview                                     │
│  ⚠️ This content will be posted as a 3-tweet thread │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │ Tweet 1/3:                                     │ │
│  │ Your AI-generated content goes here! This is   │ │
│  │ the first part of your thread... (1/3)        │ │
│  │                                                 │ │
│  │ 265 / 280 characters                           │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │ Tweet 2/3:                                     │ │
│  │ Continuing from the previous tweet, here's     │ │
│  │ more valuable insights... (2/3)                │ │
│  │                                                 │ │
│  │ 248 / 280 characters                           │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │ Tweet 3/3:                                     │ │
│  │ Final thoughts in this thread. #AI #Growth    │ │
│  │ #Marketing (3/3)                               │ │
│  │                                                 │ │
│  │ 189 / 280 characters                           │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│           [Cancel]  [Publish Thread to Twitter]     │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

**Ready to build? Let's start Session 10! 🐦**
