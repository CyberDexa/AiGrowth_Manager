#!/bin/bash
set -e

echo "🚀 Starting AI Growth Manager Backend..."

# Run database migrations
echo "📊 Running database migrations..."
alembic upgrade head

echo "✅ Migrations complete!"

# Start the application
echo "🌐 Starting Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
