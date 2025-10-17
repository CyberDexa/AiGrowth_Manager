# 🚀 Session 8: Social Media Integration

**Date**: October 12, 2025  
**Session Goal**: Enable users to connect their social media accounts (LinkedIn, Twitter/X, Meta/Facebook/Instagram)  
**Estimated Duration**: 3-4 hours  
**Status**: 🟢 IN PROGRESS

---

## 📋 SESSION OVERVIEW

### What We're Building

A complete **Social Media Account Connection System** that allows users to:
1. Connect LinkedIn, Twitter/X, and Meta (Facebook/Instagram) accounts
2. View connection status and account information
3. Disconnect and reconnect accounts
4. Store OAuth tokens securely for automated posting

This is a **critical MVP feature** - without it, users can't publish content to their social platforms.

---

## 🎯 SESSION OBJECTIVES

### Primary Goals
1. ✅ **OAuth Integration** - Implement OAuth 2.0 flows for all 3 platforms
2. ✅ **UI Component** - Build social account connection interface in Settings
3. ✅ **Token Management** - Securely store and manage access tokens
4. ✅ **Error Handling** - Handle connection failures, expired tokens, rate limits

### Success Criteria
- [ ] User can click "Connect LinkedIn" and complete OAuth flow
- [ ] User can click "Connect Twitter" and complete OAuth flow  
- [ ] User can click "Connect Facebook/Instagram" and complete OAuth flow
- [ ] Connected accounts show status: ✅ Connected or ❌ Not Connected
- [ ] User can disconnect accounts
- [ ] Tokens are encrypted and stored in database
- [ ] Error messages are clear and helpful

---

## 🏗️ ARCHITECTURE OVERVIEW

