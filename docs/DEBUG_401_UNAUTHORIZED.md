# Fix: 401 Unauthorized Error - Debugging Steps

## Current Issue
```
POST http://localhost:8003/api/v1/publishing/twitter 401 (Unauthorized)
```

## Progress Made
1. ✅ Added Clerk `useAuth` import to PublishContentModal
2. ✅ Added `Authorization: Bearer ${token}` header  
3. ⚠️ Now getting 401 instead of 403 (token is being sent, but rejected)

## Root Cause Analysis

The backend is rejecting the Clerk JWT token. Possible reasons:

### 1. Token Format Issue
- **Check**: Frontend might not be getting a valid token
- **Debug**: Added console logs to see token presence

### 2. Backend Token Verification
- **Current State**: Backend has JWT verification **disabled**
- **Code** (`backend/app/core/auth.py` line 29):
  ```python
  decoded = jwt.decode(
      token,
      options={"verify_signature": False}  # TODO: Add proper verification
  )
  ```
- **Issue**: Even with verification disabled, token parsing might fail

### 3. Token Structure
- **Clerk tokens** use specific claim structure
- **Backend expects**: `sub` claim for user ID
- **Need to verify**: Clerk token has correct format

## Debugging Steps (WITH NEW CONSOLE LOGS)

### Step 1: Check Frontend Console
With the new logs added, you should now see:

```javascript
Publishing to platform: twitter
Token present: true  // or false if problem
Business ID: 1
Payload: { business_id: 1, content_text: "..." }
Response status: 401
Response headers: {...}
Error response: { detail: "..." }
```

**What to check**:
- Is `Token present: true`? 
  - ❌ **If false**: Clerk authentication issue (user not signed in)
  - ✅ **If true**: Continue to Step 2

### Step 2: Check Backend Logs
The backend has debug logging enabled. Check terminal where backend is running:

```bash
# In backend terminal, you should see:
DEBUG: get_current_user called with token: eyJhbGciOiJSUzI1NiIsImNhdCI6...
DEBUG: Verifying token: eyJhbGciOiJSUzI1NiIsImNhdCI6...
DEBUG: Token decoded successfully: {'sub': 'user_33pfWO1feUWrBkOkuQNamIxuXwF', ...}
# OR
DEBUG: Invalid token error: ...
```

**What error do you see?**

### Step 3: Check Clerk Token in Browser
1. Open browser DevTools → Application → Local Storage
2. Find `clerk-db-jwt` or similar
3. Copy the token value
4. Go to https://jwt.io
5. Paste token and decode

**Check**:
- Does it have a `sub` claim?
- Does it have an `exp` (expiration) claim?
- Is it expired?

## Quick Fixes

### Fix Option 1: Refresh Browser (Simple)
```bash
1. Hard refresh browser: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
2. Try publishing again
```

**Why this works**: Clerk might have cached an expired token.

### Fix Option 2: Sign Out and Sign Back In
```bash
1. Click Sign Out in the app
2. Sign back in
3. Try publishing again
```

**Why this works**: Forces Clerk to issue a fresh token.

### Fix Option 3: Check Backend Response (Already Added)
The new console logs will show the exact error from the backend:
```javascript
console.error('Error response:', errorData);
```

Look for the `detail` field - it will tell you exactly why auth failed.

## Common Error Messages

### "Token has expired"
**Solution**: Sign out and sign back in to get fresh token.

### "Invalid token"
**Causes**:
1. Token format incorrect
2. Token signature invalid
3. Token not from expected Clerk instance

**Solution**: 
```typescript
// Check if getToken() is actually returning a token
const token = await getToken();
console.log('Raw token:', token);
console.log('Token length:', token?.length);
console.log('Token starts with:', token?.substring(0, 10));
```

### "Invalid user data in token"
**Cause**: Token doesn't have `sub` claim.

**Solution**: Check Clerk dashboard - ensure user IDs are being issued.

### "Authentication required. Please sign in."
**Cause**: `getToken()` returned `null`.

**Solution**: User session expired or not authenticated. Sign in again.

## Backend Auth Flow

```
┌───────────────────────────────────────────┐
│ 1. Frontend: Get Token                    │
│    const token = await getToken()         │
│    Check: Is token null?                  │
└─────────────────┬─────────────────────────┘
                  │
                  ↓ Token exists
┌───────────────────────────────────────────┐
│ 2. Frontend: Send Request                 │
│    Authorization: Bearer ${token}         │
└─────────────────┬─────────────────────────┘
                  │
                  ↓
┌───────────────────────────────────────────┐
│ 3. Backend: Extract Token                 │
│    credentials.credentials                │
└─────────────────┬─────────────────────────┘
                  │
                  ↓
┌───────────────────────────────────────────┐
│ 4. Backend: Decode JWT                    │
│    jwt.decode(token, verify=False)        │
│    Check: Does it have 'sub'?             │
└─────────────────┬─────────────────────────┘
                  │
                  ↓ Success
┌───────────────────────────────────────────┐
│ 5. Backend: Return User ID                │
│    return user["sub"]                     │
└───────────────────────────────────────────┘
```

## Next Steps

### Immediate Action:
1. **Refresh the browser** and try publishing again
2. **Check browser console** for the new debug logs
3. **Report back** what you see in the console logs

### What to Report:
```
Token present: [true/false]
Response status: [401/other]
Error response detail: [error message from backend]
```

### Based on Error Message:

**If "Token has expired"**:
→ Sign out and sign back in

**If "Invalid token"**:
→ Check backend terminal for detailed error
→ May need to implement proper Clerk token verification

**If "Invalid user data in token"**:
→ Token missing `sub` claim
→ Check Clerk configuration

**If token is null**:
→ Clerk authentication not working
→ Check Clerk configuration in frontend

## Files Modified (With Debug Logging)

| File | Addition |
|------|----------|
| `PublishContentModal.tsx` | ✅ Console logs before request |
| `PublishContentModal.tsx` | ✅ Console logs for response |
| `PublishContentModal.tsx` | ✅ Better error catching |

## Testing Command

To test auth independently:
```bash
# Get a real Clerk token from browser console:
# Open DevTools → Console → Run:
# await window.Clerk.session.getToken()

# Then test backend:
curl -X POST http://localhost:8003/api/v1/publishing/twitter \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_CLERK_TOKEN_HERE" \
  -d '{
    "business_id": 1,
    "content_text": "Test post"
  }'
```

## Status

✅ **Added debug logging** - Frontend now logs token presence and errors  
⏳ **Waiting for test** - Try publishing and check console logs  
⏳ **Need error details** - Report what error message appears  

## Related Documentation

- **403 Fix**: `docs/FIX_403_PUBLISHING_ERROR.md`
- **OAuth Setup**: `docs/OAUTH_READY_TO_TEST.md`
- **Platform Limits**: `docs/PLATFORM_CONTENT_LIMITS.md`
