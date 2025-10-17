# OAuth Setup Guide

Quick reference for setting up OAuth 2.0 for LinkedIn, Twitter, and Meta.

## 🚀 Quick Start

### 1. Set Environment Variables

Add these to your `.env` file:

```bash
# LinkedIn OAuth
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_REDIRECT_URI=http://localhost:8000/api/v1/oauth/linkedin/callback

# Twitter OAuth 2.0
TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret
TWITTER_REDIRECT_URI=http://localhost:8000/api/v1/oauth/twitter/callback

# Meta (Facebook/Instagram) OAuth
META_APP_ID=your_meta_app_id
META_APP_SECRET=your_meta_app_secret
META_REDIRECT_URI=http://localhost:8000/api/v1/oauth/meta/callback
```

### 2. Test OAuth Flow

```bash
# Start the backend server
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Visit API docs
open http://localhost:8000/docs

# Test the OAuth endpoints:
# 1. GET /api/v1/oauth/platforms - List available platforms
# 2. GET /api/v1/oauth/{platform}/authorize?business_id=1 - Start OAuth flow
# 3. GET /api/v1/oauth/status?business_id=1 - Check connection status
```

---

## 📱 Platform-Specific Setup

### LinkedIn

**1. Create LinkedIn App**
- Go to: https://www.linkedin.com/developers/apps
- Click "Create app"
- Fill in app details:
  - App name: "AI Growth Manager"
  - LinkedIn Page: Select your company page
  - App logo: Upload logo (optional)

**2. Configure Products**
- Go to "Products" tab
- Request access to:
  - ✅ Sign In with LinkedIn using OpenID Connect
  - ✅ Share on LinkedIn
  - ✅ Advertising API (for organization posting)

**3. Configure OAuth Settings**
- Go to "Auth" tab
- Add Redirect URL: `http://localhost:8000/api/v1/oauth/linkedin/callback`
- For production: `https://yourdomain.com/api/v1/oauth/linkedin/callback`

**4. Get Credentials**
- Client ID: Copy from "Auth" tab
- Client Secret: Copy from "Auth" tab

**5. Required Scopes**
```
openid
profile
email
w_member_social
r_organization_social
w_organization_social
```

**Token Information**:
- Access token expires in: **60 days**
- Refresh token: ❌ Not supported (requires re-authentication)
- Organization posting: ✅ Supported with `r_organization_social` and `w_organization_social`

---

### Twitter

**1. Create Twitter App**
- Go to: https://developer.twitter.com/en/portal/projects-and-apps
- Click "Create Project"
- Fill in project details:
  - Project name: "AI Growth Manager"
  - Use case: Select appropriate use case
  - Project description: Describe your app

**2. Create App**
- App name: "AI Growth Manager"
- App environment: Development or Production

**3. Enable OAuth 2.0**
- Go to app settings
- Under "User authentication settings", click "Set up"
- Select:
  - ✅ OAuth 2.0
  - App permissions: Read and write
  - Type of App: Web App, Automated App or Bot

**4. Configure OAuth 2.0**
- Callback URL: `http://localhost:8000/api/v1/oauth/twitter/callback`
- Website URL: `http://localhost:8000`
- For production use HTTPS!

**5. Get Credentials**
- Client ID: Copy from "Keys and tokens" tab
- Client Secret: Copy from "Keys and tokens" tab

**6. Required Scopes**
```
tweet.read
tweet.write
users.read
offline.access
```

**Token Information**:
- Access token expires in: **2 hours**
- Refresh token: ✅ Supported (long-lived)
- **Important**: New refresh token issued on each refresh
- PKCE: ✅ Required (automatically handled)

---

### Meta (Facebook/Instagram)

**1. Create Meta App**
- Go to: https://developers.facebook.com/apps
- Click "Create App"
- Select app type: **Business**
- Fill in app details:
  - App name: "AI Growth Manager"
  - App contact email: your_email@example.com

**2. Add Products**
- Add **Facebook Login** product
- Add **Instagram** product

**3. Configure Facebook Login**
- Go to Facebook Login → Settings
- Add OAuth Redirect URIs:
  - `http://localhost:8000/api/v1/oauth/meta/callback`
  - For production: `https://yourdomain.com/api/v1/oauth/meta/callback`

**4. Configure App Settings**
- Go to Settings → Basic
- Add App Domains: `localhost` (for development)
- For production: Add your domain

**5. Get Credentials**
- App ID: Copy from Settings → Basic
- App Secret: Click "Show" to reveal, then copy

**6. Required Permissions**
Add these permissions in App Review → Permissions and Features:
```
pages_show_list
pages_read_engagement
pages_manage_posts
instagram_basic
instagram_content_publish
```

**7. Test Users** (Development Mode)
- Go to Roles → Test Users
- Add test users for development
- Test users can use the app in Development mode

