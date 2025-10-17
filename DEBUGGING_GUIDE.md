# "Failed to Fetch" Debugging Guide

## What We Fixed

### 1. Added Trailing Slashes (Required by FastAPI)
**Files Updated:**
- ✅ `frontend/app/dashboard/settings/page.tsx` (line 73)
- ✅ `frontend/app/dashboard/strategies/page.tsx` (line 48)

### 2. Added Debug Logging to Settings Page
Now the console will show:
```
Token exists: true/false
API URL: http://localhost:8003
Fetching from: http://localhost:8003/api/v1/businesses/
Response status: 200/403/500
```

## How to Debug This Error

### Step 1: Check Browser Console (F12)

After refreshing the page, look for these console messages:

#### Scenario A: Token Problem
```
Token exists: false  ← YOU'RE NOT SIGNED IN!
```
**Solution**: Sign in at http://localhost:3000/sign-in

#### Scenario B: Backend Not Running
```
Token exists: true
Fetching from: http://localhost:8003/api/v1/businesses/
Failed to load businesses: TypeError: Failed to fetch
```
**Solution**: Start backend (see below)

#### Scenario C: Backend Returns Error
```
Token exists: true
Response status: 403
API Error: 403 {"detail":"Not authenticated"}
```
**Solution**: Clerk token validation issue (see below)

### Step 2: Verify Backend is Running

```bash
# Test health endpoint
curl http://localhost:8003/health

# Expected: {"status":"healthy","environment":"development"}
# If fails: Backend not running - see "Start Backend" below
```

### Step 3: Test the Actual Endpoint

```bash
# Test without authentication (should return 403)
curl http://localhost:8003/api/v1/businesses/

# Expected: {"detail":"Not authenticated"}
# If fails: Check backend logs
```

## Common Issues & Solutions

### Issue 1: "Token exists: false"
**Problem**: User not signed in to Clerk  
**Solution**:
1. Go to http://localhost:3000/sign-in
2. Sign in or create account
3. Return to dashboard/settings

### Issue 2: Backend Not Running
**Problem**: Port 8003 not responding  
**Solution**:
```bash
cd /Users/olaoluwabayomi/Desktop/growth/solodev/04_MY_PROJECTS/active/ai-growth-manager/backend

# Start backend
/Users/olaoluwabayomi/Desktop/growth/solodev/04_MY_PROJECTS/active/ai-growth-manager/backend/venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8003 --app-dir /Users/olaoluwabayomi/Desktop/growth/solodev/04_MY_PROJECTS/active/ai-growth-manager/backend
```

### Issue 3: NEXT_PUBLIC_API_URL Not Set
**Problem**: Frontend doesn't know where backend is  
**Check**: `frontend/.env.local` should have:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8003
```

### Issue 4: Clerk Token Invalid
**Problem**: Token exists but backend rejects it  
**Symptoms**: Response status 403 even with token  
**Solution**:
1. Check Clerk keys match in both `.env` files:
   - `backend/.env` - `CLERK_SECRET_KEY`
   - `frontend/.env.local` - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
2. Sign out and sign back in
3. Clear browser cookies and try again

### Issue 5: Frontend Not Reloaded
**Problem**: Code changes not applied  
**Solution**:
1. Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
2. Or restart frontend dev server:
   ```bash
   cd frontend
   # Kill existing process (Ctrl+C)
   npm run dev
   ```

## Verification Checklist

Before debugging, verify:

- [ ] Backend running on port 8003
  ```bash
  curl http://localhost:8003/health
  ```

- [ ] Frontend running on port 3000
  ```bash
  curl http://localhost:3000
  ```

- [ ] You are signed in
  - Check navbar for user menu/profile
  - No "Sign In" button visible

- [ ] Browser console open (F12)
  - Check Console tab for debug messages
  - Check Network tab for failed requests

- [ ] `.env.local` has correct API URL
  ```bash
  cat frontend/.env.local | grep API_URL
  # Should show: NEXT_PUBLIC_API_URL=http://localhost:8003
  ```

## Network Tab Investigation

Open Browser DevTools → Network Tab:

### What to Look For

1. **Request sent?**
   - Filter by "businesses"
   - Should see `GET http://localhost:8003/api/v1/businesses/`

2. **Request headers**
   - Click on request
   - Check "Headers" tab
   - Look for: `Authorization: Bearer eyJhbGc...` (long JWT token)
   - If missing → Not signed in

3. **Response**
   - Status: Should be 200 (success) or 403 (auth error)
   - If `ERR_CONNECTION_REFUSED` → Backend not running
   - If `CORS error` → Backend CORS misconfigured (but we verified it's correct)

## Current Status

### ✅ Fixed
1. Backend logging errors
2. Trailing slash in settings page
3. Trailing slash in strategies page
4. Added comprehensive debug logging

### ✅ Verified Working
1. Backend health endpoint
2. Backend businesses endpoint (returns 403 without auth - correct!)
3. CORS configuration
4. API URL in environment variables

### ❓ To Verify
1. **Are you signed in?** → Check navbar
2. **Is frontend showing debug logs?** → Check console
3. **Is backend still running?** → Test curl command

## Next Steps

1. **Refresh browser** (hard refresh: `Cmd+Shift+R`)
2. **Open console** (F12)
3. **Look for debug messages**:
   - "Token exists: true" → Good!
   - "Token exists: false" → Sign in
   - "Failed to fetch" → Check backend running
4. **Report back** with console output

## Quick Test Script

Run this in your terminal:

```bash
#!/bin/bash
echo "=== Backend Health Check ==="
curl -s http://localhost:8003/health
echo -e "\n"

echo "=== Businesses Endpoint (no auth) ==="
curl -s http://localhost:8003/api/v1/businesses/
echo -e "\n"

echo "=== Frontend Running? ==="
curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend running" || echo "❌ Frontend not running"

echo -e "\n=== Backend Running? ==="
curl -s http://localhost:8003/health > /dev/null && echo "✅ Backend running" || echo "❌ Backend not running"

echo -e "\n=== API URL Config ==="
cat frontend/.env.local | grep NEXT_PUBLIC_API_URL
```

Save as `test-connection.sh`, run with `bash test-connection.sh`

---

**What to do now:**
1. Refresh browser (hard refresh)
2. Check console for debug messages
3. Share what you see in the console

The detailed logging will tell us exactly where the issue is!
