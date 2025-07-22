# Era Beacon API Notification Scheduler

This directory contains a job scheduler implementation using APScheduler to automatically send absence notifications from the Era Beacon API.

## Features

- **Automatic Authentication**: Obtains and manages Bearer tokens from the Era Beacon API
- **Scheduled Notifications**: Sends absence notifications every M minutes during business hours
- **Business Hours Only**: Runs only on weekdays (Monday-Friday) between 9:00-18:00
- **Configurable**: All settings can be customized via `config.ini`
- **Error Handling**: Comprehensive error handling with retry logic for authentication
- **Logging**: Detailed logging to both file and console
- **Token Management**: Automatic token refresh when expired

## Installation

1. Install required dependencies:
```bash
pip install apscheduler requests
```

2. Configure the scheduler by editing `config.ini`:
```ini
[scheduler]
threshold_minutes = 30
api_base_url = https://era-beacon-api.onrender.com/v1
auth_username = era_user
auth_password = Era2025!
weekday_start_hour = 9
weekday_end_hour = 18

[logging]
level = INFO
format = %(asctime)s - %(name)s - %(levelname)s - %(message)s
file = scheduler.log
```

## Usage

### Running the Scheduler

Start the scheduler in continuous mode:
```bash
python scheduler.py
```

The scheduler will:
1. Authenticate with the API on startup
2. Schedule the notification job to run every `threshold_minutes`
3. Only execute during business hours (weekdays 9:00-18:00)
4. Log all activities to `scheduler.log` and console

### Testing

To test the notification job once without scheduling:
```python
from scheduler import EraBeaconScheduler

scheduler = EraBeaconScheduler()
result = scheduler.run_once()
print(result)
```

### Stopping the Scheduler

Press `Ctrl+C` to gracefully stop the scheduler.

## Configuration Options

### Scheduler Section
- `threshold_minutes`: Interval in minutes for running the job AND the threshold value sent to the API
- `api_base_url`: Base URL of the Era Beacon API
- `auth_username`: Username for API authentication
- `auth_password`: Password for API authentication
- `weekday_start_hour`: Start hour for business hours (24-hour format)
- `weekday_end_hour`: End hour for business hours (24-hour format)

### Logging Section
- `level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `format`: Log message format
- `file`: Log file name

## API Integration

The scheduler integrates with two Era Beacon API endpoints:

### Authentication Endpoint
- **URL**: `POST /v1/auth/login`
- **Body**: `{"username": "era_user", "password": "Era2025!"}`
- **Response**: `{"access_token": "...", "expires_in": 3600}`

### Notification Endpoint
- **URL**: `POST /v1/notifications/notify-absence`
- **Headers**: `Authorization: Bearer <token>`, `Content-Type: application/json`
- **Body**: `{"threshold": M}`
- **Response**: Detailed notification results with curl commands and response details

## Error Handling

The scheduler includes comprehensive error handling:

1. **Authentication Failures**: Automatically retries authentication on token expiration
2. **Network Issues**: Logs network errors and continues with next scheduled run
3. **API Errors**: Handles various HTTP status codes appropriately
4. **Business Hours**: Skips execution outside of configured business hours
5. **Job Failures**: Logs failed jobs and continues scheduling

## Logging

All activities are logged with timestamps and appropriate log levels:

- **INFO**: Normal operations, successful notifications, schedule events
- **WARNING**: Non-critical issues, failed notifications
- **ERROR**: Authentication failures, network errors, API errors
- **DEBUG**: Detailed execution information (when log level is DEBUG)

Logs are written to both:
- Console output
- Log file (default: `scheduler.log`)

## Example Log Output

```
2025-07-22 09:00:00,123 - __main__ - INFO - Starting Era Beacon Notification Scheduler
2025-07-22 09:00:00,456 - __main__ - INFO - Attempting to authenticate with Era Beacon API
2025-07-22 09:00:01,789 - __main__ - INFO - Authentication successful
2025-07-22 09:00:01,790 - __main__ - INFO - Job scheduled to run every 30 minutes
2025-07-22 09:30:00,001 - __main__ - INFO - Executing scheduled absence notification job
2025-07-22 09:30:01,234 - __main__ - INFO - Sending absence notification with threshold: 30 minutes
2025-07-22 09:30:02,567 - __main__ - INFO - Notification sent successfully: Processed 2 employees
2025-07-22 09:30:02,568 - __main__ - INFO - Notification summary: 2 employees processed, 0 sent, 2 failed
```

## Production Deployment

For production deployment, consider:

1. **Service Management**: Use systemd, supervisor, or similar to manage the scheduler process
2. **Log Rotation**: Configure log rotation to prevent log files from growing too large
3. **Monitoring**: Monitor the scheduler process and log files for issues
4. **Security**: Secure the configuration file containing credentials
5. **Timezone**: Ensure the server timezone matches your business hours requirements

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Check username/password in config.ini
   - Verify API URL is correct and accessible
   - Check network connectivity

2. **Jobs Not Running**
   - Verify current time is within business hours
   - Check scheduler logs for errors
   - Ensure APScheduler is properly installed

3. **Token Expiration**
   - The scheduler automatically handles token refresh
   - Check logs for authentication retry attempts

4. **Network Issues**
   - Verify internet connectivity
   - Check if API endpoints are accessible
   - Review timeout settings if needed
