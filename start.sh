#!/usr/bin/env bash
# Start script for Render.com

set -o errexit  # Exit on error

# Skip database migrations - schema is already correct in production
echo "Skipping database migrations - production schema is already up to date..."

# Start the FastAPI application
echo "Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
