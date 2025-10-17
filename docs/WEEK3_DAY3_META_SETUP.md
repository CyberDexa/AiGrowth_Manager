# Week 3 Day 3: Meta (Facebook/Instagram) OAuth Setup

## Overview
This guide walks you through completing Meta (Facebook/Instagram) OAuth configuration for the AI Growth Manager application. You already have your Meta App ID and Secret - now we'll add the necessary products and configure OAuth to enable posting to Facebook and Instagram.

## Prerequisites
- Meta Developer account created ✅
- Meta App created: "AI Growth Manager" ✅
- App ID: `4284592478453354` ✅
- App Secret: `4d236810aab33cf822fa89e9490f1303` ✅
- Credentials in `backend/.env` ✅
- AI Growth Manager backend running locally
- Completed Twitter (Day 1) and LinkedIn (Day 2) OAuth setup

## Timeline
- **Add Products**: 5 minutes
- **OAuth Configuration**: 5-10 minutes
- **Testing**: 10-15 minutes
- **Total Active Time**: ~20-30 minutes

---

## Step 1: Add Facebook Login Product

### 1.1 Navigate to Your Meta App
1. Go to [https://developers.facebook.com/apps](https://developers.facebook.com/apps)
2. Click on **"AI Growth Manager"** (App ID: 4284592478453354)
3. You'll see the App Dashboard

### 1.2 Add Facebook Login
1. In the left sidebar, find **"Add Products"** section
2. Locate **"Facebook Login"** product
3. Click **"Set Up"** button
4. Select **"Web"** as the platform (or skip if asked)

### 1.3 Configure Facebook Login Settings
1. In left sidebar, click **"Facebook Login"** → **"Settings"**
2. You'll see **"Valid OAuth Redirect URIs"** section
3. Add the following URLs (one per line):

**For Development (using localtunnel):**
```
https://aigrowth.loca.lt/api/v1/oauth/meta/callback
```

**For Production (add these later):**
```
https://yourdomain.com/api/v1/oauth/meta/callback
https://app.yourdomain.com/api/v1/oauth/meta/callback
```

4. Scroll down and click **"Save Changes"**

### 1.4 Configure OAuth Settings
In the same Facebook Login Settings page:

**Client OAuth Login**: ✅ Enable  
**Web OAuth Login**: ✅ Enable  
**Force Web OAuth Reauthentication**: ❌ Disable (optional)  
**Use Strict Mode for Redirect URIs**: ✅ Enable  
**Login with the JavaScript SDK**: ✅ Enable (optional)

Click **"Save Changes"**

---

## Step 2: Add Instagram Graph API Product

### 2.1 Add Instagram Graph API
1. In the left sidebar, find **"Add Products"** section again
2. Locate **"Instagram Graph API"** or **"Instagram Basic Display"**
3. Click **"Set Up"** button
4. **That's it!** ✅ No need to connect your own Instagram account

### 2.2 Understanding Multi-Tenant OAuth
**IMPORTANT - Multi-Tenant Architecture:**

Since AI Growth Manager is a **multi-tenant SaaS platform**:
- ❌ **You (the developer) DON'T connect your Instagram account**
- ✅ **Your customers connect THEIR Instagram Business accounts** via OAuth
- ✅ Each business authenticates independently through your app
- ✅ Your app posts to their accounts on their behalf
- ✅ Complete data isolation between different businesses

**What happens in production:**
1. Customer signs up for AI Growth Manager
2. Customer clicks "Connect Instagram" in their dashboard
3. They're redirected to Facebook/Instagram OAuth
4. They authorize YOUR APP to access THEIR Instagram Business account
5. Your app stores their OAuth token (encrypted, isolated per business)
6. Your app can now post to their Instagram on their behalf

### 2.3 Optional: Connect Your Own Instagram for Testing
**Only if you want to test Instagram posting during development:**

If you want to test Instagram features before having customers:
1. Convert your personal Instagram to Business account (see below)
2. Test the OAuth flow with your own account
3. Verify posting works

**To convert personal Instagram to Business:**
1. Open Instagram mobile app
2. Go to **Settings** → **Account**
3. Tap **"Switch to Professional Account"**
4. Choose **"Business"** or **"Creator"**
5. Connect it to your Facebook Page
6. Complete the setup

**Note**: This is **optional** for development testing only. In production, each customer connects their own Instagram Business account.

---

## Step 3: Configure App Permissions & Scopes

### 3.1 Request Required Permissions
Meta apps need specific permissions to post content:

1. Go to **"App Review"** → **"Permissions and Features"**
2. Request the following permissions:

**For Facebook Posting:**
- ✅ `pages_manage_posts` - Publish posts to Pages
- ✅ `pages_read_engagement` - Read Page engagement data
- ✅ `pages_show_list` - Get list of Pages user manages
- ✅ `public_profile` - Access public profile info
- ✅ `email` - Access email address

**For Instagram Posting:**
- ✅ `instagram_basic` - Basic Instagram access
- ✅ `instagram_content_publish` - Publish content to Instagram
- ✅ `instagram_manage_comments` - Manage comments
- ✅ `instagram_manage_insights` - Access insights

3. For each permission:
   - Click **"Request Advanced Access"**
   - Fill out the use case form (see below)
   - Submit for review

### 3.2 Use Case Description for Permissions
```
AI Growth Manager is a multi-tenant SaaS platform serving multiple business 
customers who need to manage their Facebook and Instagram presence through 
a centralized dashboard.

PLATFORM NATURE:
- Multi-tenant application serving multiple independent businesses
- Each business connects their own Facebook Pages and Instagram accounts via OAuth
- Complete data isolation between different business tenants
- No cross-tenant data sharing or access

USE CASE FOR PERMISSIONS:

1. pages_manage_posts:
   - Allow authenticated business users to publish posts to their Facebook Pages
   - Schedule content for future publication
   - All posting is user-initiated through our dashboard

2. instagram_content_publish:
   - Allow authenticated business users to publish content to their Instagram Business accounts
   - Support images, videos, and captions
   - All posting is user-initiated and business-controlled

3. pages_read_engagement & instagram_manage_insights:
   - Display post performance metrics to business users
   - Show engagement data (likes, comments, shares)
   - Help businesses understand their content performance

TECHNICAL IMPLEMENTATION:
- OAuth 2.0 for secure per-business authentication
- Each business authorizes their own Facebook Pages and Instagram accounts
- Token storage with encryption and secure handling
- Data isolation at database and application level
- Strict privacy standards - no data mining, sharing, or selling

USER BENEFIT:
- AI-assisted content creation for multiple business customers
- Multi-platform posting (Facebook, Instagram, LinkedIn, Twitter)
- Consistent brand presence across social media
- Time-saving through centralized management
- Analytics and insights for better decision-making

IMPORTANT:
All actions are explicitly initiated by authenticated users managing their 
own business accounts. We do not perform automated bulk posting, data scraping, 
or any cross-tenant operations. Each business maintains full control over 
their social media integrations.
```

### 3.3 Development Mode (No Review Needed)
**Good News**: While permissions are under review, you can still test in **Development Mode**!

- In Development Mode, you can test with:
  - Your own account
  - Test users you create
  - Accounts you add as Developers/Testers/Admins

- To add test users:
  1. Go to **"Roles"** → **"Roles"**
  2. Click **"Add Testers"**
  3. Enter Facebook usernames or User IDs
  4. They'll receive an invitation to accept

---

## Step 4: Configure App Settings

### 4.1 Update App Domain
1. Go to **"Settings"** → **"Basic"**
2. Scroll to **"App Domains"**
3. Add:
   ```
   aigrowth.loca.lt
   localhost
   ```
4. Click **"Save Changes"**

### 4.2 Add Platform (if not already added)
1. Scroll down to **"Add Platform"**
2. Click **"Website"**
3. Enter Site URL:
   ```
   https://aigrowth.loca.lt
   ```
4. Click **"Save Changes"**

### 4.3 Privacy Policy URL
1. In **"Settings"** → **"Basic"**
2. Find **"Privacy Policy URL"**
3. Add:
   ```
   https://aigrowth.loca.lt/privacy
   ```
   (We'll create this page later if needed)
4. Click **"Save Changes"**

---

## Step 5: Verify Backend Configuration

### 5.1 Check Environment Variables
Your `backend/.env` should already have:

```bash
# Meta (Facebook/Instagram)
META_APP_ID=4284592478453354
META_APP_SECRET=4d236810aab33cf822fa89e9490f1303
```

### 5.2 Verify Backend OAuth Routes
The backend already has Meta OAuth configured:
- `/api/v1/oauth/meta/authorize` - Initiates OAuth flow
- `/api/v1/oauth/meta/callback` - Handles OAuth callback
- `/api/v1/oauth/meta/connect` - Connects account to business

### 5.3 Check Backend Meta Integration
The backend includes:
- Facebook Graph API client
- Instagram Graph API client
- Token management and refresh
- Multi-tenant account isolation

---

## Step 6: Test the Integration

### 6.1 Ensure Servers are Running

**Start Localtunnel** (if not running):
```bash
lt --port 8003 --subdomain aigrowth
```

**Start Backend**:
```bash
cd backend && ./venv/bin/python -m uvicorn app.main:app --reload --port 8003
```

**Start Frontend**:
```bash
cd frontend && npm run dev
```

### 6.2 Test Facebook OAuth Flow

1. **Open browser** to `http://localhost:3000`
2. **Sign in** to your account
3. **Go to Settings** → **Social Accounts**
4. **Click "Connect Facebook"**
5. **You'll be redirected to Facebook** to authorize
6. **Select Facebook Pages** you want to connect
7. **Authorize the app**
8. **Redirected back** - Facebook account should show as connected! ✅

### 6.3 Test Instagram OAuth Flow

1. **In Settings** → **Social Accounts**
2. **Click "Connect Instagram"**
3. **You'll be redirected to Facebook/Instagram** to authorize
4. **Select Instagram Business account** to connect
5. **Authorize the app**
6. **Redirected back** - Instagram account should show as connected! ✅

---

## Step 7: Test Posting

### 7.1 Test Facebook Post

1. Go to **Content** or **Strategies** section
2. Create a new post
3. Select **Facebook** as the platform
4. Write a test post (e.g., "Testing my AI Growth Manager integration! 🚀")
5. Click **"Publish"**
6. Go to your Facebook Page and verify the post appears! ✅

### 7.2 Test Instagram Post

1. Create a new post
2. Select **Instagram** as the platform
3. Upload an image (required for Instagram)
4. Write a caption (e.g., "Testing AI Growth Manager! 🎨 #automation")
5. Click **"Publish"**
6. Go to your Instagram Business profile and verify the post appears! ✅

---

## API Capabilities

### Facebook Graph API

**What You Can Do:**
- ✅ Post text updates to Facebook Pages
- ✅ Upload and post images (up to 10 images)
- ✅ Post videos
- ✅ Schedule posts for later
- ✅ Post links with rich previews
- ✅ Get Page information
- ✅ Retrieve post insights and analytics

**Rate Limits:**
- **200 calls per hour** per user
- **Rate limit applies per app per user**
- Generous for most use cases

**Content Restrictions:**
- Max **63,206 characters** per post
- Max **10 images** per post
- Supported formats: JPG, PNG, GIF, BMP
- Max image size: **4MB** per image
- Video max size: **1GB**

### Instagram Graph API

**What You Can Do:**
- ✅ Post photos to Instagram feed
- ✅ Post videos to Instagram feed
- ✅ Post carousel albums (up to 10 items)
- ✅ Post Instagram Stories (with approval)
- ✅ Post Instagram Reels (with approval)
- ✅ Get Instagram account info
- ✅ Retrieve post insights and analytics

**Rate Limits:**
- **25 posts per day** per Instagram account
- **200 calls per hour** per user (API calls)
- Be mindful of Instagram's content guidelines

**Content Restrictions:**
- **Image required** for all feed posts
- Max **2,200 characters** for captions
- Aspect ratios: 1.91:1 to 4:5
- Supported formats: JPG, PNG
- Max image size: **8MB**
- Video: 3-60 seconds, max **100MB**

---

## Troubleshooting

### Issue: "Invalid OAuth Redirect URI"
**Solution:**
- Ensure `https://aigrowth.loca.lt/api/v1/oauth/meta/callback` is added to Facebook Login settings
- No trailing slashes
- Must use HTTPS (not HTTP)
- Tunnel must be running

### Issue: "App Not Setup"
**Solution:**
- Ensure Facebook Login product is added
- Check OAuth redirect URIs are configured
- Verify app is in Development or Live mode

### Issue: "Insufficient Permissions"
**Solution:**
- Check that required permissions are requested
- In Development Mode, test with your own account or added testers
- For production, wait for permission review approval

### Issue: "Instagram Account Not Eligible"
**Solution:**
- Instagram account must be a Business or Creator account
- Must be linked to a Facebook Page
- Convert personal account to business in Instagram app settings

### Issue: "Can't Select Facebook Page"
**Solution:**
- Ensure you're an admin of the Facebook Page
- Page must be published (not unpublished/draft)
- Try disconnecting and reconnecting

### Issue: "Posts Not Appearing"
**Solution:**
- Check backend logs for API errors
- Verify access tokens are valid
- Ensure Pages have proper permissions
- Check Instagram account is Business account
- Review Meta's content policies (may be blocked if violates policies)

---

## Development vs Live Mode

### Development Mode (Current)
- **Testing**: Test with your account and added testers
- **Limitations**: Only works for developers, testers, and admins
- **Permissions**: No review needed for basic testing
- **Best for**: Building and testing features

### Live Mode (Production)
- **Public Access**: Anyone can connect their accounts
- **Requirements**: App Review required for permissions
- **Process**: Submit for review with screenshots and demo
- **Timeline**: 3-7 days for review

### Switching to Live Mode (Later)
When ready for production:
1. Complete App Review for all permissions
2. Add Privacy Policy and Terms of Service
3. Switch app to "Live" mode
4. Update OAuth redirect URLs to production domain

---

## Security Best Practices

### 1. Protect Your Credentials
- ✅ Never commit `.env` file to git
- ✅ Use `.env.example` for templates
- ✅ Store App Secret in password manager
- ✅ Rotate credentials if exposed

### 2. OAuth Security
- ✅ Validate all redirect URIs
- ✅ Use state parameter to prevent CSRF
- ✅ HTTPS required in production
- ✅ Implement token refresh logic
- ✅ Encrypt stored access tokens

### 3. Token Management
- ✅ Facebook tokens expire after 60 days
- ✅ Implement automatic token refresh
- ✅ Handle token expiration gracefully
- ✅ Provide clear re-authorization flow

### 4. Multi-Tenant Isolation
- ✅ Never share tokens between businesses
- ✅ Isolate data at database level
- ✅ Validate business ownership before API calls
- ✅ Audit all cross-tenant access attempts

---

## Next Steps

After completing Meta setup:

1. **Week 3 Day 4**: Test All OAuth Integrations (Twitter, LinkedIn, Meta)
2. **Week 3 Day 5**: Multi-Platform Content Publishing & Scheduling
3. **Week 4**: Analytics Dashboard & Content Calendar

---

## Resources

- [Meta for Developers](https://developers.facebook.com)
- [Facebook Graph API Documentation](https://developers.facebook.com/docs/graph-api)
- [Instagram Graph API Documentation](https://developers.facebook.com/docs/instagram-api)
- [App Review Process](https://developers.facebook.com/docs/app-review)
- [Facebook Login Documentation](https://developers.facebook.com/docs/facebook-login)
- [Instagram Business Account Setup](https://help.instagram.com/502981923235522)

---

## Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Review Meta's developer documentation
3. Check backend logs for detailed error messages
4. Verify all environment variables are set correctly
5. Ensure you're testing with a Business Instagram account

---

**Estimated Time to Complete**: 20-30 minutes

**Current Status**: Ready to begin Step 1

---

## Quick Reference

### Meta App Details:
```
App ID: 4284592478453354
App Secret: 4d236810aab33cf822fa89e9490f1303
```

### OAuth Redirect URL:
```
https://aigrowth.loca.lt/api/v1/oauth/meta/callback
```

### Required Permissions:
```
Facebook:
- pages_manage_posts
- pages_read_engagement
- pages_show_list
- public_profile
- email

Instagram:
- instagram_basic
- instagram_content_publish
- instagram_manage_insights
```

### Backend Endpoints:
- Authorize: `/api/v1/oauth/meta/authorize`
- Callback: `/api/v1/oauth/meta/callback`
- Connect: `/api/v1/oauth/meta/connect`

### Testing Checklist:
- [ ] Facebook Login product added
- [ ] Instagram Graph API product added
- [ ] OAuth redirect URI configured
- [ ] App domains configured
- [ ] Credentials verified in `.env`
- [ ] Backend restarted
- [ ] Tunnel running
- [ ] Facebook OAuth tested (with your account OR test customer)
- [ ] Instagram OAuth tested (optional - only if you want to test posting)
- [ ] Test post to Facebook successful (optional)
- [ ] Test post to Instagram successful (optional)

### Multi-Tenant Notes:
- ✅ **Developer**: Configure products and OAuth (no need to connect your own accounts)
- ✅ **Customers**: Each connects their own Facebook Pages and Instagram Business accounts
- ✅ **Testing**: Optional - you can test with your own accounts before having customers
- ✅ **Production**: Each business authenticates independently through OAuth
