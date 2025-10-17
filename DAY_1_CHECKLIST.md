# Day 1 Simple Checklist ✅

**Print this or keep it visible!**

---

## Meta Developer Account (45-60 min)
- [ ] Go to https://developers.facebook.com
- [ ] Create app "AI Growth Manager" (Business type)
- [ ] Add Facebook Login product
- [ ] Add Instagram Graph API product
- [ ] Copy App ID → Save it
- [ ] Copy App Secret → Save it
- [ ] Configure OAuth redirect: `http://localhost:8000/api/oauth/meta/callback`
- [ ] Create 2-3 test users

**App ID**: `_________________________________`  
**App Secret**: `_________________________________`

---

## Twitter Developer Account (45-60 min)
- [ ] Go to https://developer.twitter.com
- [ ] Apply for developer account
- [ ] ⚠️ **REQUEST ELEVATED ACCESS** (CRITICAL!)
- [ ] Create project "AI Growth Manager"
- [ ] Create app "AI Growth Manager App"
- [ ] Enable OAuth 1.0a (Read and Write)
- [ ] Copy API Key → Save it
- [ ] Copy API Secret → Save it
- [ ] Copy Bearer Token → Save it
- [ ] Copy Access Token → Save it
- [ ] Copy Access Token Secret → Save it
- [ ] Configure callback: `http://localhost:8000/api/oauth/twitter/callback`

**API Key**: `_________________________________`  
**API Secret**: `_________________________________`  
**Bearer Token**: `_________________________________`  
**Access Token**: `_________________________________`  
**Access Token Secret**: `_________________________________`

---

## LinkedIn Developer Account (60-90 min)
- [ ] Create company page at https://linkedin.com/company/setup/new
  - Name: "AI Growth Manager"
  - Industry: Software Development
- [ ] Go to https://developer.linkedin.com
- [ ] Create app "AI Growth Manager"
- [ ] Link to company page
- [ ] Request Marketing Developer Platform access
- [ ] Copy Client ID → Save it
- [ ] Copy Client Secret → Save it
- [ ] Configure OAuth redirect: `http://localhost:8000/api/oauth/linkedin/callback`

**Client ID**: `_________________________________`  
**Client Secret**: `_________________________________`

---

## Update Environment (15-30 min)
- [ ] Open `backend/.env`
- [ ] Update `META_APP_ID=` with your App ID
- [ ] Update `META_APP_SECRET=` with your App Secret
- [ ] Update `TWITTER_API_KEY=` with your API Key
- [ ] Update `TWITTER_API_SECRET=` with your API Secret
- [ ] Add `TWITTER_BEARER_TOKEN=` (new line)
- [ ] Add `TWITTER_ACCESS_TOKEN=` (new line)
- [ ] Add `TWITTER_ACCESS_TOKEN_SECRET=` (new line)
- [ ] Update `LINKEDIN_CLIENT_ID=` with your Client ID
- [ ] Update `LINKEDIN_CLIENT_SECRET=` with your Client Secret
- [ ] Save file
- [ ] Restart backend: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8003`
- [ ] Test: `curl http://localhost:8003/health`

---

## Final Steps
- [ ] Update `CREDENTIALS_TEMPLATE.md` with all credentials
- [ ] Update `WEEK_3_PROGRESS.md` with completion
- [ ] Note any blockers or issues
- [ ] Celebrate! 🎉

---

## Success = 
✅ All credentials obtained  
✅ Backend running with new config  
✅ Health check passing  
✅ Twitter Elevated Access requested  
✅ Documentation updated

---

**Time Started**: _________  
**Time Completed**: _________  
**Total Hours**: _________

**Issues Encountered**: 
_____________________________________________________________
_____________________________________________________________
_____________________________________________________________

**Notes**: 
_____________________________________________________________
_____________________________________________________________
_____________________________________________________________
