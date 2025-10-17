# Social Media API Credentials Template

**Date Started**: October 14, 2025  
**Purpose**: Track credentials as you obtain them during Day 1 setup

---

## 📋 Credentials Checklist

### Meta (Facebook + Instagram)
- [x] Account Created: ✅ October 14, 2025
- [x] App Created: AI Growth Manager
- [x] App ID: `1868636850413828`
- [x] App Secret: `05369794ff5ae3a81ec2089bd3fe0c72`
- [ ] Facebook Login Added: ___________
- [ ] Instagram Graph API Added: ___________
- [ ] OAuth Redirect URI Configured: ___________
- [ ] Test Users Created: ___________

**App Dashboard URL**: https://developers.facebook.com/apps/1868636850413828

### Twitter (X)
- [ ] Developer Account Created: ___________
- [ ] Elevated Access Requested: ___________
- [ ] Project Created: ___________
- [ ] App Created: ___________
- [ ] API Key: `_________________________________`
- [ ] API Secret: `_________________________________`
- [ ] Bearer Token: `_________________________________`
- [ ] Access Token: `_________________________________`
- [ ] Access Token Secret: `_________________________________`
- [ ] OAuth 1.0a Enabled: ___________
- [ ] Callback URL Configured: ___________

**App Dashboard URL**: _________________________________
**Elevated Access Status**: ⏳ Pending / ✅ Approved

### LinkedIn
- [ ] Company Page Created: ___________
- [ ] Company Page URL: _________________________________
- [ ] Developer App Created: ___________
- [ ] Client ID: `_________________________________`
- [ ] Client Secret: `_________________________________`
- [ ] Marketing Developer Platform Requested: ___________
- [ ] OAuth Redirect URI Configured: ___________

**App Dashboard URL**: _________________________________
**MDP Access Status**: ⏳ Pending / ✅ Approved

---

## 📝 Copy-Paste Ready for .env

Once you have all credentials, copy this section and update `backend/.env`:

```bash
# =============================================================================
# SOCIAL MEDIA API CREDENTIALS (Week 3 Day 1)
# =============================================================================

# Meta (Facebook/Instagram)
META_APP_ID=your_app_id_here
META_APP_SECRET=your_app_secret_here
META_REDIRECT_URI=http://localhost:8000/api/oauth/meta/callback

# Twitter (X) - Requires Elevated Access for OAuth
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
TWITTER_REDIRECT_URI=http://localhost:8000/api/oauth/twitter/callback

# LinkedIn - Requires Marketing Developer Platform for publishing
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
LINKEDIN_REDIRECT_URI=http://localhost:8000/api/oauth/linkedin/callback
```

---

## ⚠️ Important Notes

### Security Reminders
- ✅ .env file is in .gitignore (won't be committed)
- ✅ Never share these credentials publicly
- ✅ Save in password manager for backup
- ✅ Rotate credentials if exposed

### Access Levels
- **Twitter**: Elevated Access required for OAuth 1.0a (1-2 week wait)
- **LinkedIn**: Marketing Developer Platform for publishing (few days wait)
- **Meta**: Instant access for development, app review for production

### OAuth Callback URLs
All set to localhost for development:
- Meta: `http://localhost:8000/api/oauth/meta/callback`
- Twitter: `http://localhost:8000/api/oauth/twitter/callback`  
- LinkedIn: `http://localhost:8000/api/oauth/linkedin/callback`

**Production URLs**: Update these when deploying to production!

---

## ✅ Verification Steps

After updating .env, verify each credential:

### 1. Check Backend Loads Config
```bash
cd backend
source venv/bin/activate
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Meta App ID:', os.getenv('META_APP_ID'))"
```

Should print your actual App ID (not placeholder).

### 2. Restart Backend Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
```

Look for successful startup (no errors about missing env vars).

### 3. Test Health Endpoint
```bash
curl http://localhost:8003/health
```

Should return: `{"status":"healthy"}`

---

## 📊 Progress Tracking

### Time Spent
- Meta Setup: _____ minutes
- Twitter Setup: _____ minutes  
- LinkedIn Setup: _____ minutes
- Environment Config: _____ minutes
**Total**: _____ hours

### Status
- [ ] All credentials obtained
- [ ] backend/.env updated
- [ ] Backend server restarted successfully
- [ ] Health check passed
- [ ] WEEK_3_PROGRESS.md updated

---

## 🎯 Next Steps (Tomorrow - Day 2)

Once credentials are saved and backend is running:
1. Implement OAuth flows for each platform
2. Test authentication with real credentials
3. Store OAuth tokens in database

**But first**: Complete credential collection today! 🚀

---

## 🚨 Troubleshooting

### Common Issues

**Backend won't start after adding credentials**
```bash
# Check for syntax errors in .env
cat backend/.env | grep "="
# Look for missing quotes, extra spaces, or line breaks
```

**Can't find a credential**
- Go back to the platform's developer dashboard
- Meta: developers.facebook.com/apps → Your App → Settings → Basic
- Twitter: developer.twitter.com → Projects & Apps → Your App → Keys and tokens
- LinkedIn: developer.linkedin.com → My Apps → Your App → Auth

**Credential not working**
- Regenerate the secret/token in the dashboard
- Update .env with new value
- Restart backend server

---

## 💾 Backup Strategy

Save credentials in multiple secure locations:

1. **Password Manager** (recommended)
   - 1Password, LastPass, Bitwarden, etc.
   - Create secure note: "AI Growth Manager - Social Media API Keys"

2. **Encrypted File** (backup)
   - Create encrypted zip: `zip -e credentials_backup.zip CREDENTIALS_TEMPLATE.md`
   - Password protect it
   - Store in secure location (not in git repo)

3. **Platform Dashboards** (source of truth)
   - Meta: developers.facebook.com/apps
   - Twitter: developer.twitter.com/en/portal/dashboard
   - LinkedIn: developer.linkedin.com/console

---

## 📅 Timeline

**9:00 AM**: Start Meta setup  
**10:00 AM**: Start Twitter setup  
**11:00 AM**: Break  
**11:15 AM**: Start LinkedIn setup  
**12:30 PM**: Lunch  
**1:30 PM**: Update .env file  
**2:00 PM**: Test configuration  
**2:30 PM**: Update progress docs  
**3:00 PM**: Day 1 complete! 🎉

---

**Pro Tip**: Take screenshots of each dashboard after setup. Visual reference helps later!

**Remember**: These credentials are the foundation for OAuth implementation tomorrow. Take your time to get them right! 💪
