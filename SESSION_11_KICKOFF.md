# 📘 Session 11: Meta (Facebook/Instagram) Integration

**Date**: October 13, 2025  
**Previous Session**: Session 10 - Twitter/X Publishing (Complete)  
**Current Session Goal**: Add Facebook and Instagram posting capability via Meta Graph API

---

## 🎯 OBJECTIVES

### Primary Goal
Enable users to publish AI-generated content to Facebook Pages and Instagram Business accounts from the AI Growth Manager platform.

### Core Features to Build
1. ✅ **Meta OAuth 2.0** - Authenticate with Facebook
2. ✅ **Facebook Page Publishing** - Post to Facebook Pages
3. ✅ **Instagram Business Publishing** - Post to Instagram
4. ✅ **Long-Lived Tokens** - 60-day tokens with refresh
5. ✅ **Page Selection** - Choose which Facebook Page to use
6. ✅ **Instagram Account Linking** - Connect Instagram Business account

### Success Metrics
- User can connect Facebook account via OAuth 2.0
- User can select a Facebook Page
- User can publish posts to Facebook Page
- User can publish posts to Instagram Business
- Posts appear on Facebook and Instagram
- URLs saved for reference

---

## 🏗️ ARCHITECTURE OVERVIEW

### Meta Platform Ecosystem

```
┌─────────────────────────────────────────────────────────────┐
│                    META PLATFORM                             │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Facebook   │  │  Facebook    │  │  Instagram   │      │
│  │   Personal   │  │   Pages      │  │   Business   │      │
│  │   Profile    │  │  (Business)  │  │   Account    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                           ↓                  ↓               │
│                    ┌──────────────┐  ┌──────────────┐      │
│                    │  Page Access │  │  IG Account  │      │
│                    │    Token     │  │    Token     │      │
│                    └──────────────┘  └──────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘

User Auth → Facebook Personal → Get Pages → Select Page
  → Get Page Token → Link Instagram → Ready to Publish!
```

### Publishing Flow

```
┌─────────────────────────────────────────────────────────────┐
│                META PUBLISHING ARCHITECTURE                  │
│                                                              │
│  1. User connects Facebook (OAuth)                          │
│       ↓                                                      │
│  2. Backend gets Facebook Pages list                        │
│       ↓                                                      │
│  3. User selects which Page to use                          │
│       ↓                                                      │
│  4. Backend gets Page Access Token                          │
│       ↓                                                      │
│  5. Backend checks if Page has Instagram linked             │
│       ↓                                                      │
│  6. If yes: Get Instagram Business Account ID               │
│       ↓                                                      │
│  7. User generates content                                  │
│       ↓                                                      │
│  8. User selects Facebook or Instagram                      │
│       ↓                                                      │
│  9. Backend posts via Graph API:                            │
│     • Facebook: POST /{page-id}/feed                        │
│     • Instagram: POST /{ig-user-id}/media                   │
│       ↓                                                      │
│  10. Post appears on selected platform                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 META OAUTH 2.0

### OAuth Flow (Standard, No PKCE)

Unlike Twitter, Meta uses **standard OAuth 2.0** (no PKCE required).

```python
# Step 1: Generate authorization URL
auth_url = (
    "https://www.facebook.com/v18.0/dialog/oauth?"
    f"client_id={APP_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&scope=pages_show_list,pages_read_engagement,pages_manage_posts,"
    f"instagram_basic,instagram_content_publish"
    f"&state={random_state}"
)

# Step 2: User authorizes on Facebook
# Facebook redirects back with: ?code=AUTHORIZATION_CODE&state=STATE

# Step 3: Exchange code for short-lived token (1 hour)
response = requests.get(
    "https://graph.facebook.com/v18.0/oauth/access_token",
    params={
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": authorization_code
    }
)
# Returns: {"access_token": "...", "token_type": "bearer", "expires_in": 5183999}

# Step 4: Exchange short-lived for long-lived token (60 days)
response = requests.get(
    "https://graph.facebook.com/v18.0/oauth/access_token",
    params={
        "grant_type": "fb_exchange_token",
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "fb_exchange_token": short_lived_token
    }
)
# Returns: {"access_token": "...", "token_type": "bearer", "expires_in": 5183999}

