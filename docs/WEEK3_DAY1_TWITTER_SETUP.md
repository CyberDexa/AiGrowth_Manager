# Week 3 Day 1: Twitter/X Developer Account Setup

## Overview
This guide walks you through setting up Twitter/X API access for the AI Growth Manager application. You'll create a developer account, apply for Elevated Access, and configure OAuth 2.0 authentication.

## Prerequisites
- Active Twitter/X account (you'll use this to create the developer account)
- Email address for verification
- AI Growth Manager backend running locally

## Timeline
- **Developer Account Creation**: 5-10 minutes
- **Elevated Access Application**: 10-15 minutes
- **Approval Wait Time**: 1-2 business days (sometimes faster)
- **App Configuration**: 10-15 minutes
- **Total Active Time**: ~30-40 minutes + waiting for approval

---

## Step 1: Create Twitter Developer Account

### 1.1 Navigate to Twitter Developer Portal
1. Go to [https://developer.twitter.com](https://developer.twitter.com)
2. Click **"Sign Up"** or **"Apply for a developer account"**
3. Log in with your Twitter/X account

### 1.2 Complete Basic Information
Fill out the developer account application:
- **Account Type**: Select your account type (usually "Professional" or "Hobbyist")
- **Country**: Select your country
- **Use Case**: Describe what you're building

**Example Use Case Description:**
```
I'm building AI Growth Manager, a multi-tenant SaaS platform that provides 
social media management services to multiple business customers. The platform 
enables different companies to manage their Twitter/X presence through our 
centralized dashboard.

PLATFORM NATURE:
- Multi-tenant application serving multiple independent businesses
- Each business connects their own Twitter account via OAuth 2.0
- Businesses manage their own content and posting schedule
- No cross-tenant data sharing or access

KEY FEATURES:
1. OAuth 2.0 authentication for each business's Twitter account
2. Post tweets on behalf of authenticated users to their own timeline
3. Upload media (images) with tweets
4. Schedule tweets for future publication
5. Retrieve authenticated user's basic profile information
6. Display post analytics for user's own published content

TECHNICAL IMPLEMENTATION:
- OAuth 2.0 with PKCE for secure per-user authentication
- Each business authorizes their own Twitter account
- Data isolation between different business tenants
- No automated, bulk, or cross-tenant actions

This is a SaaS platform for business owners to manage their social media 
presence efficiently. All actions are user-initiated and tenant-isolated.
```

### 1.3 Verify Email
- Check your email for verification link
- Click the link to verify your developer account

---

## Step 2: Apply for Elevated Access

### 2.1 Why Elevated Access?
Free tier (Essential) has strict limitations:
- Only 1,500 tweets per month
- Limited endpoints
- No media upload support

**Elevated Access provides:**
- 50,000 tweets per month (write)
- 2,000,000 tweets per month (read)
- Media upload support
- Full OAuth 2.0 support
- Essential for production apps

### 2.2 Submit Elevated Access Application

1. In the Developer Portal, go to **"Products"** → **"Twitter API v2"**
2. Click **"Apply for Elevated Access"** or **"Elevated"**
3. Fill out the detailed application form

### 2.3 Application Questions and Answers

**Question: In your words, describe how you plan to use Twitter data and/or APIs**

**Sample Answer:**
```
I am developing "AI Growth Manager", a multi-tenant SaaS platform that 
provides social media management services to multiple business customers. 
Our platform helps different companies and entrepreneurs manage their 
Twitter/X presence through a centralized dashboard.

PLATFORM NATURE:
- Multi-tenant SaaS application serving multiple independent businesses
- Each business connects their own Twitter account via OAuth 2.0
- Complete data isolation between different business tenants
- No cross-tenant data sharing or access

CORE FUNCTIONALITY:
- OAuth 2.0 authentication for each business's Twitter account
- Allow authenticated users to schedule and publish tweets to their timeline
- Upload images and media to accompany tweets
- Generate AI-powered content suggestions for authenticated users
- Retrieve profile information for authenticated accounts only
- Display basic tweet analytics for user's own published content

TECHNICAL IMPLEMENTATION:
- OAuth 2.0 with PKCE for secure per-user authentication
- POST /2/tweets endpoint for publishing user-generated content
- Media upload endpoints for images
- GET /2/users/me for authenticated user's profile information
- Rate limiting and error handling to respect API limits
- Tenant isolation at database and application level

DATA USAGE & PRIVACY:
- All data stays within each tenant's isolated account
- No aggregation or analysis of other users' or tenants' data
- No data mining, selling, or cross-tenant sharing
- Strict privacy, security, and multi-tenant isolation standards
- Each business has full control over their Twitter integration

USER BENEFIT:
- Multiple businesses can use our platform independently
- AI-assisted content creation for each business
- Consistent posting schedule management
- Better engagement through optimized timing
- Centralized multi-platform social media management

IMPORTANT:
All actions are explicitly initiated by authenticated users managing their 
own business accounts. We do not perform any automated, bulk, or cross-tenant 
actions. Each business maintains complete control and privacy.
```

**Question: Will your app use Tweet, Retweet, Like, Follow, or Direct Message functionality?**

**Answer:**
```
Yes, primarily Tweet functionality:

TWEET CREATION:
- Allow users to compose and publish tweets
- Upload images to accompany tweets
- Schedule tweets for future publication

The app will NOT:
- Automatically retweet content
- Auto-like tweets
- Auto-follow users
- Send automated Direct Messages
- Perform any bulk actions

All actions are explicitly initiated by the authenticated user through the 
application interface.
```

**Question: Do you plan to analyze Twitter data?**

**Answer:**
```
No extensive analysis. Limited to:

1. Basic engagement metrics (likes, retweets, replies) for posts published 
   through the app to help users understand content performance
2. No analysis of other users' data
3. No sentiment analysis of public tweets
4. No trend analysis or data mining
5. No selling or sharing of any Twitter data

The focus is on content creation and publishing, not data analysis.
```

**Question: Will your app display Twitter content?**

**Answer:**
```
Yes, but only content created and published by the authenticated user:

- Display tweets published through the app in a dashboard
- Show basic metrics (engagement stats) for user's own posts
- Display user's profile information

The app will NOT:
- Display feeds of other users' tweets
- Create a Twitter client or alternative interface
- Embed or display third-party tweets
- Build any timeline or search functionality
```

### 2.4 Review and Submit
1. Review all your answers
2. Agree to the Developer Agreement and Policy
3. Click **"Submit Application"**

### 2.5 Wait for Approval
- Approval typically takes 1-2 business days
- Sometimes approved within hours
- Check your email for approval notification
- You can check status in the Developer Portal

---

## Step 3: Create Your Twitter App (After Approval)

### 3.1 Create New App
1. Log into [Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Click **"+ Add App"** or **"Create Project"**
3. Choose **"Production"** environment
4. Name your app: `AI Growth Manager` (or your preferred name)

### 3.2 App Settings
Configure the following:

**App Permissions:**
- ✅ Read
- ✅ Write
- ❌ Direct Messages (not needed)

**Type of App:**
- Select **"Web App, Automated App or Bot"**

**App Info:**
- **App Name**: AI Growth Manager
- **Description**: AI-powered social media management platform
- **Website URL**: `https://your-domain.com` (or `http://localhost:3000` for dev)
- **Privacy Policy URL**: (Optional for development)
- **Terms of Service URL**: (Optional for development)

---

## Step 4: Configure OAuth 2.0 Settings

### 4.1 Enable OAuth 2.0
1. In your App settings, go to **"Keys and tokens"** tab
2. Scroll to **"OAuth 2.0 Settings"**
3. Click **"Set up"** or **"Edit"**

### 4.2 OAuth 2.0 Configuration

**Type of App:**
- Select **"Web App, Automated App or Bot"**

**Callback URLs / Redirect URIs:**
Add the following URLs (one per line):
```
http://localhost:8003/api/oauth/twitter/callback
http://localhost:3000/dashboard/social-accounts
```

**Website URL:**
```
http://localhost:3000
```

### 4.3 Generate Client ID and Secret
1. After configuring OAuth 2.0, Twitter will generate:
   - **OAuth 2.0 Client ID** (public, safe to expose)
   - **OAuth 2.0 Client Secret** (private, keep secure!)

2. **IMPORTANT**: Copy and save these immediately!
   - You won't be able to see the Client Secret again
   - Store them securely (password manager recommended)

---

## Step 5: Update Backend Environment Variables

### 5.1 Add Twitter Credentials to .env

Open `backend/.env` and add:

```bash
# Twitter/X API Configuration
TWITTER_CLIENT_ID=your_client_id_here
TWITTER_CLIENT_SECRET=your_client_secret_here

# Optional: For API v1.1 endpoints (if needed later)
# TWITTER_API_KEY=your_api_key_here
# TWITTER_API_SECRET=your_api_secret_here
# TWITTER_BEARER_TOKEN=your_bearer_token_here
```

### 5.2 Verify Configuration
The backend already has OAuth routes configured:
- `/api/oauth/twitter/authorize` - Initiates OAuth flow
- `/api/oauth/twitter/callback` - Handles OAuth callback
- `/api/oauth/twitter/connect` - Connects account to business

---

## Step 6: Test the Integration

### 6.1 Start Development Environment
Ensure both servers are running:

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m uvicorn app.main:app --reload --port 8003

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

### 6.2 Test OAuth Flow
1. Open browser to `http://localhost:3000`
2. Log in to your account
3. Go to **Dashboard** → **Social Accounts**
4. Click **"Connect Twitter Account"**
5. You should be redirected to Twitter for authorization
6. Authorize the app
7. You should be redirected back to your dashboard
8. Verify the Twitter account appears as connected

### 6.3 Test Tweet Publishing
1. Go to **Content** section
2. Create a new post
3. Select Twitter as the platform
4. Write a test tweet
5. Click **"Publish"**
6. Verify the tweet appears on your Twitter account

---

## Troubleshooting

### Issue: "App is not configured for OAuth 2.0"
**Solution:**
- Verify OAuth 2.0 is enabled in app settings
- Ensure redirect URIs are configured correctly
- Check that Client ID and Secret are in .env file

### Issue: "Callback URL mismatch"
**Solution:**
- Ensure `http://localhost:8003/api/oauth/twitter/callback` is added to allowed URLs
- Check for trailing slashes (Twitter is strict about exact matches)
- Verify port numbers match

### Issue: "Invalid client credentials"
**Solution:**
- Double-check Client ID and Secret in .env
- Regenerate credentials if needed
- Ensure no extra spaces in .env file
- Restart backend server after updating .env

### Issue: "403 Forbidden when posting"
**Solution:**
- Verify app has "Read and Write" permissions
- Check if Elevated Access is approved
- Ensure OAuth token has write scope
- Try reconnecting the Twitter account

### Issue: "Rate limit exceeded"
**Solution:**
- Elevated Access allows 50,000 tweets/month
- That's about 1,600 tweets per day
- Implement rate limiting in your app
- Monitor usage in Developer Portal

---

## API Rate Limits (Elevated Access)

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /2/tweets | 50,000 | Per month |
| GET /2/tweets | 2,000,000 | Per month |
| Media Upload | 50,000 | Per month |
| User Lookup | 900 | Per 15 min |

---

## Security Best Practices

### 1. Protect Your Credentials
- ✅ Never commit .env file to git
- ✅ Use .env.example for templates
- ✅ Store secrets in password manager
- ✅ Use environment variables in production
- ❌ Never hardcode credentials in code

### 2. OAuth Security
- ✅ Use state parameter to prevent CSRF
- ✅ Validate redirect URIs strictly
- ✅ Use HTTPS in production (required by Twitter)
- ✅ Implement token refresh logic
- ✅ Encrypt stored access tokens

### 3. Token Management
- ✅ Store tokens encrypted in database
- ✅ Implement token expiration checks
- ✅ Handle token refresh automatically
- ✅ Provide clear re-authorization flow
- ✅ Log OAuth events for debugging

---

## Next Steps

After completing Twitter setup:

1. **Week 3 Day 2**: LinkedIn API Setup
2. **Week 3 Day 3**: Meta (Facebook/Instagram) API Setup
3. **Week 3 Day 4**: Testing and Integration
4. **Week 3 Day 5**: Production Deployment Preparation

---

## Resources

- [Twitter API Documentation](https://developer.twitter.com/en/docs)
- [OAuth 2.0 Guide](https://developer.twitter.com/en/docs/authentication/oauth-2-0)
- [API Reference](https://developer.twitter.com/en/docs/api-reference-index)
- [Rate Limits](https://developer.twitter.com/en/docs/twitter-api/rate-limits)
- [Developer Portal](https://developer.twitter.com/en/portal/dashboard)

---

## Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Review Twitter's API documentation
3. Check backend logs for detailed error messages
4. Verify all environment variables are set correctly

---

**Estimated Time to Complete**: 30-40 minutes + 1-2 days waiting for approval

**Current Status**: Ready to begin Step 1
