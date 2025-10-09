# 🚀 Quick Start Guide - Test Your App NOW!

**Session 4 Complete!** Time to test the full-stack application.

---

## ⚡ Quick Start (5 Minutes)

### Step 1: Start Docker Desktop
1. Open Docker Desktop application
2. Wait for it to start (whale icon in menu bar)
3. Ensure it says "Docker is running"

### Step 2: Start Backend Services
```bash
cd /Users/olaoluwabayomi/Desktop/growth/solodev/04_MY_PROJECTS/active/ai-growth-manager

# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Verify they're running
docker-compose ps
```

You should see:
- ✅ postgres (healthy)
- ✅ redis (healthy)

### Step 3: Set Up Backend Python Environment
```bash
cd backend

# Create virtual environment (first time only)
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt
```

### Step 4: Run Database Migrations
```bash
# Still in backend directory with venv activated

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration to create tables
alembic upgrade head
```

You should see: `Running upgrade -> xxxxx, Initial migration`

### Step 5: Start Backend API
```bash
# Still in backend directory

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend is running at: http://localhost:8000
API Docs: http://localhost:8000/docs

### Step 6: Start Frontend (New Terminal)
```bash
cd /Users/olaoluwabayomi/Desktop/growth/solodev/04_MY_PROJECTS/active/ai-growth-manager/frontend

npm run dev
```

Frontend is running at: http://localhost:3000

---

## 🧪 Test the Complete Flow

### 1. Open the App
Visit: http://localhost:3000

You should see the beautiful landing page.

### 2. Sign Up
1. Click "Get Started" button
2. Enter your email and create a password
3. Verify your email if prompted

### 3. Complete Onboarding
**Step 1 - Business Info:**
- Business Name: "Test Business"
- Description: "We help small businesses grow with AI"

**Step 2 - Target Audience:**
- "Small business owners who struggle with marketing"

**Step 3 - Marketing Goals:**
- "Increase brand awareness and generate more leads"

### 4. Click "Get Started"
- You'll see a loading spinner
- Data is being saved to PostgreSQL
- Redirects to dashboard

### 5. Verify Dashboard
You should see:
- ✅ Sidebar navigation
- ✅ Your profile (UserButton)
- ✅ Stats cards (all showing 0 for now)
- ✅ "Getting Started" guide

---

## ✅ Verify Data Was Saved

### Option 1: Check via Database
```bash
# In a new terminal
docker exec -it ai-growth-manager-postgres-1 psql -U postgres -d aigrowth

# View users
SELECT * FROM users;

# View businesses  
SELECT * FROM businesses;

# Exit
\q
```

You should see:
- **users table**: Your Clerk ID and email
- **businesses table**: "Test Business" with your info

### Option 2: Check via API
```bash
# Get user info (replace TOKEN with your Clerk token)
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get businesses
curl http://localhost:8000/api/v1/businesses/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎉 Success Indicators

If everything worked:
- ✅ Frontend loads at localhost:3000
- ✅ Backend API at localhost:8000
- ✅ Can sign up with Clerk
- ✅ Onboarding form works
- ✅ Loading state appears on submit
- ✅ Redirects to dashboard
- ✅ Data appears in PostgreSQL
- ✅ No errors in browser console
- ✅ No errors in backend terminal

---

## 🐛 Troubleshooting

### "Docker daemon not running"
```bash
# Start Docker Desktop app
open -a Docker

# Wait 30 seconds, then try again
docker-compose up -d postgres redis
```

### "Port 8000 already in use"
```bash
# Find and kill the process
lsof -i :8000
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

### "Module not found" errors
```bash
# Make sure venv is activated
source backend/venv/bin/activate

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### "Authentication failed"
- Check that Clerk keys are in `frontend/.env.local`
- Restart Next.js dev server
- Clear browser cookies and try again

### "Database connection error"
```bash
# Restart PostgreSQL
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

---

## 📊 What You've Built

After successful testing, you have:
1. ✅ **Full-stack SaaS application**
2. ✅ **Authentication system** (Clerk)
3. ✅ **Beautiful UI** (Next.js + TailwindCSS)
4. ✅ **REST API** (FastAPI)
5. ✅ **Database** (PostgreSQL with migrations)
6. ✅ **Data persistence** (Onboarding → DB)

**Total Build Time**: 8.5 hours
**Lines of Code**: ~3,000+
**Files Created**: 80+
**Completion**: 22% overall, 95% Week 1

---

## 🎯 Next Steps

Once testing is successful:

### Immediate:
- ✅ Confirm data saves to database
- ✅ Test sign out and sign in again
- ✅ Verify dashboard persists business info

### Session 5 (Next):
1. **AI Strategy Generation**:
   - Build strategy generation API endpoint
   - Integrate OpenRouter/OpenAI
   - Create prompt templates
   - Display strategies in dashboard

2. **Strategy Management**:
   - List all strategies
   - View strategy details
   - Edit/regenerate strategies
   - Approve strategies for content generation

---

## 📸 Screenshot Checklist

Capture these for your portfolio:
- [ ] Landing page
- [ ] Sign up flow
- [ ] Onboarding wizard (all 3 steps)
- [ ] Dashboard with stats
- [ ] PostgreSQL data (terminal)
- [ ] API docs (localhost:8000/docs)

---

**You're ready to test! Follow the steps above and watch your app come to life!** 🚀

If you encounter any issues, check SESSION_4_SUMMARY.md or backend/README.md for detailed troubleshooting.
