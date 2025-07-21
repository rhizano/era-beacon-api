# FCM (Firebase Cloud Messaging) Integration

This document describes the complete FCM integration implemented in the ERA Beacon API.

## Overview

The FCM integration provides comprehensive push notification capabilities including:
- Single device notifications
- Multiple device notifications
- Topic-based notifications
- Custom message payloads
- Topic subscription management
- Token validation
- Health monitoring

## Configuration

### Environment Variables

Add the following to your `.env` file:

```env
# Method 1: Service Account (Recommended)
FCM_SERVICE_ACCOUNT_KEY_PATH=service-account-key.json
FCM_PROJECT_ID=erabeacon-customer

# Method 2: Legacy Server Key (Optional fallback)
# FCM_SERVER_KEY=your_fcm_server_key_here
# FCM_SENDER_ID=your_sender_id
```

### Getting Firebase Credentials

#### Method 1: Service Account (Recommended)

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project (erabeacon-customer)
3. Navigate to Project Settings > Service Accounts
4. Click "Generate new private key"
5. Download the JSON file and save it as `service-account-key.json` in your project root
6. Set `FCM_SERVICE_ACCOUNT_KEY_PATH=service-account-key.json` in your `.env` file
7. Set `FCM_PROJECT_ID=erabeacon-customer` in your `.env` file

#### Method 2: Legacy Server Key (Fallback)

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Navigate to Project Settings > Cloud Messaging
4. Copy the Server key (Legacy) for `FCM_SERVER_KEY`
5. Copy the Sender ID for `FCM_SENDER_ID`

**Note**: The service account method is more secure and is the recommended approach for production environments.

## API Endpoints

### 1. Send Notification to Single Device

**POST** `/v1/fcm/send-notification`

Send a push notification to a specific device token.

```json
{
  "token": "eXQJ8V9K5fD:APA91bH...",
  "title": "Eraspace Member is Detected!",
  "body": "Open Information",
  "link": "https://erabeacon-7e08e.web.app/",
  "data": {
    "beacon_id": "E2C56DB5-DFFB-48D2-B060-D0F5A71096E0",
    "user_id": "user123"
  }
}
```

### 2. Send Notification to Multiple Devices

**POST** `/v1/fcm/send-multiple`

Send a push notification to multiple device tokens.

```json
{
  "tokens": ["token1", "token2", "token3"],
  "title": "Broadcast Message",
  "body": "Important announcement",
  "data": {
    "type": "broadcast",
    "priority": "high"
  }
}
```

### 3. Send Notification to Topic

**POST** `/v1/fcm/send-to-topic`

Send a push notification to all devices subscribed to a topic.

```json
{
  "topic": "news",
  "title": "Breaking News",
  "body": "Important update available",
  "data": {
    "category": "news",
    "article_id": "123"
  }
}
```

### 4. Send Custom Message

**POST** `/v1/fcm/send-custom`

Send a custom FCM message with full control over the payload.

```json
{
  "token": "eXQJ8V9K5fD:APA91bH...",
  "notification": {
    "title": "Custom Title",
    "body": "Custom Body",
    "image": "https://example.com/image.png"
  },
  "data": {
    "key1": "value1",
    "key2": "value2"
  },
  "android": {
    "priority": "high",
    "notification": {
      "icon": "stock_ticker_update",
      "color": "#f45342"
    }
  }
}
```

### 5. Subscribe to Topic

**POST** `/v1/fcm/subscribe-to-topic`

Subscribe device tokens to a topic.

```json
{
  "tokens": ["token1", "token2", "token3"],
  "topic": "news"
}
```

### 6. Unsubscribe from Topic

**POST** `/v1/fcm/unsubscribe-from-topic`

Unsubscribe device tokens from a topic.

```json
{
  "tokens": ["token1", "token2", "token3"],
  "topic": "news"
}
```

### 7. Validate Token

**POST** `/v1/fcm/validate-token`

