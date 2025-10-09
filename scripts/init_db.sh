#!/bin/bash
# Initialize database with Alembic migrations

set -e

echo "🔧 Setting up database..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
while ! docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; do
    sleep 1
done

echo "✅ PostgreSQL is ready"

# Create database if it doesn't exist
echo "📦 Creating database..."
docker-compose exec -T postgres psql -U postgres -c "CREATE DATABASE ai_growth_manager;" || echo "Database already exists"

# Install Python dependencies in backend container
echo "📚 Installing Python dependencies..."
docker-compose exec -T backend pip install -r requirements.txt

# Initialize Alembic (if not already initialized)
echo "🔧 Initializing Alembic..."
docker-compose exec -T backend alembic revision --autogenerate -m "Initial migration: users and businesses"

# Run migrations
echo "📊 Running database migrations..."
docker-compose exec -T backend alembic upgrade head

echo "✅ Database setup complete!"
echo ""
echo "🎉 You can now:"
echo "   - Access API docs at http://localhost:8000/docs"
echo "   - Start making API calls from the frontend"
