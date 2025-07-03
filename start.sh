#!/usr/bin/env bash
# Start script for Render.com

set -o errexit  # Exit on error

# Run database migrations (in case they weren't run in build)
echo "Ensuring database is up to date..."
alembic upgrade head

# Start the FastAPI application
echo "Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
