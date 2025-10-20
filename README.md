# 🚀 AI Growth Manager

> **Your autonomous AI marketing team that works 24/7**  
> Stop struggling with marketing. Our AI builds strategies, creates content, and runs campaigns automatically so you can focus on building your business.

[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)]()
[![License](https://img.shields.io/badge/License-MIT-blue)]()
[![Version](https://img.shields.io/badge/Version-1.0.0-orange)]()

---

## 📖 Table of Contents

- [Features](#-features)
- [Screenshots](#-screenshots)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Installation](#-installation)
- [Environment Variables](#-environment-variables)
- [Deployment](#-deployment)
- [Project Structure](#-project-structure)
- [Development Workflow](#-development-workflow)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🎯 AI Strategy Generation
Our AI analyzes your business and creates a custom 12-week marketing strategy with content pillars, target audiences, and growth tactics tailored to your industry and goals.

**Key Capabilities:**
- Industry-specific strategy templates
- Competitive analysis insights
- Target audience profiling
- Content pillar recommendations
- 12-week execution timeline

<!-- ![AI Strategy Generation](./screenshots/feature-ai-strategy.png) -->

---

### ✨ AI Content Creation
Generate platform-optimized content in seconds. Our AI adapts content length, style, and hashtags for Twitter, LinkedIn, Facebook, and Instagram automatically.

**Key Capabilities:**
- Platform-specific character limits
- Hashtag and mention formatting
- URL shortening
- Emoji suggestions
- Real-time platform previews

<!-- ![Content Creation](./screenshots/feature-content-creation.png) -->

---

### ⚡ Multi-Platform Publishing
Publish to all your social accounts with one click. Schedule posts or publish immediately to Twitter, LinkedIn, Facebook, and Instagram.

**Key Capabilities:**
- One-click multi-platform publishing
- OAuth authentication for secure connections
- Platform-specific optimization
- Bulk scheduling
- Post status tracking

<!-- ![Multi-Platform Publishing](./screenshots/feature-multi-platform.png) -->

---

### 📝 Content Templates
Create reusable templates for product launches, promotions, announcements, and more. Fill in placeholders and generate consistent content in seconds.

**Key Capabilities:**
- Custom template creation
- Dynamic placeholder system (`{{variable_name}}`)
- Template categories and tags
- One-click content generation
- Template library management

<!-- ![Content Templates](./screenshots/feature-templates.png) -->

---

### 📊 Analytics Dashboard
Track reach, engagement, and growth across all platforms. Beautiful charts show what content performs best and when to post for maximum impact.

**Key Capabilities:**
- Total posts, reach, and engagement metrics
- Growth rate tracking
- Platform-specific performance charts
- Engagement trends over time
- Top-performing content analysis
- Exportable reports

<!-- ![Analytics Dashboard](./screenshots/feature-analytics.png) -->

---

### ⏰ Smart Posting Times
AI analyzes your audience engagement patterns and recommends the best times to post on each platform for maximum reach and interaction.

**Key Capabilities:**
- Platform-specific time recommendations
- Day-of-week optimization
- Confidence scoring (high/medium/low)
- Historical engagement analysis
- "Best time now" indicator
- Customizable posting schedules

<!-- ![Posting Time Recommendations](./screenshots/feature-posting-times.png) -->

---

### 📚 Content Library
Save your best-performing content for reuse. Build a library of proven posts and adapt them for future campaigns.

**Key Capabilities:**
- Save successful content
- Tag and categorize posts
- Search and filter functionality
- One-click republishing
- Performance metrics per item
- Bulk operations

<!-- ![Content Library](./screenshots/feature-content-library.png) -->

---

### 📅 Visual Calendar
See all your scheduled posts at a glance. Drag and drop to reschedule, edit upcoming content, and maintain a consistent posting rhythm.

**Key Capabilities:**
- Month/week/day calendar views
- Drag-and-drop rescheduling
- Color-coded platform indicators
- Inline post editing
- Bulk schedule operations
- Export to iCal/Google Calendar

<!-- ![Scheduled Calendar](./screenshots/feature-calendar.png) -->

---

### ✅ Guided Onboarding
Interactive checklist walks you through setup step-by-step. Connect accounts, create your first strategy, and publish content in under 10 minutes.

**Key Capabilities:**
- 9-step guided setup process
- Progress tracking with confetti celebration
- Contextual help tooltips
- Mobile-responsive design
- Skip and resume functionality
- Completion badges

<!-- ![Guided Onboarding](./screenshots/feature-onboarding.png) -->

---

## 🖼️ Screenshots

> **Note:** Run your local development server and capture screenshots using the guide in `/screenshots/README.md`. Add them here once captured.

### Dashboard Overview
<!-- Add screenshot: ./screenshots/hero-dashboard.png -->

### AI Strategy Builder
<!-- Add screenshot: ./screenshots/feature-ai-strategy.png -->

### Content Creation
<!-- Add screenshot: ./screenshots/feature-content-creation.png -->

### Analytics & Insights
<!-- Add screenshot: ./screenshots/feature-analytics.png -->

### Mobile Experience
<!-- Add screenshots: ./screenshots/mobile-menu.png, ./screenshots/mobile-dashboard.png -->

---

## 🛠️ Tech Stack

### Frontend
- **Framework:** [Next.js 15.5.4](https://nextjs.org/) (React 18)
- **Language:** TypeScript
- **Styling:** [Tailwind CSS](https://tailwindcss.com/)
- **UI Components:** 
  - [Radix UI](https://www.radix-ui.com/) (Tooltips, Modals)
  - [Lucide React](https://lucide.dev/) (Icons)
  - [Recharts](https://recharts.org/) (Analytics Charts)
- **Calendar:** [react-big-calendar](https://jquense.github.io/react-big-calendar/)
- **Notifications:** [react-hot-toast](https://react-hot-toast.com/)
- **Authentication:** [Clerk](https://clerk.com/)
- **State Management:** React Context + Hooks
- **Deployment:** [Vercel](https://vercel.com/)

### Backend
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11)
- **Database:** [PostgreSQL](https://www.postgresql.org/)
- **Cache:** [Redis](https://redis.io/) (with in-memory fallback)
- **ORM:** [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Job Queue:** [Celery](https://docs.celeryq.dev/)
- **AI:** [OpenAI GPT-4](https://openai.com/) (via [OpenRouter](https://openrouter.ai/))
- **OAuth:** LinkedIn, Twitter, Facebook, Instagram APIs
- **Deployment:** [Render](https://render.com/)

### DevOps & Tools
- **Version Control:** Git + GitHub
- **CI/CD:** GitHub Actions (planned)
- **Error Tracking:** Sentry (configured)
- **Monitoring:** Render built-in + Custom logging
- **Package Management:** npm (frontend), pip + venv (backend)

---

## 🚀 Getting Started

### Prerequisites

- **Node.js:** v18.x or higher
- **Python:** 3.11 or higher
- **PostgreSQL:** 14.x or higher
- **Redis:** 6.x or higher (optional, falls back to in-memory)
- **Git:** Latest version

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/CyberDexa/AiGrowth_Manager.git
   cd AiGrowth_Manager
   ```

2. **Set up the backend:**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
   pip install -r requirements.txt
   ```

3. **Set up the frontend:**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Configure environment variables** (see [Environment Variables](#-environment-variables))

5. **Start the development servers:**
   
   **Backend (Terminal 1):**
   ```bash
   cd backend
   source .venv/bin/activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
   ```

   **Celery Worker (Terminal 2):**
   ```bash
   cd backend
   source .venv/bin/activate
   celery -A app.core.celery_app worker --loglevel=info
   ```

   **Frontend (Terminal 3):**
   ```bash
   cd frontend
   npm run dev
   ```

6. **Open your browser:**
   - Frontend: http://localhost:3001
   - Backend API: http://localhost:8003
   - API Docs: http://localhost:8003/docs

---

## 📦 Installation

### Backend Setup

1. **Create virtual environment:**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up database:**
   ```bash
   # Create PostgreSQL database
   createdb ai_growth_manager
   
   # Run migrations (if using Alembic)
   alembic upgrade head
   ```

4. **Set up Redis (optional):**
   ```bash
   # macOS
   brew install redis
   brew services start redis
   
   # Ubuntu/Debian
   sudo apt-get install redis-server
   sudo systemctl start redis
   
   # Windows
   # Download from: https://github.com/microsoftarchive/redis/releases
   ```

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure Next.js:**
   ```bash
   # Create .env.local file (see Environment Variables section)
   cp .env.example .env.local
   ```

---

## 🔐 Environment Variables

### Backend `.env`

Create `backend/.env` with the following variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ai_growth_manager

# Redis (optional - falls back to in-memory)
REDIS_URL=redis://localhost:6379/0

# OpenAI / OpenRouter
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Alternative to OpenRouter

# Clerk Authentication
CLERK_SECRET_KEY=your_clerk_secret_key_here

# OAuth - LinkedIn
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_REDIRECT_URI=http://localhost:8003/api/v1/oauth/linkedin/callback

# OAuth - Twitter
TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret
TWITTER_REDIRECT_URI=http://localhost:8003/api/v1/oauth/twitter/callback

# OAuth - Facebook
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
FACEBOOK_REDIRECT_URI=http://localhost:8003/api/v1/oauth/facebook/callback

# OAuth - Instagram (uses Facebook app)
INSTAGRAM_APP_ID=your_instagram_app_id
INSTAGRAM_APP_SECRET=your_instagram_app_secret

# Sentry (optional)
SENTRY_DSN=your_sentry_dsn_here

# CORS
FRONTEND_URL=http://localhost:3001

# Environment
ENVIRONMENT=development
```

### Frontend `.env.local`

Create `frontend/.env.local` with the following variables:

```bash
# API
NEXT_PUBLIC_API_URL=http://localhost:8003

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here
CLERK_SECRET_KEY=your_clerk_secret_key_here

# OAuth Redirect URLs (must match backend)
NEXT_PUBLIC_LINKEDIN_REDIRECT_URI=http://localhost:8003/api/v1/oauth/linkedin/callback
NEXT_PUBLIC_TWITTER_REDIRECT_URI=http://localhost:8003/api/v1/oauth/twitter/callback
NEXT_PUBLIC_FACEBOOK_REDIRECT_URI=http://localhost:8003/api/v1/oauth/facebook/callback
```

### Getting API Keys

1. **Clerk:** https://clerk.com/ (Free tier available)
2. **OpenRouter:** https://openrouter.ai/ (Pay-as-you-go)
3. **LinkedIn OAuth:** https://www.linkedin.com/developers/
4. **Twitter OAuth:** https://developer.twitter.com/
5. **Facebook/Instagram:** https://developers.facebook.com/

---

## 🚢 Deployment

### Frontend (Vercel)

1. **Push to GitHub:**
   ```bash
   git push origin main
   ```

2. **Deploy to Vercel:**
   - Go to https://vercel.com/
   - Click "Import Project"
   - Select your GitHub repository
   - Configure environment variables (from `.env.local`)
   - Click "Deploy"

3. **Configure domain:**
   - Add custom domain in Vercel settings
   - Update OAuth redirect URIs with production URLs

### Backend (Render)

1. **Create new Web Service:**
   - Go to https://render.com/
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select "backend" directory as root

2. **Configure service:**
   - **Name:** ai-growth-manager-api
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Add environment variables:**
   - Copy all variables from `backend/.env`
   - Update `DATABASE_URL` with Render PostgreSQL connection string
   - Update `FRONTEND_URL` with Vercel deployment URL

4. **Create background worker for Celery:**
   - Click "New +" → "Background Worker"
   - Same repo and environment
   - **Start Command:** `celery -A app.core.celery_app worker --loglevel=info`

5. **Create Redis instance:**
   - Click "New +" → "Redis"
   - Copy connection URL to `REDIS_URL` environment variable

---

## 📁 Project Structure

```
ai-growth-manager/
├── frontend/                   # Next.js frontend application
│   ├── app/                   # Next.js 13+ app directory
│   │   ├── dashboard/        # Protected dashboard pages
│   │   │   ├── analytics/    # Analytics page
│   │   │   ├── calendar/     # Calendar page
│   │   │   ├── content/      # Content creation page
│   │   │   ├── library/      # Content library page
│   │   │   ├── settings/     # Settings page
│   │   │   ├── strategies/   # Strategy page
│   │   │   ├── templates/    # Templates page
│   │   │   └── layout.tsx    # Dashboard layout with nav
│   │   ├── components/       # Shared app components
│   │   ├── page.tsx          # Landing page
│   │   └── layout.tsx        # Root layout
│   ├── components/           # Reusable UI components
│   │   ├── ErrorBoundary.tsx
│   │   ├── HelpIcon.tsx
│   │   ├── OnboardingChecklist.tsx
│   │   ├── PlatformPreview.tsx
│   │   ├── PostingInsights.tsx
│   │   ├── Skeletons.tsx
│   │   ├── ToastProvider.tsx
│   │   └── Tooltip.tsx
│   ├── contexts/             # React contexts
│   │   └── OnboardingContext.tsx
│   ├── lib/                  # Utilities
│   │   └── api.ts           # API client
│   ├── public/              # Static assets
│   └── package.json
│
├── backend/                   # FastAPI backend application
│   ├── app/
│   │   ├── api/             # API routes
│   │   │   ├── analytics.py
│   │   │   ├── businesses.py
│   │   │   ├── content.py
│   │   │   ├── content_library.py
│   │   │   ├── content_templates.py
│   │   │   ├── oauth.py
│   │   │   ├── posting_insights.py
│   │   │   ├── publishing.py
│   │   │   ├── scheduler.py
│   │   │   ├── social.py
│   │   │   ├── strategies.py
│   │   │   └── users.py
│   │   ├── core/            # Core utilities
│   │   │   ├── auth.py     # Clerk authentication
│   │   │   ├── celery_app.py  # Celery configuration
│   │   │   ├── openrouter.py  # OpenRouter AI client
│   │   │   ├── rate_limit.py  # Rate limiting
│   │   │   ├── redis_client.py # Redis client
│   │   │   └── security.py    # Security utilities
│   │   ├── db/              # Database
│   │   │   └── database.py # SQLAlchemy setup
│   │   ├── models/          # SQLAlchemy models
│   │   │   ├── business.py
│   │   │   ├── content.py
│   │   │   ├── content_library.py
│   │   │   ├── content_template.py
│   │   │   ├── published_post.py
│   │   │   ├── scheduled_post.py
│   │   │   ├── social_account.py
│   │   │   ├── strategy.py
│   │   │   └── user.py
│   │   ├── services/        # Business logic
│   │   │   ├── linkedin.py
│   │   │   ├── twitter.py
│   │   │   └── meta.py
│   │   └── main.py          # FastAPI app entry point
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables
│
├── screenshots/              # Marketing screenshots
│   └── README.md           # Screenshot guidelines
│
├── docs/                    # Documentation
├── .gitignore
├── README.md               # This file
├── POLISH_COMPLETE_SUMMARY.md  # Polish phase summary
└── LICENSE
```

---

## 🔧 Development Workflow

### Daily Development Process

1. **Start all services:**
   ```bash
   # Terminal 1: Backend
   cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8003
   
   # Terminal 2: Celery
   cd backend && source .venv/bin/activate && celery -A app.core.celery_app worker --loglevel=info
   
   # Terminal 3: Frontend
   cd frontend && npm run dev
   ```

2. **Make changes:**
   - Follow existing code patterns
   - Add TypeScript types for new features
   - Update components with proper error handling
   - Test on mobile devices (responsive design)

3. **Test changes:**
   - Manual testing in browser
   - Check console for errors
   - Test API endpoints in `/docs`
   - Verify mobile responsiveness

4. **Commit and push:**
   ```bash
   git add .
   git commit -m "feat: descriptive commit message"
   git push origin main
   ```

### Code Style Guidelines

- **TypeScript:** Use strict typing, avoid `any`
- **React:** Use functional components with hooks
- **CSS:** Use Tailwind utility classes
- **Naming:** camelCase for variables, PascalCase for components
- **Commits:** Use conventional commits (feat, fix, docs, style, refactor, test, chore)

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Test thoroughly**
5. **Commit:** `git commit -m 'feat: add amazing feature'`
6. **Push:** `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Pull Request Guidelines

- Include a clear description of changes
- Add screenshots for UI changes
- Update documentation if needed
- Ensure all tests pass
- Follow existing code style

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 API
- **Clerk** for authentication
- **Radix UI** for accessible components
- **Recharts** for beautiful charts
- **FastAPI** for amazing Python framework
- **Next.js** for powerful React framework

---

## 📞 Support

- **Documentation:** See `/docs` folder
- **Issues:** [GitHub Issues](https://github.com/CyberDexa/AiGrowth_Manager/issues)
- **Discussions:** [GitHub Discussions](https://github.com/CyberDexa/AiGrowth_Manager/discussions)

---

## 🎯 Roadmap

### ✅ Completed (v1.0.0)
- AI Strategy Generation
- Multi-Platform Content Creation
- Scheduled Publishing
- Analytics Dashboard
- Content Templates
- Content Library
- Smart Posting Times
- Guided Onboarding
- Mobile Responsive Design
- Error Handling & Loading States
- Toast Notifications
- Performance Optimizations
- Help System with Tooltips

### 🚧 In Progress
- Marketing assets (screenshots, demo video)
- SEO optimization
- Advanced analytics features

### 📅 Future (v2.0.0+)
- AI-powered image generation
- Video content support
- Email marketing integration
- CRM features
- A/B testing
- Multi-language support
- White-label solution
- API for third-party integrations
- Mobile app (iOS/Android)
- Advanced automation workflows

---

**Made with ❤️ for small businesses and solopreneurs**

*Last Updated: October 20, 2025*