### System Flow
```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                          │
│  Settings Page → Click "Connect LinkedIn" Button            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 FRONTEND (Next.js)                          │
│  1. Redirect to: /api/v1/social/linkedin/auth              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 BACKEND (FastAPI)                           │
│  2. Generate OAuth URL with state token                     │
│  3. Redirect user to LinkedIn OAuth page                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              LINKEDIN OAUTH (External)                      │
│  4. User logs in to LinkedIn                                │
│  5. User authorizes app permissions                         │
│  6. LinkedIn redirects to callback URL with code            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│          BACKEND CALLBACK HANDLER                           │
│  7. Receive authorization code                              │
│  8. Exchange code for access token                          │
│  9. Fetch user profile info                                 │
│  10. Encrypt and store token in database                    │
│  11. Redirect user back to Settings page                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              SETTINGS PAGE (Success)                        │
│  12. Show "✅ LinkedIn Connected"                           │
│  13. Display account info (name, profile picture)           │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

**`social_accounts` Table** (Already exists from migrations):
```sql
CREATE TABLE social_accounts (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES businesses(id),
    platform VARCHAR NOT NULL,  -- 'linkedin', 'twitter', 'facebook', 'instagram'
    account_id VARCHAR NOT NULL,  -- Platform's user ID
    account_name VARCHAR,
    access_token TEXT NOT NULL,  -- Encrypted OAuth token
    refresh_token TEXT,  -- For refreshing expired tokens
    token_expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔐 OAUTH SETUP REQUIREMENTS

### 1. LinkedIn OAuth
**Developer Portal**: https://www.linkedin.com/developers/  
**Permissions Needed**:
- `openid` - Basic profile access
- `profile` - Full profile info
- `w_member_social` - Post to LinkedIn
- `r_basicprofile` - Read basic profile (deprecated, use profile)

**Redirect URI**: `http://localhost:8003/api/v1/social/linkedin/callback`

**Environment Variables**:
```bash
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_REDIRECT_URI=http://localhost:8003/api/v1/social/linkedin/callback
```

### 2. Twitter/X OAuth 2.0
**Developer Portal**: https://developer.twitter.com/  
**Permissions Needed**:
- `tweet.read` - Read tweets
- `tweet.write` - Post tweets
- `users.read` - Read user info
- `offline.access` - Refresh tokens

**Redirect URI**: `http://localhost:8003/api/v1/social/twitter/callback`

**Environment Variables**:
```bash
TWITTER_CLIENT_ID=your_client_id
TWITTER_CLIENT_SECRET=your_client_secret
TWITTER_REDIRECT_URI=http://localhost:8003/api/v1/social/twitter/callback
```

### 3. Meta (Facebook/Instagram) OAuth
**Developer Portal**: https://developers.facebook.com/  
**Permissions Needed**:
- `pages_manage_posts` - Post to Facebook Pages
- `instagram_basic` - Basic Instagram access
- `instagram_content_publish` - Publish to Instagram
- `business_management` - Manage business accounts

**Redirect URI**: `http://localhost:8003/api/v1/social/meta/callback`

**Environment Variables**:
```bash
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
META_REDIRECT_URI=http://localhost:8003/api/v1/social/meta/callback
```

---

## 📁 FILE STRUCTURE

### Backend Files to Create/Modify
```
backend/
├── app/
│   ├── api/
│   │   └── social.py                    # NEW - OAuth endpoints
│   ├── models/
│   │   └── social_account.py            # EXISTS - Review/update
│   ├── schemas/
│   │   └── social.py                    # NEW - Pydantic schemas
│   ├── services/
│   │   ├── oauth_linkedin.py            # NEW - LinkedIn OAuth
│   │   ├── oauth_twitter.py             # NEW - Twitter OAuth
│   │   └── oauth_meta.py                # NEW - Meta OAuth
│   └── core/
│       └── encryption.py                # NEW - Token encryption
└── .env                                 # UPDATE - Add OAuth credentials
```

### Frontend Files to Create/Modify
```
frontend/
└── app/
    └── dashboard/
        └── settings/
            ├── page.tsx                  # UPDATE - Add social section
            └── components/
                └── SocialConnections.tsx # NEW - Social UI component
```

---

## 🎨 UI DESIGN

### Settings Page - Social Accounts Tab

```
┌─────────────────────────────────────────────────────────────┐
│  Settings                                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Business Profile] [Notifications] [Preferences]           │
│  [➤ Social Accounts] [Security]                             │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Connected Social Accounts                             │ │
│  │                                                         │ │
│  │  Link your social media accounts to enable automated   │ │
│  │  content publishing and analytics tracking.            │ │
│  │                                                         │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │ 🟦 LinkedIn                                      │  │ │
│  │  │                                                   │  │ │
│  │  │ ✅ Connected as John Doe                         │  │ │
│  │  │ Connected on: Oct 12, 2025                       │  │ │
│  │  │                                                   │  │ │
│  │  │ [Disconnect]                                     │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │                                                         │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │ 🐦 Twitter / X                                   │  │ │
│  │  │                                                   │  │ │
│  │  │ ❌ Not Connected                                 │  │ │
│  │  │                                                   │  │ │
│  │  │ [Connect Twitter]                                │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │                                                         │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │ 📘 Facebook / Instagram                          │  │ │
│  │  │                                                   │  │ │
│  │  │ ❌ Not Connected                                 │  │ │
│  │  │                                                   │  │ │
│  │  │ [Connect Facebook]                               │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │                                                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔨 IMPLEMENTATION PLAN

### Step 1: Backend - OAuth Service Setup (45 mins)
**Task**: Create OAuth service classes for each platform

**Files to Create**:
1. `backend/app/services/oauth_linkedin.py`
2. `backend/app/services/oauth_twitter.py`
3. `backend/app/services/oauth_meta.py`

**Each service should have**:
- `get_authorization_url()` - Generate OAuth URL
- `exchange_code_for_token()` - Exchange auth code for token
- `get_user_profile()` - Fetch user info
- `refresh_token()` - Refresh expired tokens

### Step 2: Backend - API Endpoints (30 mins)
**Task**: Create FastAPI endpoints for OAuth flows

**File**: `backend/app/api/social.py`

**Endpoints**:
```python
GET  /api/v1/social/linkedin/auth     → Redirect to LinkedIn
GET  /api/v1/social/linkedin/callback → Handle LinkedIn callback
POST /api/v1/social/linkedin/disconnect → Disconnect LinkedIn

GET  /api/v1/social/twitter/auth      → Redirect to Twitter
GET  /api/v1/social/twitter/callback  → Handle Twitter callback
POST /api/v1/social/twitter/disconnect → Disconnect Twitter

GET  /api/v1/social/meta/auth         → Redirect to Meta
GET  /api/v1/social/meta/callback     → Handle Meta callback
POST /api/v1/social/meta/disconnect   → Disconnect Meta

GET  /api/v1/social/accounts          → List connected accounts
```

### Step 3: Backend - Token Encryption (20 mins)
**Task**: Implement secure token storage

**File**: `backend/app/core/encryption.py`

**Functions**:
- `encrypt_token(token: str) -> str`
- `decrypt_token(encrypted: str) -> str`

Uses: `cryptography` library with Fernet symmetric encryption

### Step 4: Backend - Schemas & Models (20 mins)
**Task**: Create Pydantic schemas for social accounts

**File**: `backend/app/schemas/social.py`

**Schemas**:
- `SocialAccountBase` - Base fields
- `SocialAccountCreate` - For creation
- `SocialAccountResponse` - For API responses
- `SocialAccountList` - List of accounts

### Step 5: Frontend - Social Connections Component (45 mins)
**Task**: Build interactive UI for connecting accounts

**File**: `frontend/app/dashboard/settings/components/SocialConnections.tsx`

**Features**:
- Display connection status for each platform
- Connect/Disconnect buttons
- Loading states during OAuth
- Error messages
- Account info display (name, profile pic)

### Step 6: Frontend - Settings Page Integration (15 mins)
**Task**: Add Social Accounts tab to Settings page

**File**: `frontend/app/dashboard/settings/page.tsx`

**Changes**:
- Add "Social Accounts" tab
- Import and render `SocialConnections` component
- Handle tab switching

### Step 7: Testing (30 mins)
**Task**: Test OAuth flows end-to-end

**Test Cases**:
1. Connect LinkedIn → Should redirect → Should callback → Should show connected
2. Connect Twitter → Same flow
3. Connect Meta → Same flow
4. Disconnect account → Should remove from database
5. Reconnect account → Should update token
6. Handle errors (user denies, network failure, expired token)

### Step 8: Documentation (15 mins)
**Task**: Document setup and usage

**Create**: `SESSION_8_SOCIAL_INTEGRATION.md`

---

## 🧪 TESTING STRATEGY

### Local Testing (Development)

**Redirect URIs** (for local testing):
```
http://localhost:8003/api/v1/social/linkedin/callback
http://localhost:8003/api/v1/social/twitter/callback
http://localhost:8003/api/v1/social/meta/callback
```

**Test Accounts**:
- Create test accounts on each platform
- Use sandbox/developer mode where available
- Document test credentials in `.env.local`

### Manual Testing Checklist

**LinkedIn**:
- [ ] Click "Connect LinkedIn"
- [ ] Redirects to LinkedIn login
- [ ] Login with test account
- [ ] Authorize permissions
- [ ] Redirects back to Settings
- [ ] Shows "✅ LinkedIn Connected"
- [ ] Click "Disconnect"
- [ ] Shows "❌ Not Connected"

**Twitter**:
- [ ] Same flow as LinkedIn
- [ ] Verify scopes: `tweet.write`, `users.read`, `offline.access`

**Meta**:
- [ ] Same flow as LinkedIn
- [ ] Verify both Facebook and Instagram access
- [ ] Check page/account selection

---

## 🚨 POTENTIAL CHALLENGES

### Challenge 1: OAuth Callback Handling
**Issue**: Callback must handle both success and error cases  
**Solution**: Parse query params for `code` (success) or `error` (failure)

### Challenge 2: Token Expiration
**Issue**: Access tokens expire (LinkedIn: 60 days, Twitter: refreshable, Meta: 60 days)  
**Solution**: Store `expires_at` timestamp, implement token refresh logic

### Challenge 3: CORS in OAuth Flow
**Issue**: OAuth callbacks might have CORS issues  
**Solution**: Backend handles redirects, not frontend fetch calls

### Challenge 4: Multiple Accounts
**Issue**: User might connect multiple accounts per platform  
**Solution**: For MVP, limit to 1 account per platform. Post-MVP: support multiple

### Challenge 5: Testing Without Real Credentials
**Issue**: Can't test without actual OAuth apps  
**Solution**: Mock OAuth responses in development, use real apps for testing

---

## 📊 SUCCESS METRICS

### Technical Metrics
- [ ] All 3 OAuth flows complete successfully
- [ ] Tokens encrypted in database (verify with database query)
- [ ] Zero errors in OAuth callback handling
- [ ] Response time < 3 seconds for OAuth flow

### User Experience Metrics
- [ ] User can connect account in < 30 seconds
- [ ] Clear visual feedback at each step
- [ ] Error messages are actionable
- [ ] No page reloads (smooth redirects)

---

## 🔄 IMPLEMENTATION ORDER

### Phase 1: LinkedIn (Simplest OAuth)
1. ✅ LinkedIn service
2. ✅ LinkedIn endpoints
3. ✅ Test LinkedIn flow
4. ✅ Frontend LinkedIn UI

**Why first?** LinkedIn has the most straightforward OAuth 2.0 flow

### Phase 2: Twitter/X
1. ✅ Twitter service (OAuth 2.0 with PKCE)
2. ✅ Twitter endpoints
3. ✅ Test Twitter flow
4. ✅ Frontend Twitter UI

**Why second?** Twitter recently moved to OAuth 2.0 (similar to LinkedIn)

### Phase 3: Meta (Most Complex)
1. ✅ Meta service
2. ✅ Meta endpoints (handles both Facebook & Instagram)
3. ✅ Test Meta flow
4. ✅ Frontend Meta UI

**Why last?** Meta requires page selection, business verification, more complex setup

---

## 📚 RESOURCES & DOCUMENTATION

### OAuth Documentation
- **LinkedIn**: https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication
- **Twitter**: https://developer.twitter.com/en/docs/authentication/oauth-2-0
- **Meta**: https://developers.facebook.com/docs/facebook-login/

### Python Libraries
- `httpx` - For making OAuth API requests
- `cryptography` - For token encryption
- `python-jose` - For JWT handling (if needed)

### Environment Variables Template
```bash
# LinkedIn OAuth
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
LINKEDIN_REDIRECT_URI=http://localhost:8003/api/v1/social/linkedin/callback

# Twitter OAuth
TWITTER_CLIENT_ID=
TWITTER_CLIENT_SECRET=
TWITTER_REDIRECT_URI=http://localhost:8003/api/v1/social/twitter/callback

# Meta OAuth
META_APP_ID=
META_APP_SECRET=
META_REDIRECT_URI=http://localhost:8003/api/v1/social/meta/callback

# Encryption key (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ENCRYPTION_KEY=
```

---

## 🎯 SESSION DELIVERABLES

### Code Deliverables
1. ✅ 3 OAuth service classes (LinkedIn, Twitter, Meta)
2. ✅ Social API endpoints (auth, callback, disconnect)
3. ✅ Token encryption utility
4. ✅ Social account schemas
5. ✅ SocialConnections React component
6. ✅ Updated Settings page with Social tab

### Documentation Deliverables
1. ✅ OAuth setup guide
2. ✅ Environment variables documentation
3. ✅ Testing procedures
4. ✅ Session summary with screenshots

### Testing Deliverables
1. ✅ Tested OAuth flow for each platform
2. ✅ Error handling tested
3. ✅ Token storage verified
4. ✅ UI states tested (loading, success, error)

---

## 🚀 NEXT STEPS (Post-Session 8)

### Session 9: Content Publishing
1. Use connected accounts to actually POST content
2. Implement platform-specific formatting
3. Handle posting errors and retries
4. Track published content status

### Session 10: Analytics Integration
1. Fetch engagement metrics (likes, shares, comments)
2. Display analytics in dashboard
3. Track content performance
4. Generate insights

---

## 💡 TIPS & BEST PRACTICES

### Security
- ✅ Never log access tokens
- ✅ Always encrypt tokens at rest
- ✅ Use HTTPS in production
- ✅ Validate OAuth state parameter to prevent CSRF

### User Experience
- ✅ Show loading spinners during OAuth
- ✅ Provide clear error messages
- ✅ Allow easy reconnection if token expires
- ✅ Display account info to confirm correct account

### Development
- ✅ Test with real OAuth apps (not mocks)
- ✅ Handle edge cases (user denies, network errors)
- ✅ Log OAuth errors for debugging
- ✅ Use environment variables for all credentials

---

**Session Started**: October 12, 2025  
**Estimated Completion**: October 12, 2025 (3-4 hours)  
**Current Status**: 🟢 Ready to begin implementation

**Let's build! 🚀**
