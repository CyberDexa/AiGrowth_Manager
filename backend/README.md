# Backend Setup & Running Guide

## Prerequisites

1. **Docker Desktop** must be running
2. **Python 3.11+** installed
3. Environment variables configured

## Quick Start

### 1. Start Docker Services

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Verify services are running
docker-compose ps
```

### 2. Set Up Python Environment

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Database Migrations

```bash
# Initialize Alembic (first time only)
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 4. Start the API Server

```bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Environment Variables

Create `backend/.env` with:

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/aigrowth

# Redis
REDIS_URL=redis://localhost:6379

# Clerk
CLERK_SECRET_KEY=sk_test_xxxxx
CLERK_DOMAIN=romantic-lemming-17.clerk.accounts.dev

# Other services (add as needed)
STRIPE_SECRET_KEY=
OPENROUTER_API_KEY=
```

## Testing the API

### 1. Health Check

```bash
curl http://localhost:8000/health
```

### 2. Create User (Protected)

```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_CLERK_TOKEN" \
  -d '{
    "clerk_id": "user_123",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### 3. Get Current User

```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_CLERK_TOKEN"
```

## Common Issues

### Docker Not Running

```bash
# Start Docker Desktop first, then:
docker-compose up -d postgres redis
```

### Database Connection Error

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Restart if needed
docker-compose restart postgres
```

### Migration Errors

```bash
# Reset database (CAUTION: Deletes all data)
docker-compose down -v
docker-compose up -d postgres redis

# Re-run migrations
alembic upgrade head
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

## Development Workflow

1. Make code changes
2. Backend auto-reloads (if using `--reload`)
3. Test in browser or with curl
4. Check logs in terminal

## Database Management

### View Database

```bash
# Connect to PostgreSQL
docker exec -it ai-growth-manager-postgres-1 psql -U postgres -d aigrowth

# List tables
\dt

# View users
SELECT * FROM users;

# View businesses
SELECT * FROM businesses;

# Exit
\q
```

### Create New Migration

```bash
# After modifying models
alembic revision --autogenerate -m "Add new field"

# Review the migration file in alembic/versions/

# Apply migration
alembic upgrade head
```

## Stopping Services

```bash
# Stop backend server
# Press Ctrl+C in the terminal

# Stop Docker services
docker-compose down

# Stop and remove volumes (deletes data)
docker-compose down -v
```

## Next Steps

After the backend is running:
1. Test authentication from frontend
2. Complete onboarding flow
3. Verify data is saved to database
4. Build AI strategy generation feature
