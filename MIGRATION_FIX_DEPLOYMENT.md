# Fix: Auto-Run Database Migrations on Render

## Problem Solved
✅ Render free tier doesn't allow Shell access  
✅ Database migrations weren't running automatically  
✅ `images` table was missing from production database

## Solution
Created a startup script that **automatically runs migrations** every time the backend deploys.

---

## What Changed

### 1. Created `backend/start.sh`
A startup script that:
- Runs `alembic upgrade head` (applies all pending migrations)
- Then starts the Uvicorn server

### 2. Updated `backend/Dockerfile`
Changed the CMD to use the startup script instead of running uvicorn directly.

**Before:**
```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**After:**
```dockerfile
RUN chmod +x start.sh
CMD ["./start.sh"]
```

---

## How to Deploy This Fix

### Step 1: Commit and Push Changes

```bash
cd /Users/olaoluwabayomi/Desktop/growth/solodev/04_MY_PROJECTS/active/ai-growth-manager

# Add the new files
git add backend/start.sh backend/Dockerfile

# Commit
git commit -m "feat: auto-run database migrations on startup

- Add start.sh script to run alembic migrations before server starts
- Update Dockerfile to use startup script
- Fixes missing images table in production database
- Works with Render free tier (no shell access needed)"

# Push to trigger Render deployment
git push origin main
```

### Step 2: Wait for Render to Deploy

1. **Render will automatically detect the push**
2. **It will rebuild the Docker image** with the new startup script
3. **On startup, migrations will run** before the server starts
4. **The `images` table will be created** automatically

### Step 3: Monitor the Deployment

In Render Dashboard:
1. Go to your service logs
2. Look for these messages:
   ```
   🚀 Starting AI Growth Manager Backend...
   📊 Running database migrations...
   Running upgrade ... -> 8aedf3a5c925, add_images_table
   ✅ Migrations complete!
   🌐 Starting Uvicorn server...
   ```

### Step 4: Test Image Upload

Once deployed:
1. Go to your frontend (http://localhost:3001)
2. Try uploading an image
3. It should work! ✅

---

## Benefits

✅ **Automatic migrations** - No manual intervention needed  
✅ **Works on free tier** - No shell access required  
✅ **Safe** - Uses `alembic upgrade head` which is idempotent  
✅ **Future-proof** - All future migrations will auto-apply on deploy

---

## How It Works on Every Deploy

```
1. Render detects code push
2. Builds new Docker image
3. Starts container
4. start.sh runs:
   a. alembic upgrade head ← Creates missing tables
   b. uvicorn app.main:app ← Starts API server
5. Backend is ready with latest database schema!
```

---

## Verification After Deploy

Test the images endpoint:

```bash
curl https://ai-growth-manager.onrender.com/api/v1/images?business_id=1
```

**Before fix:** 500 error "relation 'images' does not exist"  
**After fix:** 200 response (even if empty list)

---

## Troubleshooting

### If migrations fail during startup:

**Check Render logs** for the error message. Common issues:

1. **Database connection issue**
   - Verify `DATABASE_URL` environment variable is set in Render
   
2. **Migration conflict**
   - May need to manually mark problematic migrations as applied
   - Would require Render support or paid tier for shell access

3. **Startup timeout**
   - If migrations take too long, Render might timeout
   - Usually not an issue for small migration sets

### If images still don't work:

1. Check that the deploy completed successfully
2. Verify the startup logs show "✅ Migrations complete!"
3. Test the API directly with curl
4. Check browser console for actual error message

---

## Next Steps

After deploying this fix:

1. ✅ Image uploads will work
2. ✅ All future migrations will auto-apply
3. ✅ No more manual database management needed

**Just push code and Render handles the rest!** 🚀

---

**Created:** November 8, 2025  
**Status:** Ready to deploy  
**Impact:** Fixes image upload in production
