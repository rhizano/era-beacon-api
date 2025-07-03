# Quick Start Guide

## Prerequisites
- Python 3.8 or higher
- PostgreSQL (optional - SQLite works for development)
- Git

## Option 1: Quick Development Setup (SQLite)

1. **Clone and Setup**
   ```bash
   git clone <your-repo>
   cd era-beacon-api
   
   # Windows
   setup.bat
   
   # Linux/Mac
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.dev .env
   ```

3. **Initialize Database**
   ```bash
   alembic upgrade head
   ```

4. **Start Development Server**
   ```bash
   python run_dev.py
   ```

5. **Access API Documentation**
   - Swagger UI: http://localhost:8000/v1/docs
   - ReDoc: http://localhost:8000/v1/redoc

## Option 2: Docker Development Setup

1. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Access API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/v1/docs

## Testing the API

1. **Register a User**
   ```bash
   curl -X POST "http://localhost:8000/v1/auth/register" \
        -H "Content-Type: application/json" \
        -d '{"username": "testuser", "password": "testpass123"}'
   ```

2. **Login and Get Token**
   ```bash
   curl -X POST "http://localhost:8000/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username": "testuser", "password": "testpass123"}'
   ```

3. **Create a Beacon** (use token from step 2)
   ```bash
   curl -X POST "http://localhost:8000/v1/beacons" \
        -H "Authorization: Bearer YOUR_TOKEN_HERE" \
        -H "Content-Type: application/json" \
        -d '{
          "beacon_id": "BEACON-001",
          "location_name": "Main Entrance",
          "latitude": 34.052235,
          "longitude": -118.243683
        }'
   ```

4. **Log Presence**
   ```bash
   curl -X POST "http://localhost:8000/v1/presence-logs" \
        -H "Authorization: Bearer YOUR_TOKEN_HERE" \
        -H "Content-Type: application/json" \
        -d '{
          "user_id": "user123",
          "beacon_id": "BEACON-001",
          "latitude": 34.052235,
          "longitude": -118.243683,
          "signal_strength": -65
        }'
   ```

## Running Tests

```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Run tests
pytest
```

## Available Endpoints

### Authentication
- `POST /v1/auth/register` - Register new user
- `POST /v1/auth/login` - Login user

### Beacons (Requires Authentication)
- `GET /v1/beacons` - Get all beacons
- `POST /v1/beacons` - Create beacon
- `GET /v1/beacons/{beacon_id}` - Get beacon by ID
- `PUT /v1/beacons/{beacon_id}` - Update beacon
- `DELETE /v1/beacons/{beacon_id}` - Delete beacon

### Presence Logs (Requires Authentication)
- `POST /v1/presence-logs` - Log presence
- `GET /v1/presence-logs` - Get presence logs (with filtering)
- `GET /v1/presence-logs/{id}` - Get presence log by ID
- `DELETE /v1/presence-logs/{id}` - Delete presence log

## Development Commands

```bash
# Start development server
python run_dev.py

# Run tests
pytest

# Create database migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Build Docker image
docker build -t era-beacon-api .
```

## Troubleshooting

1. **Database Connection Issues**
   - Check DATABASE_URL in .env file
   - Ensure PostgreSQL is running (if using PostgreSQL)
   - For development, SQLite is recommended (.env.dev)

2. **Import Errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

3. **Migration Issues**
   - Delete alembic/versions/*.py files
   - Run `alembic revision --autogenerate -m "initial"`
   - Run `alembic upgrade head`