# Step 5: Get Page Access Tokens (never expire!)
response = requests.get(
    f"https://graph.facebook.com/v18.0/me/accounts",
    params={"access_token": long_lived_token}
)
# Returns: {
#   "data": [
#     {
#       "id": "123456789",
#       "name": "My Business Page",
#       "access_token": "PAGE_ACCESS_TOKEN",  # ← This never expires!
#       "category": "Company"
#     }
#   ]
# }
```

### Meta OAuth Scopes

| Scope | Permission | Needed For |
|-------|------------|------------|
| `pages_show_list` | List Pages | **Required** - Get user's Pages |
| `pages_read_engagement` | Read Page metrics | Analytics (future) |
| `pages_manage_posts` | Post to Pages | **Required** - Facebook posting |
| `instagram_basic` | Basic IG info | Get Instagram account |
| `instagram_content_publish` | Post to IG | **Required** - Instagram posting |
| `business_management` | Manage Business | Page management (optional) |

---

## 📘 FACEBOOK PAGES API

### Key Concepts

**Facebook Personal Profile** vs **Facebook Page**:
- Personal Profile: Your personal Facebook account
- Page: Business page (e.g., "Acme Corp", "Jane's Coffee Shop")
- **We post to PAGES, not personal profiles!**

**Page Access Token**:
- Special token for a specific Page
- Never expires (unless revoked)
- Obtained from user's long-lived token
- Each Page has its own token

### Publishing to Facebook Page

**POST** `https://graph.facebook.com/v18.0/{page-id}/feed`

**Headers**:
```
Authorization: Bearer {page_access_token}
Content-Type: application/json
```

**Request Body**:
```json
{
  "message": "Check out our new AI-powered content manager! 🚀\n\nGenerate engaging social media posts in seconds.\n\n#AI #SocialMedia #Marketing",
  "published": true,
  "link": "https://example.com"  // Optional
}
```

**Response**:
```json
{
  "id": "123456789_987654321"  // format: {page-id}_{post-id}
}
```

**Post URL**: `https://www.facebook.com/{post-id}`

### Character Limits

| Platform | Text Limit | Link Preview |
|----------|-----------|--------------|
| Facebook Page | 63,206 chars | Yes |
| Facebook Link | ~500 chars ideal | Yes |
| Facebook Image | 2,200 chars | N/A |

**Note**: Facebook has generous limits. No need for threading!

---

## 📷 INSTAGRAM GRAPH API

### Key Concepts

**Instagram Business Account**:
- Must be Instagram Business or Creator account
- Must be linked to a Facebook Page
- Cannot post to personal Instagram accounts

**Instagram Publishing Flow**:
1. Create media container (upload content)
2. Publish container (make it live)
3. Get media ID and permalink

### Publishing to Instagram

**Two-Step Process**:

#### Step 1: Create Media Container

**POST** `https://graph.facebook.com/v18.0/{ig-user-id}/media`

**Parameters**:
```json
{
  "image_url": "https://example.com/image.jpg",  // Image URL
  "caption": "AI-powered social media content! 🚀 #AI #Instagram #Marketing",
  "access_token": "{page_access_token}"
}
```

**Response**:
```json
{
  "id": "18012345678901234"  // Container ID
}
```

#### Step 2: Publish Container

**POST** `https://graph.facebook.com/v18.0/{ig-user-id}/media_publish`

**Parameters**:
```json
{
  "creation_id": "18012345678901234",  // Container ID from step 1
  "access_token": "{page_access_token}"
}
```

**Response**:
```json
{
  "id": "17899123456789012"  // Media ID (published post)
}
```

**Post URL**: Get permalink:
```
GET /{media-id}?fields=permalink
Response: {"permalink": "https://www.instagram.com/p/ABC123/"}
```

### Instagram Limitations

| Feature | Limit | Notes |
|---------|-------|-------|
| **Caption** | 2,200 chars | Includes hashtags |
| **Hashtags** | 30 max | Best practice: 5-10 |
| **Image Required** | Yes | Must provide image_url |
| **Text-Only** | ❌ No | Image always required |
| **Carousel** | 10 items | Advanced feature |
| **Video** | Yes | Different API call |

