# 🔑 Developer Accounts Setup Guide

**Status**: In Progress
**Last Updated**: October 9, 2025

---

## 📝 Accounts Checklist

### Required Accounts (Priority 1)

#### 1. Clerk (Authentication) 🔐
- [ ] **Sign Up**: https://clerk.com
- [ ] **Create Application**: "AI Growth Manager"
- [ ] **Get API Keys**:
  - Publishable Key: `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
  - Secret Key: `CLERK_SECRET_KEY`
- [ ] **Configure OAuth**:
  - [ ] Enable Google OAuth
  - [ ] Enable LinkedIn OAuth
- [ ] **Set up Webhooks**:
  - Endpoint: `https://your-api.com/api/webhooks/clerk`
  - Events: `user.created`, `user.updated`, `user.deleted`
- [ ] **Test**: Sign up with test account

**Estimated Time**: 15 minutes

---

#### 2. Stripe (Payments) 💳
- [ ] **Sign Up**: https://stripe.com
- [ ] **Activate Test Mode**
- [ ] **Create Products**:
  - [ ] AI Growth Manager - Free ($0/month)
  - [ ] AI Growth Manager - Pro ($29/month)
  - [ ] AI Growth Manager - Enterprise ($99/month)
- [ ] **Get API Keys**:
  - Test Publishable: `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`
  - Test Secret: `STRIPE_SECRET_KEY`
- [ ] **Set up Webhook**:
  - Endpoint: `https://your-api.com/api/webhooks/stripe`
  - Events: Select all subscription & invoice events
  - Secret: `STRIPE_WEBHOOK_SECRET`
- [ ] **Test**: Create test subscription with `4242 4242 4242 4242`

**Estimated Time**: 20 minutes

---

#### 3. OpenRouter (AI) 🤖
- [ ] **Sign Up**: https://openrouter.ai
- [ ] **Add Credits**: Start with $10
- [ ] **Get API Key**: `OPENROUTER_API_KEY`
- [ ] **Test Models**:
  - [ ] Test `openai/gpt-4o-mini` (cheap)
  - [ ] Test `openai/gpt-4o` (quality)
- [ ] **Set up Billing Alerts**: Alert at $5, $10, $20

**Alternative**: OpenAI Direct
- Sign up at https://platform.openai.com
- Get `OPENAI_API_KEY`

**Estimated Time**: 10 minutes

---

#### 4. Meta for Developers (Facebook/Instagram) 📱
- [ ] **Sign Up**: https://developers.facebook.com
- [ ] **Create App**:
  - App Type: "Business"
  - App Name: "AI Growth Manager"
- [ ] **Add Products**:
  - [ ] Facebook Login
  - [ ] Instagram Basic Display
- [ ] **Get Credentials**:
  - App ID: `META_APP_ID`
  - App Secret: `META_APP_SECRET`
- [ ] **Configure OAuth**:
  - Valid OAuth Redirect URIs: `https://your-app.com/api/social/callback/meta`
- [ ] **Request Permissions** (App Review):
  - `pages_show_list`
  - `pages_manage_posts`
  - `instagram_basic`
  - `instagram_content_publish`
- [ ] **Create Test Page**: For development testing
- [ ] **Test**: Connect test page, post test content

**Note**: App review required for production (2-7 days)

**Estimated Time**: 30 minutes

---

#### 5. Twitter Developer (X) 🐦
- [ ] **Apply for Access**: https://developer.twitter.com
- [ ] **Select Access Level**: "Elevated" (free, supports OAuth 2.0)
- [ ] **Create Project & App**:
  - Project: "AI Growth Manager"
  - App: "AI Growth Manager Production"
- [ ] **Get Credentials**:
  - Client ID: `TWITTER_CLIENT_ID`
  - Client Secret: `TWITTER_CLIENT_SECRET`
- [ ] **Configure OAuth 2.0**:
  - Type of App: "Web App"
  - Callback URLs: `https://your-app.com/api/social/callback/twitter`
  - Website URL: `https://your-app.com`
- [ ] **Enable OAuth 2.0** with PKCE
- [ ] **Test**: Post test tweet

**Note**: Approval can take 1-3 days

**Estimated Time**: 20 minutes + wait time

---

#### 6. LinkedIn Developers 💼
- [ ] **Sign Up**: https://www.linkedin.com/developers
- [ ] **Create App**:
  - App Name: "AI Growth Manager"
  - LinkedIn Page: (Create a test company page if needed)
- [ ] **Get Credentials**:
  - Client ID: `LINKEDIN_CLIENT_ID`
  - Client Secret: `LINKEDIN_CLIENT_SECRET`
- [ ] **Configure OAuth**:
  - Redirect URLs: `https://your-app.com/api/social/callback/linkedin`
- [ ] **Request Permissions**:
  - `r_liteprofile`
  - `r_emailaddress`
  - `w_member_social`
  - `w_organization_social`
- [ ] **Verify App**: May require verification for production
- [ ] **Test**: Post test update

**Note**: Some permissions require app verification

**Estimated Time**: 25 minutes

---

### Supporting Accounts (Priority 2)

#### 7. PostHog (Analytics) 📊
- [ ] **Sign Up**: https://posthog.com
- [ ] **Create Project**: "AI Growth Manager"
- [ ] **Get API Key**: `NEXT_PUBLIC_POSTHOG_KEY`
- [ ] **Note Host**: Usually `https://app.posthog.com`
- [ ] **Enable Features**:
  - [ ] Session Recording
  - [ ] Feature Flags
  - [ ] Funnels
