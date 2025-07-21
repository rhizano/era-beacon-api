# SenderId Mismatch Error - Troubleshooting Guide

## Error Details
- **Error Code**: 403 Forbidden
- **Specific Error**: `SenderId mismatch`
- **Status**: `PERMISSION_DENIED`
- **Error Code**: `SENDER_ID_MISMATCH`

## Root Cause
The FCM registration token was generated for a different Firebase project than the one you're using to send messages.

## What is SenderId?
- SenderId is the Firebase project number (numeric ID)
- Each Firebase project has a unique SenderId
- FCM tokens are tied to a specific SenderId/project

## How to Fix

### 1. Check Your Firebase Project Details
Run this diagnostic script to see your current project configuration:

```bash
# Check your service account project details
python -c "
import json
with open('service-account-key.json', 'r') as f:
    data = json.load(f)
    print(f'Project ID: {data[\"project_id\"]}')
    print(f'Project Number (SenderId): {data[\"project_number\"]}')
    print(f'Client Email: {data[\"client_email\"]}')
"
```

### 2. Verify Client App Configuration
The client app (mobile/web) must be configured with the SAME Firebase project:

**For Android:**
- Check `google-services.json` file
- Verify `project_info.project_number` matches your service account

**For Web:**
- Check Firebase config object
- Verify `messagingSenderId` matches your project number

**For iOS:**
- Check `GoogleService-Info.plist`
- Verify `PROJECT_NUMBER` matches your service account

### 3. Solutions

#### Option A: Use Correct Service Account (Recommended)
1. Download the service account key from the SAME Firebase project where your client tokens were generated
2. Replace your current `service-account-key.json`
3. Update environment variables if needed

#### Option B: Re-generate Client Tokens
1. Update client app configuration to use your current Firebase project
2. Re-generate FCM registration tokens
3. Use the new tokens for testing

### 4. Verification Steps
1. Ensure client app and server use the same Firebase project
2. Verify project numbers match between client config and service account
3. Test with newly generated tokens

## Environment Variables to Check
- `FCM_PROJECT_ID` should match the project where tokens were generated
- Service account should be from the same project

## Testing Command
```bash
# Test with a fresh token from your current project
curl -X POST "https://your-api.com/v1/fcm/send-notification" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "token": "NEW_TOKEN_FROM_CURRENT_PROJECT",
    "title": "Test",
    "body": "Testing with correct project token"
  }'
```