**Critical**: Instagram requires an image! Cannot post text-only.

---

## 📁 FILE STRUCTURE

### Backend Files to Create

```
backend/
├── app/
│   ├── services/
│   │   ├── oauth_meta.py              ← NEW: Meta OAuth 2.0 service
│   │   └── publishing_meta.py         ← NEW: Facebook + Instagram publishing
│   │
│   ├── api/
│   │   ├── social.py                  ← MODIFY: Add Meta OAuth endpoints
│   │   └── publishing.py              ← MODIFY: Add Meta publishing endpoint
│   │
│   ├── models/
│   │   └── social_account.py          ← MODIFY: Add page_id, instagram_id fields
│   │
│   └── schemas/
│       └── social.py                  ← MODIFY: Add FacebookPage, InstagramAccount schemas
```

### Frontend Files to Modify

```
frontend/
├── app/
│   ├── dashboard/
│   │   ├── strategies/components/
│   │   │   └── PublishContentModal.tsx    ← MODIFY: Enable Meta, image warning
│   │   │
│   │   └── settings/components/
│   │       ├── SocialConnections.tsx      ← MODIFY: Add page selection
│   │       └── MetaPageSelector.tsx       ← NEW: Facebook Page picker
```

---

## 🔨 IMPLEMENTATION PLAN

### Phase 1: Meta OAuth Service (60 mins)

**Step 1.1: Add Meta Config**
- `app/core/config.py` already has Meta credentials
- Verify `META_APP_ID`, `META_APP_SECRET`, `META_REDIRECT_URI`

**Step 1.2: Create OAuth Service**
- Create `app/services/oauth_meta.py`
- Implement:
  - `get_authorization_url()` - Build OAuth URL with scopes
  - `exchange_code_for_token()` - Get short-lived token
  - `get_long_lived_token()` - Exchange for 60-day token
  - `get_user_pages()` - Fetch user's Facebook Pages
  - `get_page_access_token()` - Get never-expiring Page token
  - `get_instagram_account()` - Get linked Instagram Business account
  - `get_user_profile()` - Fetch Facebook user info

**Step 1.3: Add Database Fields**
- Add to `social_accounts` table:
  - `page_id` - Facebook Page ID
  - `page_name` - Facebook Page name
  - `instagram_id` - Instagram Business account ID
  - `instagram_username` - Instagram @username

**Step 1.4: Add OAuth Endpoints**
- Update `app/api/social.py`
- Add `GET /social/meta/auth` - Initiate OAuth
- Add `GET /social/meta/callback` - Handle callback
- Add `POST /social/meta/select-page` - User selects Page
- Add `POST /social/meta/disconnect` - Disconnect account

### Phase 2: Meta Publishing Service (60 mins)

**Step 2.1: Create Publishing Service**
- Create `app/services/publishing_meta.py`
- Implement:
  - `post_to_facebook()` - Post to Facebook Page
  - `post_to_instagram()` - Two-step Instagram publish
  - `create_instagram_container()` - Step 1: Create media
  - `publish_instagram_container()` - Step 2: Publish media
  - `get_instagram_permalink()` - Get post URL

**Step 2.2: Handle Image Requirement**
- Instagram requires image
- Facebook is optional
- Frontend must validate/warn

**Step 2.3: Add Publishing Endpoint**
- Update `app/api/publishing.py`
- Add `POST /publishing/facebook` - Publish to Facebook
- Add `POST /publishing/instagram` - Publish to Instagram
- Handle image validation for Instagram

### Phase 3: Frontend Integration (45 mins)

**Step 3.1: Update Social Connections**
- Modify `SocialConnections.tsx`
- Enable Meta platform card
- Add Page selection UI after OAuth

**Step 3.2: Create Page Selector Component**
- Create `MetaPageSelector.tsx`
- Show list of user's Facebook Pages
- Allow user to select one Page
- Show Instagram status (linked/not linked)

**Step 3.3: Update Publish Modal**
- Modify `PublishContentModal.tsx`
- Enable Facebook and Instagram
- Show image warning for Instagram
- Split Meta into two sub-platforms:
  - Facebook (text + optional image)
  - Instagram (image required)

### Phase 4: Testing & Polish (45 mins)

