# BLE Beacon Presence Tracking API

A FastAPI-based REST API for tracking user presence via BLE Beacons, including user authentication and beacon/presence log management.

## Features

- User registration and authentication with JWT tokens
- BLE Beacon management (CRUD operations)
- Presence logging with geographic coordinates
- RESTful API with comprehensive error handling
- PostgreSQL database with SQLAlchemy ORM
- Comprehensive test coverage

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL
- pip

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd era-beacon-api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Set up the database:
```bash
alembic upgrade head
```

6. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000` and the interactive documentation at `http://localhost:8000/docs`.

## New Endpoints

### POST /v1/notifications/notify-absence

Send absence notifications to employees who have exceeded a specified duration threshold.

**Request Body:**
```json
{
    "threshold": 30
}
```

**Functionality:**
1. Queries the `v_presence_tracking` view for employees with `duration_minutes >= threshold`
2. Retrieves Employee ID and Employee Token for matching records
3. Sends FCM notifications to each employee via `https://even-trainer-464609-d1.et.r.appspot.com/send-notification`
4. Returns summary of notifications sent and failed

**Response:**
```json
{
    "success": true,
    "message": "Processed 5 employees", 
    "total_employees": 5,
    "notifications_sent": 4,
    "notifications_failed": 1,
    "threshold_minutes": 30
}
```

### GET /v1/absent-detail

Get detailed absence information for a specific employee from the presence tracking view.

**Query Parameters:**
- `employee_id` (required): The employee ID to get absent details for

**Functionality:**
1. Executes a SELECT query against the `v_presence_tracking` view
2. Filters results by the provided `employee_id`
3. Returns detailed information about the employee's presence status

**SQL Query Executed:**
```sql
SELECT "Store ID", "Store", "Location", "Employee ID", "Employee", 
       "Shift In", "Shift Out", "Last Detection", "Absent Duration (Hour:Minute)"
FROM v_presence_tracking
WHERE "Employee ID" = :employee_id;
```

**Response:**
```json
[
    {
        "store_id": "ST001",
        "store": "Main Store",
        "location": "Downtown",
        "employee_id": "EMP001",
        "employee": "John Doe",
        "shift_in": "2025-07-22 09:00:00",
        "shift_out": "2025-07-22 18:00:00",
        "last_detection": "2025-07-22 10:30:00",
        "absent_duration": "07:30"
    }
]
```

**Error Responses:**
- `400 Bad Request`: Missing or invalid employee_id parameter
- `404 Not Found`: No records found for the specified employee_id
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Database or server error

## 🚀 Easy Deployment

### Render.com (Recommended - Free Tier)
Deploy in 5 minutes with free PostgreSQL database:

```bash
# 1. Prepare for deployment
deploy-to-render.bat  # Windows
./deploy-to-render.sh # Mac/Linux

# 2. Push to GitHub
git add . && git commit -m "Deploy to Render" && git push

# 3. Go to render.com, create Web Service, connect your repo
# 4. Build Command: ./build.sh
# 5. Start Command: ./start.sh
# 6. Add PostgreSQL database and set environment variables
```

**📖 Complete guide**: [deployment/RENDER_DEPLOYMENT.md](deployment/RENDER_DEPLOYMENT.md)

### AWS Deployment (Advanced)
```bash
# Install serverless dependencies
npm install -g serverless
npm install

# Deploy to AWS
export DATABASE_URL="your-rds-connection-string"
export SECRET_KEY="your-secret-key"
serverless deploy
```

**📖 Complete AWS deployment guide**: [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)

## API Documentation

The API follows the OpenAPI 3.0 specification. You can view the interactive documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
era-beacon-api/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   ├── beacons.py       # Beacon management endpoints
│   │   │   └── presence_logs.py # Presence logging endpoints
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py            # Application configuration
│   │   ├── security.py          # JWT and password utilities
│   │   └── __init__.py
│   ├── database/
│   │   ├── base.py              # SQLAlchemy base
│   │   ├── session.py           # Database session
│   │   └── __init__.py
│   ├── models/
│   │   ├── beacon.py            # Beacon SQLAlchemy model
│   │   ├── presence_log.py      # PresenceLog SQLAlchemy model
│   │   ├── user.py              # User SQLAlchemy model
│   │   └── __init__.py
│   ├── services/
│   │   ├── auth_service.py      # Authentication business logic
│   │   ├── beacon_service.py    # Beacon business logic
│   │   ├── presence_service.py  # Presence logging business logic
│   │   └── __init__.py
│   ├── schemas/                 # Pydantic models
│   │   ├── auth.py
│   │   ├── beacon.py
│   │   ├── presence_log.py
│   │   └── __init__.py
│   └── main.py                  # FastAPI application entry point
├── tests/                       # Test files
├── alembic/                     # Database migrations
├── .env.example                 # Environment variables example
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Environment Variables

Create a `.env` file with the following variables:

```
# Database
DATABASE_URL=postgresql://username:password@localhost/beacon_api

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_V1_STR=/v1
PROJECT_NAME=BLE Beacon Presence Tracking API
```

## Testing

Run the tests with:
```bash
pytest
```

## License

This project is licensed under the MIT License.
