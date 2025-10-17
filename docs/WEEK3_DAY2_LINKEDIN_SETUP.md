# Week 3 Day 2: LinkedIn API Setup

## Overview
This guide walks you through setting up LinkedIn API access for the AI Growth Manager application. You'll create a LinkedIn App, configure OAuth 2.0 authentication, and enable posting to LinkedIn profiles and company pages.

## Prerequisites
- Active LinkedIn account (personal or company)
- Email address for verification
- AI Growth Manager backend running locally
- Completed Twitter OAuth setup (Day 1)

## Timeline
- **App Creation**: 5-10 minutes
- **OAuth Configuration**: 10-15 minutes
- **Product Access Request**: 5-10 minutes
- **Approval Wait Time**: Instant to 24 hours
- **Total Active Time**: ~20-40 minutes

---

## Step 1: Create LinkedIn Developer App

### 1.1 Navigate to LinkedIn Developer Portal
1. Go to [https://www.linkedin.com/developers](https://www.linkedin.com/developers)
2. Click **"Create app"** button
3. Log in with your LinkedIn account if needed

### 1.2 Complete App Information

Fill out the app creation form:

**App name:**
```
AI Growth Manager
```

**LinkedIn Page:**
- **Option A**: Select your existing LinkedIn Company Page
- **Option B**: If you don't have one, create a LinkedIn Page first at [https://www.linkedin.com/company/setup/new/](https://www.linkedin.com/company/setup/new/)

**App logo:**
- Upload a 300x300px logo (optional but recommended)
- Use your brand logo or a generic app icon

**Legal agreement:**
- ✅ Check "I have read and agree to the LinkedIn API Terms of Use"

Click **"Create app"**

---

## Step 2: Configure App Settings

### 2.1 Verify Your App
1. Go to the **"Settings"** tab
2. Under **"App settings"**, you'll see your app
3. Click **"Verify"** (if required)
4. LinkedIn will send a verification URL to your Company Page admin
5. Complete the verification process

### 2.2 Add Products (CRITICAL!)

LinkedIn requires you to request access to specific API products:

1. Go to the **"Products"** tab
2. Request access to **"Sign In with LinkedIn using OpenID Connect"**
   - Click **"Request access"**
   - Fill out the form explaining your use case
   
3. Request access to **"Share on LinkedIn"**
   - Click **"Request access"**
   - This allows posting to LinkedIn

4. Request access to **"Marketing Developer Platform"** (Optional, for advanced features)
   - Only needed for analytics and ads
   - Can be added later

**Use Case Description for "Share on LinkedIn":**
```
AI Growth Manager is a multi-tenant SaaS platform that provides social media 
management services to multiple business customers. Our platform enables 
different companies and entrepreneurs to manage their LinkedIn presence 
through a centralized dashboard.

PLATFORM NATURE:
- Multi-tenant application serving multiple independent businesses
- Each business connects their own LinkedIn account via OAuth
- Businesses manage their own content and posting schedule
- No cross-tenant data sharing or access

KEY FEATURES:
- OAuth 2.0 authentication for each business's LinkedIn account
- Allow authenticated users to create and publish posts to their LinkedIn
- Schedule posts for future publication to user's own timeline
- Retrieve authenticated user's profile information
- Display basic post analytics for user's published content

USER BENEFIT:
- AI-assisted content creation for multiple business customers
- Consistent posting schedule management
- Better engagement through optimized timing
- Centralized multi-platform social media management

TECHNICAL IMPLEMENTATION:
- OAuth 2.0 for secure per-user authentication
- UGC Posts API for publishing user-generated content
- Each business authorizes their own LinkedIn account
- Profile API for retrieving member information
- Strict privacy standards - no data mining, sharing, or selling
- Data isolation between different business tenants

IMPORTANT:
All actions are explicitly initiated by authenticated users managing their own 
business accounts. We do not perform any automated, bulk, or cross-tenant 
actions. Each business has full control over their LinkedIn integration.
```

### 2.3 Wait for Product Approval
- **"Sign In with LinkedIn"** - Usually approved instantly ✅
- **"Share on LinkedIn"** - May take 24 hours (sometimes instant)
- You'll receive email notifications when approved

---

## Step 3: Configure OAuth 2.0 Settings

### 3.1 Set Up OAuth Redirect URLs

1. Go to the **"Auth"** tab
2. Scroll to **"OAuth 2.0 settings"**
3. Add the following **Redirect URLs** (one per line):

**For Development (using localtunnel):**
```
https://aigrowth.loca.lt/api/oauth/linkedin/callback
```

**For Production (add these later):**
```
https://yourdomain.com/api/oauth/linkedin/callback
https://app.yourdomain.com/api/oauth/linkedin/callback
```

4. Click **"Update"**

### 3.2 Get Your Credentials

In the **"Auth"** tab, you'll find:

1. **Client ID** (visible immediately)
   - Copy this - you'll need it for your `.env` file
   
2. **Client Secret** (click "Show" to reveal)
   - **IMPORTANT**: Copy this immediately and store it securely
   - You won't be able to see it again!

**Example:**
```
Client ID: 78abc1234xyz
Client Secret: A1B2C3D4E5F6G7H8
```

### 3.3 Configure OAuth Scopes

LinkedIn uses scopes to define what your app can access:

**Required Scopes:**
- `openid` - Basic authentication
- `profile` - User profile information
- `email` - User email address
- `w_member_social` - Post to LinkedIn on behalf of user

These are automatically configured when you add the "Share on LinkedIn" product.

---

## Step 4: Update Backend Environment Variables

### 4.1 Add LinkedIn Credentials to .env

Open `backend/.env` and update the LinkedIn section:

```bash
# LinkedIn OAuth Configuration
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
```

### 4.2 Verify Backend OAuth Routes

The backend already has LinkedIn OAuth configured:
- `/api/oauth/linkedin/authorize` - Initiates OAuth flow
- `/api/oauth/linkedin/callback` - Handles OAuth callback
- `/api/oauth/linkedin/connect` - Connects account to business

---

## Step 5: Test the Integration

### 5.1 Ensure Tunnel is Running

If you closed the tunnel from Twitter setup, restart it:

```bash
lt --port 8003 --subdomain aigrowth
```

Your URL: `https://aigrowth.loca.lt`

### 5.2 Update Frontend Environment (if needed)

Ensure `frontend/.env.local` has:

```bash
# For LinkedIn OAuth testing (same as Twitter)
NEXT_PUBLIC_API_URL=https://aigrowth.loca.lt
```

### 5.3 Test OAuth Flow

1. **Start both servers:**
   ```bash
   # Backend
   cd backend && ./venv/bin/python -m uvicorn app.main:app --reload --port 8003
   
   # Frontend
   cd frontend && npm run dev
   ```

2. **Open browser** to `http://localhost:3000`

3. **Go to Settings** → **Social Accounts**

4. **Click "Connect LinkedIn"**

5. **You'll be redirected to LinkedIn** to authorize

6. **Authorize the app**

7. **Redirected back** - LinkedIn account should show as connected! ✅

---

## Step 6: Test LinkedIn Posting

### 6.1 Create a Test Post

1. Go to **Content** or **Strategies** section
2. Create a new post
3. Select **LinkedIn** as the platform
4. Write a test post (e.g., "Testing my AI Growth Manager integration! 🚀")
5. Click **"Publish"**

### 6.2 Verify on LinkedIn

1. Go to your LinkedIn profile
2. Check your posts/activity
3. The test post should appear! ✅

---

## API Endpoints & Capabilities

### LinkedIn UGC Posts API v2

**What You Can Do:**
- ✅ Post text updates to personal profile
- ✅ Post text updates to company pages (if admin)
- ✅ Upload and post images (up to 9 images)
- ✅ Post videos (with video upload)
- ✅ Post articles with rich previews
- ✅ Auto-threading for long posts (>3000 characters)
- ✅ Retrieve post analytics

**Rate Limits:**
- **100 posts per user per day** (personal profile)
- **250 posts per day** per organization page
- **Generous limits** for most use cases

**Content Restrictions:**
- Max **3000 characters** per post (auto-thread if longer)
- Max **9 images** per post
- Supported image formats: JPG, PNG, GIF
- Max image size: **5MB** per image

---

## Troubleshooting

### Issue: "Share on LinkedIn" Product Not Approved
**Solution:**
- Wait 24 hours for review
- Check email for approval notification
- Ensure your use case description is clear
- Highlight that users initiate all actions (not automated)

### Issue: "Redirect URI Mismatch"
**Solution:**
- Ensure `https://aigrowth.loca.lt/api/oauth/linkedin/callback` is added exactly
- No trailing slashes
- Must use HTTPS (not HTTP)
- Tunnel must be running

### Issue: "Invalid Client Credentials"
**Solution:**
- Double-check Client ID and Secret in `.env`
- Ensure no extra spaces
- Regenerate credentials if needed
- Restart backend server after updating `.env`

### Issue: "Insufficient Permissions" When Posting
**Solution:**
- Ensure "Share on LinkedIn" product is approved
- Check that `w_member_social` scope is granted
- Reconnect your LinkedIn account
- Verify OAuth token has write permissions

### Issue: "LinkedIn Account Not Connecting"
**Solution:**
- Check backend logs for errors
- Verify tunnel is active and responding
- Ensure OAuth callback URL is correct
- Try disconnecting and reconnecting

---

## LinkedIn API Features

### Available with "Share on LinkedIn" Product:

**UGC Posts API:**
- Create text posts
- Upload and share images
- Share articles with previews
- Post to personal timeline
- Post to organization pages (if admin)

**Profile API:**
- Get authenticated user's profile
- Access name, headline, profile picture
- Access email address (with email scope)

**Analytics (Limited):**
- Basic post engagement metrics
- Likes, comments, shares count
- Impressions and reach data

### NOT Available in Free Tier:

❌ Advanced analytics (requires Marketing Developer Platform)
❌ Lead generation forms
❌ Advertising APIs
❌ Recruiter APIs
❌ Sales Navigator integration

---

## Security Best Practices

### 1. Protect Your Credentials
- ✅ Never commit `.env` file to git
- ✅ Use `.env.example` for templates
- ✅ Store Client Secret in password manager
- ✅ Rotate credentials if exposed

### 2. OAuth Security
- ✅ Validate all redirect URIs
- ✅ Use state parameter to prevent CSRF
- ✅ HTTPS required in production
- ✅ Implement token refresh logic
- ✅ Encrypt stored access tokens

### 3. Token Management
- ✅ LinkedIn tokens expire after 60 days
- ✅ Implement automatic token refresh
- ✅ Handle token expiration gracefully
- ✅ Provide clear re-authorization flow

---

## Next Steps

After completing LinkedIn setup:

1. **Week 3 Day 3**: Meta (Facebook/Instagram) API Setup
2. **Week 3 Day 4**: Test all social media integrations
3. **Week 3 Day 5**: Content calendar and scheduling features

---

## Resources

- [LinkedIn Developer Portal](https://www.linkedin.com/developers)
- [LinkedIn API Documentation](https://learn.microsoft.com/en-us/linkedin/)
- [UGC Posts API Guide](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/ugc-post-api)
- [OAuth 2.0 Guide](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication)
- [LinkedIn API Best Practices](https://learn.microsoft.com/en-us/linkedin/shared/api-guide/best-practices)

---

## Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Review LinkedIn's API documentation
3. Check backend logs for detailed error messages
4. Verify all environment variables are set correctly
5. Ensure "Share on LinkedIn" product is approved

---

**Estimated Time to Complete**: 20-40 minutes + approval wait time

**Current Status**: Ready to begin Step 1

---

## Quick Reference

### OAuth URLs in LinkedIn Settings:
```
https://aigrowth.loca.lt/api/oauth/linkedin/callback
```

### Environment Variables Needed:
```bash
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
```

### Backend Endpoints:
- Authorize: `/api/oauth/linkedin/authorize`
- Callback: `/api/oauth/linkedin/callback`
- Connect: `/api/oauth/linkedin/connect`

### Testing Checklist:
- [ ] App created and verified
- [ ] "Share on LinkedIn" product approved
- [ ] OAuth redirect URL configured
- [ ] Credentials added to `.env`
- [ ] Backend restarted
- [ ] Tunnel running
- [ ] OAuth flow tested
- [ ] Test post published successfully