**8. Go Live** (Production)
- Complete Business Verification
- Submit permissions for App Review
- Switch app to Live mode

**Token Information**:
- Short-lived token: **1 hour**
- Long-lived token: **60 days** (exchange short-lived → long-lived)
- Page Access Token: **Never expires** ✨
- Instagram: Requires Facebook Page with linked Instagram Business account

---

## 🔄 OAuth Flow Examples

### LinkedIn OAuth Flow

```python
# 1. Initiate OAuth
GET /api/v1/oauth/linkedin/authorize?business_id=1

Response:
{
  "authorization_url": "https://www.linkedin.com/oauth/v2/authorization?...",
  "state": "abc123...",
  "platform": "linkedin",
  "business_id": 1
}

# 2. User authorizes on LinkedIn
# LinkedIn redirects to: /api/v1/oauth/linkedin/callback?code=...&state=abc123

# 3. Backend exchanges code for token
GET /api/v1/oauth/linkedin/callback?code=xyz&state=abc123&business_id=1

Response:
{
  "success": true,
  "platform": "linkedin",
  "business_id": 1,
  "profile": {
    "name": "John Doe",
    "id": "abc123",
    "email": "john@example.com"
  },
  "expires_at": "2024-03-15T12:00:00Z"
}

# 4. Check connection status
GET /api/v1/oauth/status?business_id=1

Response:
{
  "business_id": 1,
  "platforms": {
    "linkedin": {
      "connected": true,
      "status": "active",
      "expires_at": "2024-03-15T12:00:00Z",
      "profile": {
        "username": "John Doe",
        "id": "abc123"
      }
    }
  }
}
```

### Twitter OAuth Flow (with PKCE)

```python
# 1. Initiate OAuth
GET /api/v1/oauth/twitter/authorize?business_id=1

Response:
{
  "authorization_url": "https://twitter.com/i/oauth2/authorize?...",
  "state": "abc123...",
  "code_verifier": "xyz789...",  # Store this!
  "platform": "twitter",
  "business_id": 1
}

# 2. User authorizes on Twitter
# Twitter redirects to: /api/v1/oauth/twitter/callback?code=...&state=abc123

# 3. Backend exchanges code for token (requires code_verifier!)
GET /api/v1/oauth/twitter/callback?code=xyz&state=abc123&business_id=1&code_verifier=xyz789

Response:
{
  "success": true,
  "platform": "twitter",
  "business_id": 1,
  "profile": {
    "name": "John Doe",
    "id": "12345",
    "email": "john@example.com"
  },
  "expires_at": "2024-01-15T14:00:00Z"  # 2 hours from now
}

# 4. Refresh token (when expired)
POST /api/v1/oauth/twitter/refresh?business_id=1

Response:
{
  "success": true,
  "platform": "twitter",
  "expires_at": "2024-01-15T16:00:00Z"  # New expiration
}
```

### Meta OAuth Flow (3-Token Flow)

```python
# 1. Initiate OAuth
GET /api/v1/oauth/meta/authorize?business_id=1

Response:
{
  "authorization_url": "https://www.facebook.com/v18.0/dialog/oauth?...",
  "state": "abc123...",
  "platform": "meta",
  "business_id": 1
}

# 2. User authorizes on Facebook
# Facebook redirects to: /api/v1/oauth/meta/callback?code=...&state=abc123

# 3. Backend handles 3-token flow automatically:
#    - Exchange code for short-lived token (1 hour)
#    - Exchange short-lived for long-lived token (60 days)
#    - Store long-lived token
GET /api/v1/oauth/meta/callback?code=xyz&state=abc123&business_id=1

Response:
{
  "success": true,
  "platform": "meta",
  "business_id": 1,
  "profile": {
    "name": "John Doe",
    "id": "123456789",
    "email": "john@example.com"
  },
  "expires_at": "2024-03-15T12:00:00Z"  # Long-lived token expiration
}

# Additional steps for Instagram posting (manual or separate endpoint):
# 4. Get user's Facebook Pages
# 5. User selects a Page
# 6. Get Page Access Token (never expires)
# 7. Check for linked Instagram Business account
# 8. Store Page token and Instagram account ID
```

---

## 🔐 Security Best Practices

### State Parameter Validation

**Current Implementation**: ⚠️ State is generated but not validated

**TODO**: Implement state storage and validation
```python
# Store state in Redis with 10-minute expiration
redis.setex(f"oauth:state:{state}", 600, json.dumps({
    "business_id": business_id,
    "platform": platform,
    "timestamp": datetime.utcnow().isoformat()
}))

# Validate on callback
stored_data = redis.get(f"oauth:state:{state}")
if not stored_data:
    raise HTTPException(status_code=400, detail="Invalid or expired state")
```

### Token Encryption

**Current Implementation**: ⚠️ Tokens stored in plaintext

