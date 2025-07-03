# Project Structure

```
era-beacon-api/
├── app/                           # Main application package
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── api/                       # API layer
│   │   ├── __init__.py
│   │   └── routes/                # API route handlers
│   │       ├── __init__.py
│   │       ├── auth.py            # Authentication endpoints
│   │       ├── beacons.py         # Beacon management endpoints
│   │       └── presence_logs.py   # Presence logging endpoints
│   ├── core/                      # Core utilities
│   │   ├── __init__.py
│   │   ├── config.py              # Application configuration
│   │   └── security.py            # JWT and password utilities
│   ├── database/                  # Database configuration
│   │   ├── __init__.py
│   │   ├── base.py                # SQLAlchemy base imports
│   │   └── session.py             # Database session management
│   ├── models/                    # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── beacon.py              # Beacon database model
│   │   ├── presence_log.py        # PresenceLog database model
│   │   └── user.py                # User database model
│   ├── schemas/                   # Pydantic models (API schemas)
│   │   ├── __init__.py
│   │   ├── auth.py                # Authentication schemas
│   │   ├── beacon.py              # Beacon schemas
│   │   ├── error.py               # Error response schemas
│   │   └── presence_log.py        # Presence log schemas
│   └── services/                  # Business logic layer
│       ├── __init__.py
│       ├── auth_service.py        # Authentication business logic
│       ├── beacon_service.py      # Beacon business logic
│       └── presence_service.py    # Presence logging business logic
├── tests/                         # Test files
│   ├── __init__.py
│   ├── conftest.py               # Test configuration
│   ├── test_auth.py              # Authentication tests
│   └── test_beacons.py           # Beacon tests
├── alembic/                      # Database migrations
│   ├── versions/                 # Migration files
│   ├── env.py                    # Alembic environment
│   ├── README
│   └── script.py.mako
├── alembic.ini                   # Alembic configuration
├── docker-compose.yml            # Docker Compose for development
├── Dockerfile                    # Docker configuration
├── Makefile                      # Development commands
├── README.md                     # Project documentation
├── requirements.txt              # Python dependencies
├── run_dev.py                    # Development server script
├── setup.bat                     # Windows setup script
├── .env.example                  # Environment variables example
├── .env.dev                      # Development environment
├── .gitignore                    # Git ignore rules
└── oas.beacon-api.yaml          # OpenAPI specification
```

## Key Files Description

### Application Core
- **app/main.py**: FastAPI application setup with middleware and route registration
- **app/core/config.py**: Configuration management using Pydantic Settings
- **app/core/security.py**: JWT token handling and password hashing utilities

### Database Layer
- **app/models/**: SQLAlchemy ORM models for database tables
- **app/database/session.py**: Database connection and session management
- **alembic/**: Database migration files and configuration

### API Layer
- **app/api/routes/**: FastAPI route handlers organized by feature
- **app/schemas/**: Pydantic models for request/response validation
- **app/services/**: Business logic separated from API routes

### Development Tools
- **docker-compose.yml**: Complete development environment with PostgreSQL
- **run_dev.py**: Development server with hot reload
- **setup.bat**: Automated setup for Windows development
- **Makefile**: Common development tasks and commands

### Testing
- **tests/**: Comprehensive test suite with pytest
- **tests/conftest.py**: Test configuration and fixtures

This structure follows FastAPI best practices and clean architecture principles, separating concerns across different layers for maintainability and testability.