**Step 4.1: Manual Testing**
- Connect Facebook account
- Select Facebook Page
- Post to Facebook
- Post to Instagram (with image)
- Verify on Facebook/Instagram

**Step 4.2: Error Handling**
- Test without Page selected
- Test Instagram without image
- Test expired token
- Test Page without Instagram

**Step 4.3: Documentation**
- Create session summary
- Document Meta OAuth setup
- Add testing guide

---

## 🧪 TESTING STRATEGY

### Meta Developer Setup

**Prerequisites**:
1. Facebook Developer Account
2. Create Facebook App
3. Add Facebook Login product
4. Configure OAuth redirect URI
5. Request permissions (review process)

**App Dashboard**: https://developers.facebook.com/apps/

**Required Settings**:
- OAuth Redirect URI: `http://localhost:8003/api/v1/social/meta/callback`
- App Mode: Development (for testing)
- Permissions: Request `pages_manage_posts`, `instagram_content_publish`

### Test Scenarios

#### Scenario 1: Connect Facebook Account

**Steps**:
1. Settings → Social Accounts
2. Click "Connect Facebook"
3. Authorize app on Facebook
4. Select permissions
5. Redirected back to Settings
6. See list of Facebook Pages
7. Select a Page
8. If Page has Instagram: See Instagram info

**Expected**:
- ✅ Facebook connected
- ✅ Pages list shown
- ✅ Selected Page stored
- ✅ Instagram account detected (if linked)

#### Scenario 2: Post to Facebook

**Steps**:
1. Dashboard → Content
2. Click "Publish" on content item
3. Select "Facebook" platform
4. Click "Publish to Facebook"
5. Check Facebook Page

**Expected**:
- ✅ Post appears on Facebook Page
- ✅ Content matches
- ✅ Published posts page shows entry
- ✅ Facebook URL saved

#### Scenario 3: Post to Instagram (With Image)

**Steps**:
1. Generate content with image
2. Click "Publish"
3. Select "Instagram"
4. Click "Publish to Instagram"
5. Wait (Instagram is slower)
6. Check Instagram account

**Expected**:
- ✅ Post appears on Instagram
- ✅ Caption matches
- ✅ Image displayed
- ✅ Instagram permalink saved

#### Scenario 4: Instagram Without Image (Error)

**Steps**:
1. Generate text-only content
2. Click "Publish"
3. Select "Instagram"
4. Try to publish

**Expected**:
- ❌ Error: "Instagram requires an image"
- Show warning in modal
- Disable publish button

---

## 💡 META API TIPS

### Token Management

**Token Types**:
1. **User Access Token** (short-lived: 1 hour)
   - Initial token from OAuth
   - Exchange for long-lived ASAP

2. **Long-Lived User Token** (60 days)
   - Exchange short-lived for this
   - Use to get Page tokens

3. **Page Access Token** (never expires!)
   - Get from long-lived user token
   - Store this for publishing
   - Each Page has separate token

**Best Practice**: Always use Page Access Tokens for publishing.

### Facebook vs Instagram Posting

| Feature | Facebook | Instagram |
|---------|----------|-----------|
| Text-only | ✅ Yes | ❌ No |
| Image | Optional | **Required** |
| Character Limit | 63,206 | 2,200 |
| Link Preview | ✅ Yes | ❌ No |
| Publishing Speed | Instant | 15-30 sec delay |
| API Calls | 1 | 2 (create + publish) |

### Common Errors

| Error | Cause | Solution |
|-------|-------|---------|
| `(#200) Requires pages_manage_posts permission` | Missing scope | Re-authenticate with correct scopes |
| `(#100) Invalid image URL` | Image not accessible | Use public HTTPS URL |
| `(#190) This account doesn't have an Instagram account` | No Instagram linked | Link Instagram to Facebook Page |
| `(#368) Action not allowed` | Not Page admin | Verify Page access |

---

## 🚨 CHALLENGES & SOLUTIONS

### Challenge 1: Page Selection

**Problem**: User may have multiple Facebook Pages  
**Solution**: Show Page picker after OAuth, store selected Page ID

