# 🚀 Railway Deployment Guide

## Step 1: Deploy Backend to Railway

### 1. Sign Up / Log In to Railway
1. Go to https://railway.app
2. Click "Login" and sign in with GitHub
3. Authorize Railway to access your GitHub account

### 2. Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose `CyberDexa/AiGrowth_Manager`
4. Select the `main` branch

### 3. Configure Backend Service
1. Railway will detect your `backend` folder
2. Click on the backend service
3. Go to **Settings** tab
4. Set **Root Directory**: `backend`
5. Set **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 4. Add Environment Variables
Click **Variables** tab and add these:

```bash
# Clerk Authentication
CLERK_PUBLISHABLE_KEY=pk_test_cm9tYW50aWMtbGVtbWluZy0xNy5jbGVyay5hY2NvdW50cy5kZXYk
CLERK_SECRET_KEY=sk_test_IYi8davr1REqY9mH8bWssAzkJVFiamHa3dFUrMaJy2

# Database (Railway will provide PostgreSQL)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis (Railway will provide Redis)
REDIS_URL=${{Redis.REDIS_URL}}

# API Keys
OPENROUTER_API_KEY=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

# Cloudinary
CLOUDINARY_CLOUD_NAME=duug4mfug
CLOUDINARY_API_KEY=476553972927743
CLOUDINARY_API_SECRET=dnmBE2ojsMWjLkDEP5BOEnUUrrY

# Twitter OAuth
TWITTER_CLIENT_ID=SlBMYmQxQnpocXQzeDBYaVdpY2c6MTpjaQ
TWITTER_CLIENT_SECRET=Cxv7LiqEz0ejZO75ty4fVaTVWo6OghTKu7nfRvb5s5KQgcP4aD
TWITTER_REDIRECT_URI=https://your-app.railway.app/api/v1/oauth/twitter/callback

# Meta OAuth
META_APP_ID=4284592478453354
META_APP_SECRET=4d236810aab33cf822fa89e9490f1303
META_REDIRECT_URI=https://your-app.railway.app/api/v1/oauth/meta/callback

# LinkedIn OAuth
LINKEDIN_CLIENT_ID=77ftqu4rb7v7r2
LINKEDIN_CLIENT_SECRET=<YOUR_LINKEDIN_SECRET>
LINKEDIN_REDIRECT_URI=https://your-app.railway.app/api/v1/oauth/linkedin/callback

# Environment
ENVIRONMENT=production
FRONTEND_URL=http://localhost:3000
```

**Note:** Replace `your-app` with your actual Railway domain once deployed!

### 5. Add PostgreSQL Database
1. Click "New" in your project
2. Select "Database" → "PostgreSQL"
3. Railway will automatically set `DATABASE_URL` variable

### 6. Add Redis (Optional but Recommended)
1. Click "New" in your project
2. Select "Database" → "Redis"
3. Railway will automatically set `REDIS_URL` variable

### 7. Deploy!
1. Railway will automatically build and deploy
2. Wait for deployment to complete (~3-5 minutes)
3. Click on your backend service
4. Go to **Settings** → **Networking**
5. Click "Generate Domain"
6. Copy your Railway URL (e.g., `https://aigrowth-production.up.railway.app`)

---

## Step 2: Update OAuth Redirect URIs

Once you have your Railway URL, update these:

### Twitter Developer Portal
1. Go to https://developer.twitter.com/en/portal/apps
2. Select your app
3. Go to Settings → User authentication settings
4. Update Redirect URI: `https://your-app.railway.app/api/v1/oauth/twitter/callback`
5. Save

### Meta App Dashboard
1. Go to https://developers.facebook.com/apps
2. Select your app (4284592478453354)
3. Go to Settings → Basic
4. Update Valid OAuth Redirect URIs: `https://your-app.railway.app/api/v1/oauth/meta/callback`
5. Save

### LinkedIn Developer Portal
1. Go to https://www.linkedin.com/developers/apps
2. Select your app
3. Go to Auth tab
4. Update Redirect URLs: `https://your-app.railway.app/api/v1/oauth/linkedin/callback`
5. Save

---

## Step 3: Update Frontend Environment

In `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=https://your-app.railway.app
```

Restart your frontend:
```bash
cd frontend
npm run dev
```

---

## Step 4: Test OAuth Flow

1. Go to **Settings → Social Accounts** in your app
2. Click **Connect** for Twitter
3. Complete OAuth flow
4. Verify token is saved
5. Test publishing a post!

---

## Troubleshooting

### Deployment Fails
- Check Railway logs: Click service → "View Logs"
- Common issues:
  * Missing environment variables
  * Wrong root directory (should be `backend`)
  * Missing `requirements.txt`

### OAuth Callbacks Fail
- Ensure redirect URIs match exactly
- Check Railway URL is correct (no trailing slash)
- Verify all OAuth provider settings are updated

### Database Connection Issues
- Ensure PostgreSQL service is running
- Check `DATABASE_URL` is set correctly
- Railway auto-connects services

---

## Next Steps

1. ✅ Deploy backend to Railway
2. ✅ Add database and Redis
3. ✅ Configure environment variables
4. ✅ Update OAuth redirect URIs
5. ✅ Test OAuth connections
6. ✅ Publish your first post!

**Estimated Time**: 20-30 minutes

---

## Railway Free Tier Limits

- ✅ 500 hours/month (enough for 24/7 operation)
- ✅ 1GB RAM
- ✅ 1GB storage
- ✅ PostgreSQL included
- ✅ Custom domain support

Perfect for development and MVP testing!
