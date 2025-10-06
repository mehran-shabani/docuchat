#!/bin/bash

# DocuChat Backend Setup Script

set -e

echo "🚀 Setting up DocuChat Backend..."

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python 3.11+ is required (found $PYTHON_VERSION)"
    exit 1
fi

echo "✅ Python version: $PYTHON_VERSION"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and set your OPENAI_API_KEY"
else
    echo "✅ .env file exists"
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker."
    exit 1
fi

echo "✅ Docker is running"

# Start database and Redis
echo "🐳 Starting PostgreSQL and Redis..."
cd ../infra
docker compose up -d db redis
cd ../backend

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 5

# Run migrations
echo "🔄 Running database migrations..."
alembic upgrade head

echo ""
echo "✨ Setup complete!"
echo ""
echo "To start the server, run:"
echo "  uvicorn app.main:app --reload"
echo ""
echo "The API will be available at http://localhost:8000"
echo "API documentation at http://localhost:8000/docs"
