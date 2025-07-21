# Firebase Service Account Setup

This project is configured to use Firebase Cloud Messaging (FCM) with service account authentication for secure push notifications.

## Current Configuration

- **Project ID**: `erabeacon-customer`
- **Service Account**: `firebase-adminsdk-fbsvc@erabeacon-customer.iam.gserviceaccount.com`
- **Authentication Method**: Service Account Key (JSON file)
- **FCM API Version**: v1 (modern HTTP v1 API)

## Files

- `service-account-key.json` - Firebase service account credentials (already configured)
- `.env` - Environment configuration with FCM settings

## Verification

To verify the FCM service is working correctly:

1. Start the server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

2. Test the health endpoint:
   ```bash
   curl http://localhost:8000/v1/fcm/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "service": "fcm",
     "message": "FCM service is operational"
   }
   ```

3. View API documentation:
   Open http://localhost:8000/v1/docs in your browser

## Security Notes

- The service account key file contains sensitive credentials
- Keep this file secure and never commit it to public repositories
- The current service account has the necessary permissions for FCM operations
- Rotate the service account key periodically for enhanced security

## FCM Capabilities

With this service account, the API can:

- ✅ Send notifications to individual devices
- ✅ Send notifications to multiple devices
- ✅ Send notifications to topics
- ✅ Manage topic subscriptions
- ✅ Validate FCM tokens
- ✅ Send custom message payloads
- ✅ Handle Android, iOS, and Web push notifications

## Integration Example

```python
from app.services.fcm_service import FCMService

# Initialize FCM service (uses service account automatically)
fcm_service = FCMService()

# Send notification
await fcm_service.send_to_token(
    token="device_token_here",
    title="Welcome!",
    body="You've been detected at our location",
    data={"beacon_id": "E2C56DB5-DFFB-48D2-B060-D0F5A71096E0"}
)
```

## Troubleshooting

If you encounter issues:

1. **"FCM project ID is required"** - Check that `FCM_PROJECT_ID=erabeacon-customer` is set in `.env`
2. **"Service account file not found"** - Ensure `service-account-key.json` exists in the project root
3. **"404 Not Found for FCM endpoint"** - The service now uses FCM v1 API (fixed in latest version)
4. **Authentication errors** - Verify the service account key file is valid and not corrupted
5. **Permission errors** - The service account should have Firebase Messaging Admin permissions
6. **Token validation fails** - Ensure your device tokens are valid and not expired
