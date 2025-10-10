#!/bin/bash

echo "🎵 Shazam Clone - Setup Script"
echo "================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found! Creating from template..."
    cat > .env << 'ENV'
# Database Configuration
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=shazam_db
DATABASE_URL=postgresql://user:password@db:5432/shazam_db

# Upload Directory
UPLOAD_DIR=/app/media
ENV
    echo "✅ Created .env file"
else
    echo "✅ .env file exists"
fi

# Clean up old containers
echo ""
echo "🧹 Cleaning up old containers..."
docker-compose down --volumes --remove-orphans
docker system prune -f

# Build fresh containers
echo ""
echo "🔨 Building containers (this may take a few minutes)..."
docker-compose build --no-cache

# Start services
echo ""
echo "🚀 Starting services..."
docker-compose up -d

# Wait for database to be ready
echo ""
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run migrations
echo ""
echo "📦 Running database migrations..."
docker-compose exec -T api alembic upgrade head

echo ""
echo "================================"
echo "✅ Setup complete!"
echo ""
echo "🌐 Access the application:"
echo "   API Docs:      http://localhost:8000/docs"
echo "   Health Check:  http://localhost:8000/health"
echo "   Visualizations: http://localhost:8000/visualize/all"
echo ""
echo "📊 View logs with: docker-compose logs -f"
echo "🛑 Stop with:      docker-compose down"
echo "================================"