- [ ] **Test**: Send test event

**Estimated Time**: 10 minutes

---

#### 8. Resend (Email) 📧
- [ ] **Sign Up**: https://resend.com
- [ ] **Get API Key**: `RESEND_API_KEY`
- [ ] **Add Domain** (later): your-domain.com
- [ ] **Verify Domain** (later)
- [ ] **For now**: Use `onboarding@resend.dev` sender
- [ ] **Test**: Send test email

**Estimated Time**: 5 minutes

---

#### 9. Railway (Backend Hosting) 🚂
- [ ] **Sign Up**: https://railway.app
- [ ] **Connect GitHub**: Link your GitHub account
- [ ] **Create Project**: "AI Growth Manager"
- [ ] **Add Services**:
  - [ ] PostgreSQL (Database)
  - [ ] Redis (Cache)
- [ ] **Note Credentials**: Railway will auto-generate
- [ ] **$5 Free Credit**: Available monthly

**Estimated Time**: 10 minutes

---

#### 10. Vercel (Frontend Hosting) ▲
- [ ] **Sign Up**: https://vercel.com
- [ ] **Connect GitHub**: Link your repository
- [ ] **Note**: Will deploy automatically later
- [ ] **Free Tier**: Unlimited hobby projects

**Estimated Time**: 5 minutes

---

### Optional Accounts

#### 11. Sentry (Error Tracking)
- [ ] Sign up at https://sentry.io
- [ ] Create project
- [ ] Get DSN: `SENTRY_DSN`

#### 12. Figma (Design)
- [ ] Sign up at https://figma.com
- [ ] Free tier available

---

## 🔐 Environment Variables Template

Create this file: `.env.local` (Frontend - Next.js)

```bash
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxx
CLERK_SECRET_KEY=sk_test_xxxxx
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/onboarding

# Stripe
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
# For production: NEXT_PUBLIC_API_URL=https://api.aigrowthmanager.com

# PostHog Analytics
NEXT_PUBLIC_POSTHOG_KEY=phc_xxxxx
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com

# Sentry (Optional)
NEXT_PUBLIC_SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
```

Create this file: `.env` (Backend - FastAPI)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/aigrowth
REDIS_URL=redis://localhost:6379

# Clerk
CLERK_SECRET_KEY=sk_test_xxxxx
CLERK_WEBHOOK_SECRET=whsec_xxxxx

# Stripe
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# AI
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENAI_API_KEY=sk-xxxxx  # Backup

# Social Media APIs
META_APP_ID=xxxxx
META_APP_SECRET=xxxxx
TWITTER_CLIENT_ID=xxxxx
TWITTER_CLIENT_SECRET=xxxxx
LINKEDIN_CLIENT_ID=xxxxx
LINKEDIN_CLIENT_SECRET=xxxxx

# Email
RESEND_API_KEY=re_xxxxx

# Security
ENCRYPTION_KEY=xxxxx  # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
JWT_SECRET=xxxxx  # Generate with: openssl rand -hex 32

# Environment
ENVIRONMENT=development  # development | staging | production
DEBUG=True
```

---

## 📋 Setup Progress Tracker

| Service | Status | API Keys Obtained | Tested | Notes |
|---------|--------|-------------------|--------|-------|
| Clerk | ⏳ Pending | ⬜ | ⬜ | - |
| Stripe | ⏳ Pending | ⬜ | ⬜ | - |
| OpenRouter | ⏳ Pending | ⬜ | ⬜ | - |
| Meta | ⏳ Pending | ⬜ | ⬜ | App review needed |
| Twitter | ⏳ Pending | ⬜ | ⬜ | Elevated access |
| LinkedIn | ⏳ Pending | ⬜ | ⬜ | - |
| PostHog | ⏳ Pending | ⬜ | ⬜ | - |
| Resend | ⏳ Pending | ⬜ | ⬜ | - |
| Railway | ⏳ Pending | ⬜ | ⬜ | - |
| Vercel | ⏳ Pending | ⬜ | ⬜ | - |

**Legend**: ⏳ Pending | 🔄 In Progress | ✅ Complete | ❌ Blocked

---

## 🚨 Common Issues & Solutions

### Issue: Meta App Review Rejected
**Solution**: 
- Use test accounts for development
- Apply for review only when ready for production
- Provide detailed use case and privacy policy

### Issue: Twitter Elevated Access Denied
**Solution**:
- Clearly explain use case in application
- Mention it's for authenticated user's own account
- Reapply with more details if denied

### Issue: LinkedIn Permissions Not Available
**Solution**:
- Some permissions require partner verification
- Use personal profile posting for MVP
- Apply for partnership later if needed

---

## ✅ Next Steps After Setup

1. **Store API keys securely**:
   - Never commit to Git
   - Use `.env` files (add to `.gitignore`)
   - Use environment variable management in production

2. **Test each integration**:
   - Create test script for each API
   - Verify authentication flows
   - Test rate limits

3. **Update documentation**:
   - Mark completed services in tracker
   - Note any issues or workarounds
   - Update cost estimates with actual pricing

---

**Estimated Total Setup Time**: 2-3 hours
**Recommended Approach**: Complete Priority 1 accounts first, then move to implementation

---

*Update this document as you complete each service setup*
