#!/bin/bash

echo "🧹 Cleaning up old containers..."
docker-compose down --volumes --remove-orphans
docker system prune -f

echo "📝 Creating fresh requirements.txt..."
cat > requirements.txt << 'REQUIREMENTS'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
python-multipart==0.0.6
pydub==0.25.1
python-dotenv==1.0.0
httpx==0.25.2
aiofiles==23.2.1
mutagen==1.47.0
REQUIREMENTS

echo "🔨 Building fresh containers..."
docker-compose build --no-cache

echo "🚀 Starting services..."
docker-compose up