Validate an FCM device token.

```json
{
  "token": "eXQJ8V9K5fD:APA91bH..."
}
```

Response:
```json
{
  "token": "eXQJ8V9K5fD:APA91bH...",
  "is_valid": true,
  "details": {
    "valid": true,
    "response": {...}
  }
}
```

### 8. Health Check

**GET** `/v1/fcm/health`

Check FCM service health status.

Response:
```json
{
  "status": "healthy",
  "service": "fcm",
  "message": "FCM service is operational"
}
```

## Authentication

All FCM endpoints require JWT authentication. Include the Bearer token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Response Format

All FCM endpoints return a standardized response format:

```json
{
  "success": true,
  "message": "Notification sent successfully",
  "message_id": "0:1234567890123456%31bd1c9431bd1c94",
  "data": {
    "multicast_id": 216,
    "success": 1,
    "failure": 0
  }
}
```

For errors:
```json
{
  "success": false,
  "message": "Failed to send notification",
  "error": "Invalid registration token"
}
```

## Integration with Beacon System

The FCM service integrates with the existing beacon system through the `app_token` field in the beacons table. When a beacon detection occurs, the system can:

1. Look up users associated with the beacon
2. Get their FCM tokens from the `app_token` field
3. Send targeted notifications using the FCM service

Example workflow:
```python
# In your beacon detection logic
from app.services.fcm_service import FCMService

fcm_service = FCMService()

# Send notification when beacon is detected
await fcm_service.send_to_token(
    token=user.app_token,
    title="Eraspace Member is Detected!",
    body="Welcome! Check in to earn points.",
    link="https://erabeacon-7e08e.web.app/",
    data={
        "beacon_id": beacon.beacon_id,
        "user_id": str(user.id),
        "action": "beacon_detected"
    }
)
```

## Error Handling

The FCM service includes comprehensive error handling:

- **Invalid Token**: Returns validation error for malformed tokens
- **Unregistered Token**: Handles tokens that are no longer valid
- **Rate Limiting**: Handles FCM rate limits gracefully
- **Network Errors**: Retries on temporary network issues
- **Configuration Errors**: Clear error messages for missing configuration

## Testing

Run the FCM tests:

```bash
pytest tests/test_fcm.py -v
```

The test suite includes:
- Unit tests for FCM service methods
- Integration tests for API endpoints
- Mock tests for Firebase responses
- Authentication tests
- Error handling tests

## Monitoring

Monitor FCM service health using:

1. **Health Endpoint**: `GET /v1/fcm/health`
2. **Logs**: Check application logs for FCM-related messages
3. **Firebase Console**: Monitor delivery statistics in Firebase Console

## Security Considerations

1. **Server Key Protection**: Keep FCM server key secure and rotate regularly
2. **Token Validation**: Validate tokens before sending notifications
3. **Rate Limiting**: Implement rate limiting for notification endpoints
4. **Authentication**: All endpoints require valid JWT authentication
5. **Data Privacy**: Be mindful of data included in notification payloads

## Troubleshooting

### Common Issues

1. **"FCM server key is required"**
   - Ensure `FCM_SERVER_KEY` is set in your `.env` file
   - Verify the key is valid in Firebase Console

2. **"Invalid registration token"**
   - Token may be expired or invalid
   - Use the validation endpoint to check token status

3. **"Authentication required"**
   - Include valid JWT token in Authorization header
   - Ensure token hasn't expired

4. **High notification failure rate**
   - Check token validity
   - Monitor Firebase Console for delivery statistics
   - Verify app configuration matches Firebase setup

## Performance Tips

1. **Batch Operations**: Use multiple token endpoints for bulk notifications
2. **Topic Usage**: Use topics for broadcasting to many users
3. **Token Management**: Regularly validate and clean up invalid tokens
4. **Payload Size**: Keep notification payloads under 4KB limit
5. **Async Operations**: All FCM operations are async for better performance
