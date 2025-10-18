# 🚀 Railway Web Deployment - Step by Step

## ✅ You've Already Done:
1. ✅ Pushed code to GitHub: https://github.com/CyberDexa/AiGrowth_Manager
2. ✅ Logged into Railway: https://railway.app
3. ✅ Selected workspace: "cyberdexa's Projects"

---

## 🎯 Next Steps (Web Interface - Easier!)

### Step 1: Create Project from GitHub Repo

Since Railway can't see your repos, let's use the **direct deploy method**:

1. Go to: https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. If repos still don't show, click **"Configure GitHub App"**
   - This opens: https://github.com/settings/installations
   - Find "Railway" → Click "Configure"
   - Grant access to **"AiGrowth_Manager"** repository
   - Save and go back to Railway

4. **Select your repo**: `CyberDexa/AiGrowth_Manager`
5. Railway will scan and detect your project

### Step 2: Configure Backend Service

Railway will create a service. Configure it:

1. **Click on the backend service card**
2. **Settings tab**:
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. **Save changes**

### Step 3: Add PostgreSQL Database

1. In your Railway project dashboard, click **"+ New"**
2. Select **"Database"**
3. Choose **"Add PostgreSQL"**
4. Railway auto-connects it to your service (sets DATABASE_URL)

### Step 4: Add Environment Variables

Click **"Variables"** tab and add these one by one:

```bash
CLERK_PUBLISHABLE_KEY=pk_test_cm9tYW50aWMtbGVtbWluZy0xNy5jbGVyay5hY2NvdW50cy5kZXYk
CLERK_SECRET_KEY=sk_test_IYi8davr1REqY9mH8bWssAzkJVFiamHa3dFUrMaJy2
OPENROUTER_API_KEY=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
CLOUDINARY_CLOUD_NAME=duug4mfug
CLOUDINARY_API_KEY=476553972927743
CLOUDINARY_API_SECRET=dnmBE2ojsMWjLkDEP5BOEnUUrrY
TWITTER_CLIENT_ID=SlBMYmQxQnpocXQzeDBYaVdpY2c6MTpjaQ
TWITTER_CLIENT_SECRET=Cxv7LiqEz0ejZO75ty4fVaTVWo6OghTKu7nfRvb5s5KQgcP4aD
META_APP_ID=4284592478453354
META_APP_SECRET=4d236810aab33cf822fa89e9490f1303
LINKEDIN_CLIENT_ID=77ftqu4rb7v7r2
ENVIRONMENT=production
```

**Note**: Don't add `DATABASE_URL` - Railway sets this automatically when you add PostgreSQL!

**You'll need to update these AFTER deployment (once you get your Railway URL)**:
```bash
TWITTER_REDIRECT_URI=https://YOUR-APP.railway.app/api/v1/oauth/twitter/callback
META_REDIRECT_URI=https://YOUR-APP.railway.app/api/v1/oauth/meta/callback
LINKEDIN_REDIRECT_URI=https://YOUR-APP.railway.app/api/v1/oauth/linkedin/callback
FRONTEND_URL=http://localhost:3000
```

### Step 5: Generate Domain

1. Go to **"Settings"** → **"Networking"**
2. Click **"Generate Domain"**
3. Copy your Railway URL (e.g., `https://ai-growth-manager-production.up.railway.app`)

### Step 6: Update Redirect URIs

Now that you have your Railway URL, update:

1. **Back in Railway Variables tab**, update:
   ```
   TWITTER_REDIRECT_URI=https://your-actual-url.railway.app/api/v1/oauth/twitter/callback
   META_REDIRECT_URI=https://your-actual-url.railway.app/api/v1/oauth/meta/callback
   LINKEDIN_REDIRECT_URI=https://your-actual-url.railway.app/api/v1/oauth/linkedin/callback
   ```

2. **Update OAuth Providers**:
   - **Twitter**: https://developer.twitter.com/en/portal/apps
   - **Meta**: https://developers.facebook.com/apps
   - **LinkedIn**: https://www.linkedin.com/developers/apps

### Step 7: Deploy!

Railway will automatically deploy when you:
- Push to GitHub (automatic redeployment)
- Or click **"Deploy"** button in Railway dashboard

---

## 📝 Troubleshooting GitHub Integration

If Railway still can't see your repos:

### Option A: Grant Repository Access
1. Go to: https://github.com/settings/installations
2. Find "Railway" in installed apps
3. Click **"Configure"**
4. Under "Repository access":
   - Select **"Only select repositories"**
   - Click **"Select repositories"**
   - Choose `AiGrowth_Manager`
   - Click **"Save"**
5. Refresh Railway page

### Option B: Use Template Deploy
1. Add this to your GitHub repo README.md:
   ```markdown
   [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template)
   ```
2. Click the button
3. Follow Railway's template setup

### Option C: Manual Git Push (Advanced)
If web interface fails completely:
```bash
cd backend
railway link  # Link to existing project
railway up    # Deploy directly
```

---

## ✅ Verification Checklist

After deployment:
- [ ] Backend is deployed and shows "Active"
- [ ] PostgreSQL database is connected
- [ ] All environment variables are set
- [ ] Domain is generated
- [ ] Redirect URIs updated in Railway
- [ ] OAuth providers updated with Railway URL
- [ ] Test endpoint: `https://your-url.railway.app/health`
- [ ] Should return: `{"status":"healthy","environment":"production"}`

---

## 🎉 Success! What's Next?

Once deployed:
1. Update `frontend/.env.local`:
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-url.railway.app
   ```
2. Go to Settings → Social Accounts
3. Connect Twitter, Meta, LinkedIn
4. Test publishing!

---

## Need Help?

If you're stuck at any step, let me know where you're at and I'll help you through it!

**Current Status**: Waiting for you to create project in Railway web interface.
