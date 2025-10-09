# 🔌 API Integration Requirements & Documentation

*Complete guide to all third-party API integrations for AI Growth Manager*

**Last Updated**: October 9, 2025
**Status**: Planning Phase

---

## 📋 Table of Contents

1. [OpenAI / OpenRouter (AI Content Generation)](#1-openai--openrouter)
2. [Meta (Facebook & Instagram)](#2-meta-facebook--instagram)
3. [Twitter / X](#3-twitter--x)
4. [LinkedIn](#4-linkedin)
5. [Stripe (Payments)](#5-stripe)
6. [Clerk (Authentication)](#6-clerk)
7. [PostHog (Analytics)](#7-posthog)
8. [Resend (Email)](#8-resend)
9. [Buffer / Hootsuite (Backup Option)](#9-buffer--hootsuite-backup)

---

## 1. OpenAI / OpenRouter

### Purpose
Generate marketing strategies, social media content, ad copy, and optimize campaigns

### API Choice: OpenRouter (Primary) → OpenAI Direct (Backup)

#### Why OpenRouter First?
- Access to multiple LLMs (GPT-4, Claude, Gemini)
- Competitive pricing
- Built-in fallback logic
- Simple API (OpenAI-compatible)

### Authentication
```python
# Environment Variables
OPENROUTER_API_KEY=sk-or-v1-...
OPENAI_API_KEY=sk-...  # Backup
```

### Key Endpoints

#### 1. Strategy Generation
```python
POST https://openrouter.ai/api/v1/chat/completions

# Request
{
  "model": "openai/gpt-4o",
  "messages": [
    {
      "role": "system",
      "content": "You are an expert marketing strategist..."
    },
    {
      "role": "user",
      "content": "Create a marketing strategy for: [business description]"
    }
  ],
  "max_tokens": 2000,
  "temperature": 0.7
}

# Expected Response Structure
{
  "id": "gen-...",
  "model": "openai/gpt-4o",
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "## Marketing Strategy\n\n### Target Audience\n..."
    }
  }],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 500,
    "total_tokens": 650
  }
}
```

#### 2. Content Generation
```python
POST https://openrouter.ai/api/v1/chat/completions

# Request for batch content generation
{
  "model": "openai/gpt-4o-mini",  # Cheaper for content
  "messages": [
    {
      "role": "system",
      "content": "You are a social media content creator..."
    },
    {
      "role": "user",
      "content": "Generate 7 LinkedIn posts about [topic] for [audience]"
    }
  ],
  "max_tokens": 1500,
  "temperature": 0.8
}
```

### Rate Limits
| Plan | Requests/Min | Tokens/Min | Cost |
|------|--------------|------------|------|
| OpenRouter Free | 20 | ~20k | Pay per use |
| OpenRouter Pro | 3,500 | ~90k | Pay per use |
| OpenAI Tier 1 | 500 | 30k | Pay per use |
| OpenAI Tier 2 | 5,000 | 450k | Pay per use |

### Pricing (Per 1M Tokens)
| Model | Input | Output | Use Case |
|-------|-------|--------|----------|
| GPT-4o | $2.50 | $10.00 | Strategy, long content |
| GPT-4o-mini | $0.15 | $0.60 | Social posts, quick gen |
| Claude Sonnet | $3.00 | $15.00 | Alternative for variety |

### Cost Estimates
**Per User Per Month**:
- Strategy generation: 1x/month × 2k tokens × $0.01 = **$0.02**
- Content generation: 30 posts × 500 tokens × $0.0006 = **$0.09**
- Optimization/rewrites: 10x × 300 tokens × $0.0006 = **$0.02**
- **Total per user**: ~$0.13/month

**For 100 users**: ~$13/month
**For 1,000 users**: ~$130/month

### Implementation Notes
- ✅ Use `gpt-4o-mini` for all social content (90% cheaper)
- ✅ Use `gpt-4o` only for strategy and complex analysis
- ✅ Implement response caching (Redis) for repeated requests
- ✅ Add retry logic with exponential backoff
- ✅ Set max_tokens limits to control costs
- ✅ Log all API usage for cost tracking

### Error Handling
```python
Common Errors:
- 429: Rate limit exceeded → Retry with backoff
- 401: Invalid API key → Check environment variables
- 500: OpenAI server error → Fallback to backup model
- 400: Invalid request → Validate input before sending
```

---

## 2. Meta (Facebook & Instagram)

### Purpose
Post content to Facebook Pages and Instagram Business accounts

### API Version
**Graph API v19.0** (current as of Oct 2025)

### Prerequisites
- Facebook Developer account
- App created in Meta for Developers
- Business verification (for Instagram)
- App review for permissions (if posting on behalf of users)

### Required Permissions
- `pages_show_list` - List Pages user manages
- `pages_read_engagement` - Read Page engagement data
- `pages_manage_posts` - Create, edit, delete posts
- `instagram_basic` - Basic Instagram access
- `instagram_content_publish` - Publish Instagram content
- `pages_read_user_content` - Read user content on Page

### Authentication Flow

#### 1. OAuth 2.0 Flow
```python
# Step 1: Redirect user to Facebook OAuth
https://www.facebook.com/v19.0/dialog/oauth?
  client_id={app-id}&
  redirect_uri={redirect-uri}&
  scope=pages_show_list,pages_manage_posts,instagram_content_publish

# Step 2: Exchange code for access token
POST https://graph.facebook.com/v19.0/oauth/access_token?
  client_id={app-id}&
  client_secret={app-secret}&
  redirect_uri={redirect-uri}&
  code={authorization-code}

# Response
{
  "access_token": "EAAxxxxxxx",
  "token_type": "bearer",
  "expires_in": 5184000  # 60 days
}

# Step 3: Get long-lived token (60 days)
GET https://graph.facebook.com/v19.0/oauth/access_token?
  grant_type=fb_exchange_token&
  client_id={app-id}&
  client_secret={app-secret}&
  fb_exchange_token={short-lived-token}

# Step 4: Get Page access token (never expires if user token is valid)
GET https://graph.facebook.com/v19.0/me/accounts?
  access_token={user-access-token}

# Response
{
  "data": [{
    "access_token": "EAAxxxPage",  # Store this!
    "category": "Business",
    "name": "My Business Page",
    "id": "123456789",
    "tasks": ["ANALYZE", "ADVERTISE", "MODERATE", "CREATE_CONTENT"]
  }]
}
```

### Key Endpoints

#### 1. Post to Facebook Page
```python
POST https://graph.facebook.com/v19.0/{page-id}/feed

# Request
{
  "message": "Check out our latest product!",
  "link": "https://example.com",  # Optional
  "published": true,  # false for draft
  "scheduled_publish_time": 1234567890,  # Unix timestamp for scheduling
  "access_token": "EAAxxxPage"
}

# Response
{
  "id": "123456789_987654321"  # page-id_post-id
}
```

#### 2. Post to Instagram
```python
# Step 1: Create media container
POST https://graph.facebook.com/v19.0/{instagram-account-id}/media

{
  "image_url": "https://example.com/image.jpg",  # Or video_url
  "caption": "Amazing content! #hashtags",
  "access_token": "EAAxxxPage"
}

# Response
{
  "id": "creation-id-123"
}

# Step 2: Publish the container
POST https://graph.facebook.com/v19.0/{instagram-account-id}/media_publish

{
  "creation_id": "creation-id-123",
  "access_token": "EAAxxxPage"
}

# Response
{
  "id": "instagram-media-id-456"
}
```

#### 3. Get Post Insights (Analytics)
```python
GET https://graph.facebook.com/v19.0/{post-id}/insights?
  metric=post_impressions,post_clicks,post_reactions_by_type_total&
  access_token={page-token}

# Response
{
  "data": [{
    "name": "post_impressions",
    "period": "lifetime",
    "values": [{"value": 1234}]
  }, {
    "name": "post_clicks",
    "period": "lifetime",
    "values": [{"value": 56}]
  }]
}
```

### Rate Limits
| Limit Type | Value |
|------------|-------|
| App-level calls | 200 calls/user/hour |
| Page posts | Unlimited |
| Instagram posts | 25 posts/day per account |
| Video uploads | 100 videos/day |

### Error Codes
```python
Common Errors:
- 190: Access token expired → Refresh token
- 200: Permission denied → Request additional permissions
- 368: Temporarily blocked for posting too fast → Implement delay
- 100: Invalid parameter → Validate media URL/format
```

### Implementation Notes
- ✅ Store page access tokens securely (encrypted in DB)
- ✅ Refresh user tokens before expiry (implement webhook)
- ✅ Handle Instagram 2-step publishing (container → publish)
- ✅ Validate image URLs are publicly accessible
- ✅ Implement retry logic for failed posts
- ✅ Queue posts to avoid hitting rate limits

### Testing
- Use **Meta Graph API Explorer** for testing
- Create test pages/accounts for development
- Use sandbox mode during development

---

## 3. Twitter / X

### Purpose
Post tweets and threads on behalf of users

### API Version
**Twitter API v2** (OAuth 2.0)

### Prerequisites
- Twitter Developer account
- Create Project and App
- Elevated access (for OAuth 2.0 with write permissions)

### Required Scopes
- `tweet.read` - Read tweets
- `tweet.write` - Create, delete tweets
- `users.read` - Read user profile
- `offline.access` - Refresh tokens

### Authentication Flow (OAuth 2.0 PKCE)

```python
# Step 1: Generate PKCE challenge
import hashlib, base64, secrets

code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode('utf-8')).digest()
).decode('utf-8')

# Step 2: Redirect user to Twitter
https://twitter.com/i/oauth2/authorize?
  response_type=code&
  client_id={client-id}&
  redirect_uri={redirect-uri}&
  scope=tweet.read%20tweet.write%20users.read%20offline.access&
  state={random-state}&
  code_challenge={code-challenge}&
  code_challenge_method=S256

# Step 3: Exchange code for token
POST https://api.twitter.com/2/oauth2/token

# Body (application/x-www-form-urlencoded)
{
  "code": "{authorization-code}",
  "grant_type": "authorization_code",
  "client_id": "{client-id}",
  "redirect_uri": "{redirect-uri}",
  "code_verifier": "{code-verifier}"
}

# Response
{
  "token_type": "bearer",
  "expires_in": 7200,
  "access_token": "VGhpcyBpcxxxxxx",
  "scope": "tweet.read tweet.write users.read offline.access",
  "refresh_token": "bWlUdjQtYxxxxx"
}

# Step 4: Refresh token (every 2 hours)
POST https://api.twitter.com/2/oauth2/token

{
  "refresh_token": "{refresh-token}",
  "grant_type": "refresh_token",
  "client_id": "{client-id}"
}
```

### Key Endpoints

#### 1. Create Tweet
```python
POST https://api.twitter.com/2/tweets

# Headers
Authorization: Bearer {access-token}
Content-Type: application/json

# Request
{
  "text": "Hello Twitter! This is a test tweet from AI Growth Manager. 🚀"
}

# Response
{
  "data": {
    "id": "1234567890123456789",
    "text": "Hello Twitter! This is a test tweet..."
  }
}
```

#### 2. Create Thread
```python
# Tweet 1
POST https://api.twitter.com/2/tweets
{
  "text": "Thread time! 1/3\n\nHere's an interesting topic..."
}
# Response: {"data": {"id": "tweet-1-id"}}

# Tweet 2 (reply to tweet 1)
POST https://api.twitter.com/2/tweets
{
  "text": "2/3\n\nContinuing the thought...",
  "reply": {
    "in_reply_to_tweet_id": "tweet-1-id"
  }
}

# Tweet 3 (reply to tweet 2)
POST https://api.twitter.com/2/tweets
{
  "text": "3/3\n\nAnd that's a wrap! 🎬",
  "reply": {
    "in_reply_to_tweet_id": "tweet-2-id"
  }
}
```

#### 3. Tweet with Media
```python
# Step 1: Upload media (v1.1 API)
POST https://upload.twitter.com/1.1/media/upload.json

# multipart/form-data
{
  "media": <binary-file-data>
}

# Response
{
  "media_id": 123456789,
  "media_id_string": "123456789"
}

# Step 2: Create tweet with media
POST https://api.twitter.com/2/tweets
{
  "text": "Check out this image!",
  "media": {
    "media_ids": ["123456789"]
  }
}
```

#### 4. Get Tweet Metrics
```python
GET https://api.twitter.com/2/tweets/{tweet-id}?
  tweet.fields=public_metrics,created_at

# Response
{
  "data": {
    "id": "1234567890",
    "text": "Tweet content...",
    "public_metrics": {
      "retweet_count": 12,
      "reply_count": 5,
      "like_count": 34,
      "quote_count": 2,
      "impression_count": 567  # Requires elevated access
    },
    "created_at": "2025-10-09T10:00:00.000Z"
  }
}
```

### Rate Limits
| Endpoint | User Context | App Context |
|----------|--------------|-------------|
| POST /tweets | 50 tweets / 24 hours | N/A |
| POST /tweets (same text) | 1 per 24 hours | N/A |
| GET /tweets/:id | 900 / 15 min | 300 / 15 min |
| Media upload | 1 every 5 seconds | N/A |

### Character Limits
- Standard tweet: 280 characters
- Twitter Blue (paid): 4,000 characters
- URL: Counts as 23 characters (t.co short link)

### Error Codes
```python
Common Errors:
- 401: Unauthorized → Check access token
- 403: Forbidden → Missing permissions or duplicate tweet
- 429: Rate limit exceeded → Wait and retry
- 187: Duplicate status → Same tweet posted recently
```

### Implementation Notes
- ✅ Store refresh tokens securely (encrypted)
- ✅ Auto-refresh access tokens (every 2 hours)
- ✅ Respect rate limits (50 tweets/day per user)
- ✅ Validate character count before posting
- ✅ Handle thread creation sequentially (wait for each reply)
- ✅ Implement duplicate tweet detection

### Testing
- Use Twitter **Postman collection** for API testing
- Test with personal Twitter account first

---

## 4. LinkedIn

### Purpose
Post content to personal profiles and company pages

### API Version
**LinkedIn Marketing API v2**

### Prerequisites
- LinkedIn Developer account
- Create LinkedIn App
- Verify app for production use

### Required Permissions
- `r_liteprofile` - Read basic profile
- `r_emailaddress` - Read email
- `w_member_social` - Post on behalf of user
- `r_organization_social` - Read company page data (for company posting)
- `w_organization_social` - Post to company pages

### Authentication Flow (OAuth 2.0)

```python
# Step 1: Redirect user to LinkedIn
https://www.linkedin.com/oauth/v2/authorization?
  response_type=code&
  client_id={client-id}&
  redirect_uri={redirect-uri}&
  scope=r_liteprofile%20r_emailaddress%20w_member_social%20w_organization_social

# Step 2: Exchange code for access token
POST https://www.linkedin.com/oauth/v2/accessToken

# Body (application/x-www-form-urlencoded)
{
  "grant_type": "authorization_code",
  "code": "{authorization-code}",
  "client_id": "{client-id}",
  "client_secret": "{client-secret}",
  "redirect_uri": "{redirect-uri}"
}

# Response
{
  "access_token": "AQXdSP_xxxxxxxW",
  "expires_in": 5184000,  # 60 days
  "refresh_token": "AQXdSP_refreshxxx",  # If requested
  "refresh_token_expires_in": 31536000  # 1 year
}

# Step 3: Get user profile (for person URN)
GET https://api.linkedin.com/v2/me

# Headers
Authorization: Bearer {access-token}

# Response
{
  "id": "abc123XYZ",
  "firstName": {
    "localized": {"en_US": "John"}
  },
  "lastName": {
    "localized": {"en_US": "Doe"}
  }
}
# Person URN: urn:li:person:abc123XYZ
```

### Key Endpoints

#### 1. Create Post (Personal Profile)
```python
POST https://api.linkedin.com/v2/ugcPosts

# Headers
Authorization: Bearer {access-token}
Content-Type: application/json
X-Restli-Protocol-Version: 2.0.0

# Request
{
  "author": "urn:li:person:abc123XYZ",
  "lifecycleState": "PUBLISHED",
  "specificContent": {
    "com.linkedin.ugc.ShareContent": {
      "shareCommentary": {
        "text": "Excited to share our latest product update! 🚀\n\n#ProductLaunch #SaaS"
      },
      "shareMediaCategory": "NONE"  # or "ARTICLE", "IMAGE"
    }
  },
  "visibility": {
    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
  }
}

# Response
{
  "id": "urn:li:share:6890123456789",
  "author": "urn:li:person:abc123XYZ",
  "created": {
    "time": 1633024800000
  }
}
```

#### 2. Post with Article/Link
```python
POST https://api.linkedin.com/v2/ugcPosts

{
  "author": "urn:li:person:abc123XYZ",
  "lifecycleState": "PUBLISHED",
  "specificContent": {
    "com.linkedin.ugc.ShareContent": {
      "shareCommentary": {
        "text": "Must-read article on AI and marketing automation"
      },
      "shareMediaCategory": "ARTICLE",
      "media": [{
        "status": "READY",
        "description": {
          "text": "How AI is transforming marketing"
        },
        "originalUrl": "https://example.com/article",
        "title": {
          "text": "AI Marketing Revolution"
        }
      }]
    }
  },
  "visibility": {
    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
  }
}
```

#### 3. Post to Company Page
```python
# First, get organization URN
GET https://api.linkedin.com/v2/organizationAcls?
  q=roleAssignee&
  role=ADMINISTRATOR&
  projection=(elements*(organization~(localizedName)))

# Response
{
  "elements": [{
    "organization": "urn:li:organization:123456",
    "organization~": {
      "localizedName": "My Company"
    }
  }]
}

# Then post as organization
POST https://api.linkedin.com/v2/ugcPosts

{
  "author": "urn:li:organization:123456",  # Changed from person
  "lifecycleState": "PUBLISHED",
  "specificContent": {
    "com.linkedin.ugc.ShareContent": {
      "shareCommentary": {
        "text": "Company announcement: We're hiring! 🎉"
      },
      "shareMediaCategory": "NONE"
    }
  },
  "visibility": {
    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
  }
}
```

#### 4. Get Post Analytics
```python
GET https://api.linkedin.com/v2/socialActions/{share-urn}

# Response
{
  "likes": {
    "paging": {...},
    "total": 45
  },
  "comments": {
    "paging": {...},
    "total": 12
  }
}

# For detailed metrics (requires organization access)
GET https://api.linkedin.com/v2/organizationalEntityShareStatistics?
  q=organizationalEntity&
  organizationalEntity=urn:li:organization:123456&
  timeIntervals=(timeRange:(start:1633024800000,end:1633628800000))

# Response
{
  "elements": [{
    "totalShareStatistics": {
      "shareCount": 23,
      "likeCount": 156,
      "engagement": 0.034,
      "clickCount": 89,
      "impressionCount": 4567,
      "commentCount": 34
    }
  }]
}
```

### Rate Limits
| Endpoint | Limit |
|----------|-------|
| POST /ugcPosts | 100 posts / day |
| GET /me | 60,000 / 24 hours |
| GET /organizationAcls | 60,000 / 24 hours |

### Text Limits
- Post text: 3,000 characters
- Article description: 256 characters
- Hashtags: Recommended 3-5 per post

### Error Codes
```python
Common Errors:
- 401: Unauthorized → Invalid/expired token
- 403: Forbidden → Missing permissions
- 429: Too many requests → Rate limited
- 422: Validation failed → Check request format
```

### Implementation Notes
- ✅ Store access tokens (60-day expiry)
- ✅ Implement token refresh logic
- ✅ Support both personal and company posts
- ✅ Validate character limits
- ✅ Handle media uploads separately (2-step process)
- ✅ Respect posting limits (100/day)

### Testing
- Use LinkedIn **API Console** for testing
- Test with personal profile first, then company pages

---

## 5. Stripe

### Purpose
Handle subscription billing, payments, and customer management

### API Version
**Stripe API v2023-10-16**

### Required Setup
- Stripe account (test + production keys)
- Products and Prices created in dashboard
- Webhook endpoint configured

### Authentication
```python
# Environment Variables
STRIPE_SECRET_KEY=sk_test_xxxxx  # Test
STRIPE_SECRET_KEY=sk_live_xxxxx  # Production
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

### Product/Price Structure

```python
# Create Products (one-time setup in Stripe Dashboard)
Products:
1. "AI Growth Manager - Free"
   - Price: $0/month
   - Features: 10 posts/month, 1 platform

2. "AI Growth Manager - Pro"
   - Price: $29/month or $290/year (save $58)
   - Features: Unlimited posts, 3 platforms, analytics

3. "AI Growth Manager - Enterprise"
   - Price: $99/month or $990/year
   - Features: Everything + team features, API access
```

### Key Flows

#### 1. Create Customer on Signup
```python
import stripe
stripe.api_key = "sk_test_xxxxx"

# When user signs up (via Clerk webhook)
customer = stripe.Customer.create(
    email="user@example.com",
    name="John Doe",
    metadata={
        "clerk_user_id": "user_xxxxx",
        "source": "webapp"
    }
)

# Store customer.id in your database
# customer.id = "cus_xxxxx"
```

#### 2. Create Checkout Session (Subscribe)
```python
POST https://api.stripe.com/v1/checkout/sessions

# Request
{
  "customer": "cus_xxxxx",  # From step 1
  "success_url": "https://app.example.com/success?session_id={CHECKOUT_SESSION_ID}",
  "cancel_url": "https://app.example.com/pricing",
  "mode": "subscription",
  "line_items": [{
    "price": "price_pro_monthly_xxxxx",  # Pro plan price ID
    "quantity": 1
  }],
  "subscription_data": {
    "trial_period_days": 14,  # 14-day free trial
    "metadata": {
      "plan": "pro",
      "user_id": "user_xxxxx"
    }
  }
}

# Response
{
  "id": "cs_test_xxxxx",
  "url": "https://checkout.stripe.com/c/pay/cs_test_xxxxx"
}

# Redirect user to session.url
```

#### 3. Handle Webhook Events
```python
POST {your-domain}/api/webhooks/stripe

# Verify webhook signature
payload = request.body
sig_header = request.headers['Stripe-Signature']

try:
    event = stripe.Webhook.construct_event(
        payload, sig_header, STRIPE_WEBHOOK_SECRET
    )
except ValueError:
    return 400  # Invalid payload
except stripe.error.SignatureVerificationError:
    return 400  # Invalid signature

# Handle events
if event.type == 'checkout.session.completed':
    session = event.data.object
    # Activate subscription in your DB
    
elif event.type == 'customer.subscription.updated':
    subscription = event.data.object
    # Update subscription status
    
elif event.type == 'customer.subscription.deleted':
    subscription = event.data.object
    # Downgrade user to free plan
    
elif event.type == 'invoice.payment_failed':
    invoice = event.data.object
    # Send payment failed email
    
return 200
```

#### 4. Customer Portal (Manage Subscription)
```python
POST https://api.stripe.com/v1/billing_portal/sessions

# Request
{
  "customer": "cus_xxxxx",
  "return_url": "https://app.example.com/settings/billing"
}

# Response
{
  "id": "bps_xxxxx",
  "url": "https://billing.stripe.com/session/xxxxx"
}

# Redirect user to session.url
# They can cancel, upgrade, update payment method
```

#### 5. Check Subscription Status
```python
GET https://api.stripe.com/v1/subscriptions/{subscription-id}

# Response
{
  "id": "sub_xxxxx",
  "status": "active",  # or "trialing", "past_due", "canceled"
  "current_period_end": 1735689600,
  "items": {
    "data": [{
      "price": {
        "id": "price_pro_monthly_xxxxx",
        "unit_amount": 2900,  # $29.00
        "recurring": {
          "interval": "month"
        }
      }
    }]
  }
}
```

### Essential Webhook Events
| Event | When it fires | Action |
|-------|---------------|--------|
| `checkout.session.completed` | User completes checkout | Activate subscription |
| `customer.subscription.created` | New subscription | Store subscription ID |
| `customer.subscription.updated` | Plan change | Update user plan |
| `customer.subscription.deleted` | Subscription canceled | Downgrade to free |
| `invoice.payment_succeeded` | Successful payment | Log payment |
| `invoice.payment_failed` | Failed payment | Send reminder email |

### Usage-Based Billing (Future)
```python
# If implementing usage-based pricing (e.g., per-post)
stripe.SubscriptionItem.create_usage_record(
    subscription_item_id,
    quantity=10,  # 10 posts generated
    timestamp=int(time.time()),
    action="increment"
)
```

### Rate Limits
- **100 reads/second** per API key
- **100 writes/second** per API key
- No hard daily limit

### Error Codes
```python
Common Errors:
- card_declined: Payment method declined
- expired_card: Card expired
- insufficient_funds: Insufficient funds
- subscription_trial_end_past: Trial end date in past
```

### Implementation Notes
- ✅ Use test mode keys during development
- ✅ Implement webhook signature verification
- ✅ Handle all webhook events asynchronously
- ✅ Store Stripe customer ID and subscription ID in DB
- ✅ Implement idempotency for webhook processing
- ✅ Log all Stripe events for debugging
- ✅ Use Stripe Customer Portal for self-service

### Testing
- Use **Stripe CLI** for webhook testing locally
- Test cards: `4242 4242 4242 4242` (success)
- Test cards: `4000 0000 0000 0002` (declined)

---

## 6. Clerk

### Purpose
User authentication, session management, and user profiles

### API Version
**Clerk Frontend API v1**

### Required Setup
- Clerk account (free tier)
- Application created in Clerk Dashboard
- Environment variables configured

### Authentication
```javascript
// Environment Variables (.env.local)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxx
CLERK_SECRET_KEY=sk_test_xxxxx
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/onboarding
```

### Key Features Used

#### 1. Frontend Setup (Next.js)
```typescript
// app/layout.tsx
import { ClerkProvider } from '@clerk/nextjs'

export default function RootLayout({ children }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  )
}

// app/dashboard/page.tsx (protected route)
import { auth } from '@clerk/nextjs'

export default function Dashboard() {
  const { userId } = auth()
  
  if (!userId) {
    return redirect('/sign-in')
  }
  
  return <div>Dashboard for {userId}</div>
}
```

#### 2. Backend Setup (FastAPI)
```python
from clerk import Clerk

clerk = Clerk(bearer_auth="sk_test_xxxxx")

# Verify session token from frontend
@app.post("/api/protected")
async def protected_route(
    authorization: str = Header(None)
):
    if not authorization:
        raise HTTPException(401, "Unauthorized")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Verify token with Clerk
        session = clerk.sessions.verify_token(token)
        user_id = session.user_id
        
        # Fetch user details
        user = clerk.users.get(user_id)
        
        return {"user": user}
    except Exception as e:
        raise HTTPException(401, "Invalid token")
```

#### 3. Webhooks (Sync Users to DB)
```python
# FastAPI webhook endpoint
from svix.webhooks import Webhook

@app.post("/api/webhooks/clerk")
async def clerk_webhook(request: Request):
    # Get webhook secret from Clerk Dashboard
    webhook_secret = "whsec_xxxxx"
    
    # Verify webhook signature
    headers = request.headers
    payload = await request.body()
    
    wh = Webhook(webhook_secret)
    
    try:
        evt = wh.verify(payload, headers)
    except Exception as e:
        return {"error": "Invalid signature"}, 400
    
    # Handle events
    event_type = evt["type"]
    
    if event_type == "user.created":
        # Create user in your database
        user_data = evt["data"]
        await create_user_in_db(
            clerk_id=user_data["id"],
            email=user_data["email_addresses"][0]["email_address"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"]
        )
        
        # Create Stripe customer
        stripe_customer = stripe.Customer.create(
            email=user_data["email_addresses"][0]["email_address"],
            metadata={"clerk_user_id": user_data["id"]}
        )
        
        # Update user with Stripe customer ID
        await update_user_stripe_id(
            clerk_id=user_data["id"],
            stripe_customer_id=stripe_customer.id
        )
    
    elif event_type == "user.updated":
        # Update user in database
        pass
    
    elif event_type == "user.deleted":
        # Soft delete or anonymize user
        pass
    
    return {"status": "success"}
```

### Essential Webhook Events
| Event | Action |
|-------|--------|
| `user.created` | Create user in DB + Stripe customer |
| `user.updated` | Update user profile |
| `user.deleted` | Handle account deletion |
| `session.created` | Log user login (optional) |

### User Metadata
```javascript
// Store custom data in Clerk
await clerkClient.users.updateUserMetadata(userId, {
  publicMetadata: {
    plan: "pro",
    onboarding_completed: true
  },
  privateMetadata: {
    stripe_customer_id: "cus_xxxxx",
    internal_notes: "Beta user"
  }
})
```

### Rate Limits
- **Free tier**: 10,000 MAU (Monthly Active Users)
- **Pro tier**: $25/month (from 10k MAU)

### Implementation Notes
- ✅ Use Clerk components for sign-in/sign-up UI
- ✅ Store minimal user data in DB (Clerk is source of truth)
- ✅ Sync users via webhooks (user.created)
- ✅ Use Clerk's middleware for route protection
- ✅ Store Stripe customer ID in Clerk metadata
- ✅ Implement webhook signature verification

---

## 7. PostHog

### Purpose
Product analytics, feature flags, session replay

### API Version
**PostHog Cloud / Self-hosted**

### Setup
```javascript
// Environment Variables
NEXT_PUBLIC_POSTHOG_KEY=phc_xxxxx
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
```

### Frontend Integration (Next.js)
```typescript
// lib/posthog.ts
import posthog from 'posthog-js'

if (typeof window !== 'undefined') {
  posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
    api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST,
    loaded: (posthog) => {
      if (process.env.NODE_ENV === 'development') {
        posthog.debug()
      }
    }
  })
}

export default posthog

// Track events
posthog.capture('content_generated', {
  platform: 'linkedin',
  content_type: 'post',
  word_count: 150
})

// Identify user
posthog.identify(userId, {
  email: user.email,
  plan: user.plan,
  signup_date: user.createdAt
})
```

### Backend Integration (Python)
```python
from posthog import Posthog

posthog = Posthog(
    project_api_key='phc_xxxxx',
    host='https://app.posthog.com'
)

# Track server-side events
posthog.capture(
    distinct_id=user_id,
    event='ai_strategy_generated',
    properties={
        'business_type': 'saas',
        'tokens_used': 1500,
        'model': 'gpt-4o'
    }
)
```

### Key Events to Track
```python
User Journey:
- user_signed_up
- onboarding_started
- onboarding_completed
- business_described
- strategy_generated
- content_generated
- content_scheduled
- content_published
- social_account_connected
- subscription_started
- subscription_upgraded
- subscription_canceled

Feature Usage:
- dashboard_viewed
- analytics_viewed
- settings_changed
- api_called
```

### Feature Flags
```javascript
// Check if feature is enabled
const isNewEditorEnabled = posthog.isFeatureEnabled('new-content-editor')

if (isNewEditorEnabled) {
  return <NewEditor />
} else {
  return <OldEditor />
}
```

### Implementation Notes
- ✅ Track all key user actions
- ✅ Use for A/B testing (feature flags)
- ✅ Enable session replay for debugging
- ✅ Set up conversion funnels
- ✅ Create cohorts for user segmentation

### Rate Limits
- Free tier: 1M events/month
- Paid: $0.00031 per event

---

## 8. Resend

### Purpose
Transactional emails (welcome, password reset, notifications)

### Authentication
```python
# Environment Variable
RESEND_API_KEY=re_xxxxx
```

### Send Email
```python
import resend

resend.api_key = "re_xxxxx"

# Send welcome email
email = resend.Emails.send({
    "from": "AI Growth Manager <hello@aigrowth.app>",
    "to": "user@example.com",
    "subject": "Welcome to AI Growth Manager! 🚀",
    "html": "<h1>Welcome!</h1><p>Let's get started...</p>"
})
```

### Rate Limits
- Free tier: 100 emails/day
- Paid: $20/month for 50k emails

---

## 9. Buffer / Hootsuite (Backup Option)

### Purpose
Backup option if native social APIs are too complex

### Benefits
- Single API for multiple platforms
- Handle rate limiting automatically
- Built-in scheduling

### Drawbacks
- Additional cost (~$15-50/month per user)
- Less control over posting logic
- Vendor dependency

---

## 📊 API Cost Summary (Monthly)

| API | Free Tier | Estimated Cost (100 users) |
|-----|-----------|----------------------------|
| OpenAI / OpenRouter | Pay-per-use | $13-50 |
| Meta API | Free | $0 |
| Twitter API | Free (Elevated) | $0 |
| LinkedIn API | Free | $0 |
| Stripe | Free (2.9% + $0.30) | % of revenue |
| Clerk | 10k MAU | $0 |
| PostHog | 1M events | $0-20 |
| Resend | 100/day | $0-20 |
| **Total** | | **$13-90/month** |

---

## ✅ Next Steps

1. Create developer accounts for all services
2. Set up test applications
3. Store API keys in environment variables
4. Test authentication flows
5. Build API abstraction layer in backend

---

*This document will be updated as we implement each integration.*
