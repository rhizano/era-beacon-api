#!/usr/bin/env bash
# Build script for Render.com

set -o errexit  # Exit on error

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

echo "Build completed successfully!"