```python
# After OAuth, get Pages
pages = await meta_oauth.get_user_pages(user_token)

# User selects one Page
selected_page = pages[0]  # User choice via UI
page_id = selected_page["id"]
page_token = selected_page["access_token"]

# Store Page token for publishing
account.platform_user_id = page_id
account.access_token = encrypt_token(page_token)
```

### Challenge 2: Instagram Business Requirement

**Problem**: Can only post to Instagram Business accounts  
**Solution**: Check if Page has Instagram linked, show status in UI

```python
# Check for Instagram Business account
response = await client.get(
    f"https://graph.facebook.com/v18.0/{page_id}",
    params={
        "fields": "instagram_business_account",
        "access_token": page_token
    }
)

if "instagram_business_account" in response:
    ig_id = response["instagram_business_account"]["id"]
    # Store IG ID, enable Instagram publishing
else:
    # Show "Link Instagram" message
```

### Challenge 3: Image Requirement for Instagram

**Problem**: Instagram requires image, but AI content is text  
**Solution**: 
- Frontend validation: Show warning if no image
- Backend: Return error if Instagram + no image
- Future: Auto-generate image from text (Session 12)

### Challenge 4: Instagram Publishing Delay

**Problem**: Instagram takes 15-30 seconds to publish  
**Solution**:
- Show loading state in UI
- Use async/await properly
- Consider background job (future)

---

## 📊 META ECOSYSTEM SUMMARY

### Platform Hierarchy

```
Facebook Personal Account (User)
    ↓
Facebook Pages (Business)
    ├─ Page 1 → Page Access Token 1
    │   ├─ Instagram Business 1 (optional)
    │   └─ Facebook Posts
    │
    ├─ Page 2 → Page Access Token 2
    │   ├─ Instagram Business 2 (optional)
    │   └─ Facebook Posts
    │
    └─ Page 3 → Page Access Token 3
        └─ Facebook Posts
```

### Authentication Flow

```
1. User → Facebook Login (OAuth)
2. Get short-lived token (1 hour)
3. Exchange for long-lived token (60 days)
4. Get user's Facebook Pages
5. User selects a Page
6. Get Page Access Token (never expires!)
7. Check if Page has Instagram linked
8. Store tokens → Ready to publish!
```

### Publishing Decision Tree

```
User wants to publish
    ↓
Has Facebook Page connected?
    No → Show "Connect Facebook" message
    Yes ↓
        
Select platform:
    ↓
Facebook?
    → Use Page Access Token
    → POST to /{page-id}/feed
    → Instant publish
    → Success!
    
Instagram?
    ↓
Has Instagram linked to Page?
    No → Show "Link Instagram" message
    Yes ↓
        
Has image?
    No → Show error: "Instagram requires image"
    Yes ↓
        
    → Step 1: Create container
    → Step 2: Publish container
    → Wait 15-30 seconds
    → Get permalink
    → Success!
```

---

## 🎨 UI MOCKUPS

### Page Selection Flow

**After OAuth Success**:
```
┌────────────────────────────────────────────────────┐
│  Select Facebook Page                        [X]   │
├────────────────────────────────────────────────────┤
│                                                    │
│  Choose which Facebook Page to use for posting:   │
│                                                    │
│  ○ Acme Corporation                                │
│    123,456 followers                               │
│    ✓ Instagram: @acmecorp                         │
│                                                    │
│  ○ Jane's Coffee Shop                             │
│    5,432 followers                                 │
│    ⚠ No Instagram linked                          │
│                                                    │
│  ○ Tech Startup Hub                               │
│    89,012 followers                                │
│    ✓ Instagram: @techstartuphub                   │
│                                                    │
│           [Cancel]           [Confirm]            │
│                                                    │
└────────────────────────────────────────────────────┘
```

### Instagram Image Warning

