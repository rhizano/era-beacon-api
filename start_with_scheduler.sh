#!/usr/bin/env bash
# Enhanced start script for Render.com with scheduler support

set -o errexit  # Exit on error

# Set timezone to GMT+7 (Asia/Jakarta) to match database
export TZ="Asia/Jakarta"
echo "Set timezone to: $TZ"

# Skip database migrations - schema is already correct in production
echo "Skipping database migrations - production schema is already up to date..."

# Function to cleanup background processes on exit
cleanup() {
    echo "Cleaning up background processes..."
    if [ ! -z "$SCHEDULER_PID" ]; then
        echo "Stopping scheduler (PID: $SCHEDULER_PID)..."
        kill $SCHEDULER_PID 2>/dev/null || true
    fi
    exit 0
}

# Set up signal handlers for graceful shutdown
trap cleanup SIGTERM SIGINT

# Start the scheduler in the background
echo "Starting Era Beacon API Scheduler in background..."
cd scheduler
python scheduler.py &
SCHEDULER_PID=$!
echo "Scheduler started with PID: $SCHEDULER_PID"
cd ..

# Give scheduler a moment to initialize
sleep 5

# Start the FastAPI application in the foreground
echo "Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT &
API_PID=$!

# Wait for the API process to finish (or be killed)
wait $API_PID

# If we get here, the API has stopped, so cleanup
cleanup
