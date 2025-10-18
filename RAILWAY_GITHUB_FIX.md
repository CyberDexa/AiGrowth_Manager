# Railway GitHub Integration Fix

## Problem: Repositories Not Showing Up in Railway

If you've signed in to Railway with GitHub but can't see your repositories, follow these steps:

---

## Solution 1: Grant Railway Access to Your Repositories

### Step 1: Check GitHub Permissions
1. Go to https://github.com/settings/installations
2. Find "Railway" in the list of installed apps
3. Click **Configure** next to Railway
4. Scroll to **Repository access**
5. Select one of these options:
   - **All repositories** (easiest - gives Railway access to everything)
   - **Only select repositories** → Click "Select repositories" → Choose `AiGrowth_Manager`
6. Click **Save**

### Step 2: Refresh Railway
1. Go back to Railway (https://railway.app)
2. Click **New Project**
3. Click **Deploy from GitHub repo**
4. Your repositories should now appear!

---

## Solution 2: Reconnect GitHub Account

If repositories still don't show:

1. Go to Railway **Account Settings**: https://railway.app/account
2. Scroll to **Connected Accounts**
3. Click **Disconnect** next to GitHub
4. Click **Connect GitHub** again
5. Authorize Railway with the permissions it requests
6. Grant access to `AiGrowth_Manager` repository

---

## Solution 3: Use Direct Deploy Link

If the above doesn't work, use Railway's direct deploy feature:

### Option A: Deploy Button (Easiest)
1. Go to your GitHub repo: https://github.com/CyberDexa/AiGrowth_Manager
2. Add this button to your README (optional):
   ```markdown
   [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/CyberDexa/AiGrowth_Manager)
   ```
3. Click the button to deploy

### Option B: Manual URL
1. Go directly to: https://railway.app/new
2. Paste your repo URL: `https://github.com/CyberDexa/AiGrowth_Manager`
3. Click "Deploy"

---

## Solution 4: Deploy Using Railway CLI (Alternative)

If web interface still has issues, use the CLI:

### Install Railway CLI
```bash
brew install railway
```

### Deploy Your App
```bash
# Navigate to your project
cd /Users/olaoluwabayomi/Desktop/growth/solodev/04_MY_PROJECTS/active/ai-growth-manager

# Login to Railway
railway login

# Link to your project (or create new one)
railway init

# Deploy
railway up
```

---

## Verify Deployment is Working

Once you can see your repo in Railway:

1. **Select Repository**: Choose `CyberDexa/AiGrowth_Manager`
2. **Railway will detect**:
   - `backend/` folder with Python
   - `frontend/` folder with Node.js
3. **Configure Backend Service**:
   - Root Directory: `backend`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Add Environment Variables** (copy from `backend/.env`)
5. **Add PostgreSQL Database** (click "New" → "Database" → "PostgreSQL")
6. **Deploy!**

---

## Common Issues & Fixes

### Issue: "No repositories found"
**Fix**: Grant Railway access to repositories in GitHub settings (Solution 1)

### Issue: "Repository access denied"
**Fix**: Reconnect GitHub account (Solution 2)

### Issue: "Deploy failed - no buildpack detected"
**Fix**: Ensure `backend/requirements.txt` exists in your repo

### Issue: "Port binding error"
**Fix**: Make sure start command uses `$PORT` variable:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## Next Steps After Deployment

1. ✅ Get your Railway URL (e.g., `https://aigrowth-production.up.railway.app`)
2. ✅ Update OAuth redirect URIs in Twitter/Meta/LinkedIn dashboards
3. ✅ Update `backend/.env` REDIRECT_URI variables with Railway URL
4. ✅ Update `frontend/.env.local` with `NEXT_PUBLIC_API_URL=https://your-railway-url`
5. ✅ Redeploy if needed: `railway up` or push to GitHub
6. ✅ Test OAuth connections
7. ✅ Publish your first post!

---

## Support

If you're still stuck:
1. Check Railway status: https://status.railway.app
2. Railway Discord: https://discord.gg/railway
3. Or use the Railway CLI method (Solution 4) which bypasses web UI issues

---

## Quick Start with Railway CLI

```bash
# Install
brew install railway

# Navigate to project
cd /Users/olaoluwabayomi/Desktop/growth/solodev/04_MY_PROJECTS/active/ai-growth-manager

# Login
railway login

# Create new project
railway init

# Deploy backend
cd backend
railway up

# Get your URL
railway domain
```

Your app will be deployed and you'll get a permanent URL!
