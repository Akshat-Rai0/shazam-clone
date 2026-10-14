#!/bin/bash
# Render startup script for Shazam Clone
# This script runs database migrations and seeds the database on first deployment

set -e

echo "=========================================="
echo "Shazam Clone - Render Startup"
echo "=========================================="

# Wait for database to be ready (if needed)
echo "Waiting for database..."
# Uncomment and adjust if your database needs time to start
# sleep 5

# Run Alembic migrations
echo "Running database migrations..."
alembic upgrade head

# Seed database if empty
echo "Checking if database needs seeding..."
python scripts/seed_database.py

# Start the application
echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
