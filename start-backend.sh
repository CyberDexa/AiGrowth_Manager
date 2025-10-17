#!/bin/bash

# AI Growth Manager - Backend Startup Script

cd /Users/olaoluwabayomi/Desktop/growth/solodev/04_MY_PROJECTS/active/ai-growth-manager/backend

echo "🚀 Starting AI Growth Manager Backend..."
echo "📍 Running on: http://localhost:8003"
echo "✅ Press Ctrl+C to stop"
echo ""

/Users/olaoluwabayomi/Desktop/growth/solodev/04_MY_PROJECTS/active/ai-growth-manager/backend/venv/bin/python -m uvicorn app.main:app --reload --host localhost --port 8003 --app-dir /Users/olaoluwabayomi/Desktop/growth/solodev/04_MY_PROJECTS/active/ai-growth-manager/backend
