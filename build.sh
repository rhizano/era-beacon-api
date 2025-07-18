#!/usr/bin/env bash
# Build script for Render.com

set -o errexit  # Exit on error

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Skip database migrations - schema is already correct
echo "Skipping database migrations - schema already matches requirements"

echo "Build completed successfully!"
