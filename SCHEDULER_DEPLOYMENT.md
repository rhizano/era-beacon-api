# Era Beacon API Scheduler Deployment

This document outlines the deployment configuration for the Era Beacon API with integrated automatic absence notification scheduler.

## Deployment Architecture

### Services
1. **FastAPI Application**: Main REST API service
2. **PostgreSQL Database**: Data persistence
3. **Background Scheduler**: Automated absence notifications using APScheduler

### Scheduler Integration

The scheduler runs as a background process alongside the main FastAPI application on Render.com.

#### Scheduler Features:
- **Automatic Startup**: Starts when the application deploys
- **Business Hours**: Monday-Friday, 9:00 AM - 6:00 PM (GMT+7)
- **Interval**: Configurable notification checks (default: 5 minutes)
- **Authentication**: Automatic token management with refresh
- **Logging**: Comprehensive logging to both scheduler and server logs

#### Configuration:
- Configuration file: `scheduler/config.ini`
- Logs: `scheduler/scheduler.log` + server log integration
- Dependencies: APScheduler, requests, configparser

## Deployment Process

### 1. Prerequisites
- All scheduler files in `scheduler/` directory
- Updated `requirements.txt` with scheduler dependencies
- Enhanced `start.sh` script for dual service startup

### 2. Render.com Configuration
```yaml
services:
  - type: web
    name: beacon-api
    env: python
    plan: free
    buildCommand: "./build.sh"
    startCommand: "./start.sh"  # Enhanced to include scheduler
```

### 3. Startup Sequence
1. Environment setup (timezone: Asia/Jakarta)
2. Scheduler initialization and background startup
3. FastAPI application startup
4. Both services run concurrently

### 4. Process Management
- **Graceful Shutdown**: Both services stop cleanly on SIGTERM/SIGINT
- **Error Handling**: If API fails, scheduler also stops
- **PID Tracking**: Process IDs tracked for proper cleanup

## Scheduler Configuration

### Business Logic
- **Working Days**: Monday to Friday only
- **Working Hours**: 9:00 AM to 6:00 PM (GMT+7)
- **Threshold**: Configurable absence detection (5 minutes default)
- **Notifications**: Automatic FCM push notifications for absences

### Authentication
- **Auto-Login**: Scheduler authenticates automatically using configured credentials
- **Token Refresh**: Automatic token renewal before expiration
- **Error Recovery**: Re-authentication on 401 errors

### Logging Integration
- **Dual Logging**: Separate scheduler logs + server log integration
- **Event Tracking**: Startup, authentication, notifications, errors
- **Production Monitoring**: All events visible in main application logs

## Monitoring

### Log Locations
1. **Scheduler Logs**: `scheduler/scheduler.log`
2. **Server Logs**: Integrated into main application log files
3. **Render Logs**: Available through Render.com dashboard

### Key Events to Monitor
- Scheduler startup and initialization
- Authentication success/failure
- Business hours validation
- Notification sending results
- Error conditions and recovery

### Health Checks
- Scheduler includes health check endpoints
- Manual execution capability for testing
- Comprehensive error reporting

## Maintenance

### Configuration Updates
- Update `scheduler/config.ini` for interval or business hours changes
- Restart deployment to apply configuration changes

### Troubleshooting
- Check Render.com logs for startup issues
- Review `scheduler.log` for scheduler-specific issues
- Monitor authentication token refresh cycles
- Verify business hours logic for expected execution times

## Security

### Credentials Management
- API credentials stored in `config.ini`
- Consider environment variables for production secrets
- Automatic token refresh prevents expired authentication

### Network Security
- HTTPS endpoints only
- Bearer token authentication
- Internal service communication

## Future Enhancements

### Possible Improvements
- Environment variable configuration override
- Health check HTTP endpoints
- Metrics collection and reporting
- Database-driven configuration
- Multiple notification channels
- Advanced scheduling patterns

This deployment setup provides a robust, automated absence notification system that runs alongside the main API with proper monitoring and error handling.