**TODO**: Encrypt tokens before storing
```python
from cryptography.fernet import Fernet

# Initialize encryption
cipher_suite = Fernet(settings.ENCRYPTION_KEY)

# Encrypt token before storing
encrypted_token = cipher_suite.encrypt(access_token.encode()).decode()
social_account.access_token = encrypted_token

# Decrypt when needed
decrypted_token = cipher_suite.decrypt(encrypted_token.encode()).decode()
```

### HTTPS Enforcement

**Production**: Always use HTTPS for OAuth callbacks
```python
# Update redirect URIs in production
LINKEDIN_REDIRECT_URI=https://yourdomain.com/api/v1/oauth/linkedin/callback
TWITTER_REDIRECT_URI=https://yourdomain.com/api/v1/oauth/twitter/callback
META_REDIRECT_URI=https://yourdomain.com/api/v1/oauth/meta/callback
```

### Rate Limiting

**TODO**: Add rate limiting to OAuth endpoints
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.get("/{platform}/authorize")
@limiter.limit("10/minute")
async def initiate_oauth(...):
    ...
```

---

## 🧪 Testing OAuth Flows

### Manual Testing Checklist

- [ ] **LinkedIn**
  - [ ] Authorization flow completes
  - [ ] Profile data retrieved correctly
  - [ ] Token expiration set to 60 days
  - [ ] Organization access works (if applicable)
  - [ ] Token revocation works

- [ ] **Twitter**
  - [ ] Authorization flow with PKCE completes
  - [ ] Profile data retrieved correctly
  - [ ] Token expiration set to 2 hours
  - [ ] Token refresh works
  - [ ] New refresh token stored
  - [ ] Token revocation works

- [ ] **Meta**
  - [ ] Authorization flow completes
  - [ ] Short-lived token exchanged for long-lived
  - [ ] Profile data retrieved correctly
  - [ ] Facebook Pages listed
  - [ ] Page Access Token obtained
  - [ ] Instagram account linked (if applicable)
  - [ ] Token revocation works

- [ ] **API Endpoints**
  - [ ] `/platforms` lists all platforms with correct status
  - [ ] `/{platform}/authorize` generates valid URLs
  - [ ] `/{platform}/callback` handles success and errors
  - [ ] `/{platform}/refresh` works for Twitter
  - [ ] `/{platform}/disconnect` removes connection
  - [ ] `/status` shows accurate connection state

### Test with cURL

```bash
# List platforms
curl http://localhost:8000/api/v1/oauth/platforms

# Start LinkedIn OAuth
curl "http://localhost:8000/api/v1/oauth/linkedin/authorize?business_id=1"

# Check status
curl "http://localhost:8000/api/v1/oauth/status?business_id=1"
```

---

## 🐛 Troubleshooting

### Common Issues

**1. "Invalid redirect_uri"**
- Ensure redirect URI in code matches exactly what's configured in platform dashboard
- Check for trailing slashes
- For development, use `http://localhost:8000` (not `127.0.0.1`)

**2. "Insufficient permissions"**
- Verify all required scopes/permissions are requested
- For Meta: Check permissions are approved in App Review (production)
- For LinkedIn: Verify products are added and approved

**3. "Token expired"**
- LinkedIn: Re-authenticate (no refresh token)
- Twitter: Use refresh endpoint
- Meta: Re-authenticate for user token, Page tokens never expire

**4. "PKCE validation failed" (Twitter)**
- Ensure `code_verifier` is stored and passed to callback
- Verify code_verifier matches what was used to generate code_challenge
- Check that code is used only once (can't be reused)

**5. "State parameter mismatch"**
- Implement state validation with Redis/database
- Check state hasn't expired (10-minute window)
- Verify state matches between authorize and callback

**6. "Database connection error"**
- Ensure database is running: `docker-compose up -d postgres`
- Run migrations: `alembic upgrade head`
- Check DATABASE_URL in .env

---

## 📚 Additional Resources

### Documentation
- **LinkedIn OAuth**: https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication
- **Twitter OAuth 2.0**: https://developer.twitter.com/en/docs/authentication/oauth-2-0
- **Meta OAuth**: https://developers.facebook.com/docs/facebook-login/guides/advanced/manual-flow

### API References
- **LinkedIn API**: https://learn.microsoft.com/en-us/linkedin/marketing/
- **Twitter API v2**: https://developer.twitter.com/en/docs/twitter-api
- **Meta Graph API**: https://developers.facebook.com/docs/graph-api

### Support
- **LinkedIn Developer Forums**: https://www.linkedin.com/help/linkedin/forums
- **Twitter Developer Community**: https://twittercommunity.com/
- **Meta for Developers**: https://developers.facebook.com/support

---

**Last Updated**: Session 16  
**Maintainer**: AI Growth Manager Team