**In Publish Modal**:
```
┌────────────────────────────────────────────────────┐
│  Publish Content                             [X]   │
├────────────────────────────────────────────────────┤
│                                                    │
│  Platform: Instagram ✓                            │
│                                                    │
│  ⚠️ Instagram requires an image                    │
│  This content has no image attached.              │
│                                                    │
│  Options:                                         │
│  • Add an image to this content                   │
│  • Generate image from text (AI)                  │
│  • Select Facebook instead                        │
│                                                    │
│  [Go Back]              [Add Image]               │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## 📈 SUCCESS CRITERIA

### Must Have (MVP)
- ✅ User can connect Facebook account via OAuth 2.0
- ✅ User can select a Facebook Page
- ✅ User can post text to Facebook Page
- ✅ User can post image + text to Instagram (if linked)
- ✅ Posts appear on Facebook/Instagram
- ✅ Post URLs saved for reference
- ✅ Long-lived tokens stored (60 days)
- ✅ Page tokens stored (never expire)

### Nice to Have (Future)
- ⏳ Auto-generate images for Instagram (Session 12)
- ⏳ Facebook image posts (with image upload)
- ⏳ Instagram carousel posts (multiple images)
- ⏳ Instagram Reels (video)
- ⏳ Facebook video posts
- ⏳ Story posting (Facebook/Instagram)
- ⏳ Engagement metrics (likes, comments, shares)

---

## 🔗 API ENDPOINTS SUMMARY

### OAuth Endpoints

**GET /api/v1/social/meta/auth**
- Initiate Meta OAuth flow
- Query: `business_id`
- Response: Redirect to Facebook

**GET /api/v1/social/meta/callback**
- Handle OAuth callback
- Query: `code`, `state`
- Response: Redirect to Page selection

**POST /api/v1/social/meta/select-page**
- User selects Facebook Page
- Body: `{ "business_id": 1, "page_id": "123" }`
- Response: `{ "message": "Page selected" }`

**POST /api/v1/social/meta/disconnect**
- Disconnect Meta account
- Body: `{ "business_id": 1 }`
- Response: `{ "message": "Disconnected" }`

### Publishing Endpoints

**POST /api/v1/publishing/facebook**
- Publish to Facebook Page
- Body: Same as LinkedIn/Twitter
- Response: Post ID and URL

**POST /api/v1/publishing/instagram**
- Publish to Instagram
- Body: Same + `image_url` required
- Response: Media ID and permalink

---

## 📚 RESOURCES

### Meta Developer Documentation
- **Graph API**: https://developers.facebook.com/docs/graph-api
- **Pages API**: https://developers.facebook.com/docs/pages
- **Instagram API**: https://developers.facebook.com/docs/instagram-api
- **OAuth Flow**: https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow

### Testing Tools
- **Graph API Explorer**: https://developers.facebook.com/tools/explorer
- **Access Token Debugger**: https://developers.facebook.com/tools/debug/accesstoken

---

## 🎯 SESSION GOALS RECAP

By end of Session 11, we should have:

1. ✅ **Meta OAuth 2.0 flow** working end-to-end
2. ✅ **Facebook Page selection** UI and logic
3. ✅ **Facebook publishing** to selected Page
4. ✅ **Instagram publishing** (with image requirement)
5. ✅ **Long-lived tokens** stored and managed
6. ✅ **Instagram account detection** for Pages
7. ✅ **Frontend integration** with Meta enabled
8. ✅ **Session documentation** with Meta setup guide

---

## 🚀 GETTING STARTED

### Prerequisites
- ✅ Sessions 8-10 complete (LinkedIn + Twitter working)
- ✅ Backend and frontend servers running
- ✅ Database has social_accounts table

### Meta Developer Setup

**Required Before Coding**:
1. Go to https://developers.facebook.com/apps/
2. Create a new App (Type: Business)
3. Add "Facebook Login" product
4. Configure OAuth settings:
   - Redirect URI: `http://localhost:8003/api/v1/social/meta/callback`
   - Valid OAuth Redirect URIs (also add)
5. Request permissions (App Review):
   - `pages_show_list` - Usually approved instantly
   - `pages_manage_posts` - May require review
   - `instagram_basic` - Usually approved instantly
   - `instagram_content_publish` - May require review
6. Get App ID and App Secret

### Environment Variables

```bash
# Add to backend/.env
META_APP_ID=your_facebook_app_id
META_APP_SECRET=your_facebook_app_secret
META_REDIRECT_URI=http://localhost:8003/api/v1/social/meta/callback
```

**Note**: Meta uses both App ID and App Secret (unlike Twitter PKCE)

---

**Ready to build? Let's start Session 11! 📘**
