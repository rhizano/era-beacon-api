# Firebase API Status Check

## Possible Causes for 403 Forbidden Error

### 1. Firebase Cloud Messaging API Not Enabled
The Firebase Cloud Messaging API might not be enabled in your Google Cloud project.

**Solution:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select project: `erabeacon-customer`
3. Navigate to "APIs & Services" > "Library"
4. Search for "Firebase Cloud Messaging API"
5. Click on it and ensure it's **ENABLED**

### 2. Service Account Roles
The service account might not have the correct IAM roles.

**Required Roles:**
- `Firebase Admin SDK Service Agent`
- `Cloud Messaging Admin` (if available)

**Check/Fix:**
1. Go to Google Cloud Console > IAM & Admin > IAM
2. Find your service account: `firebase-adminsdk-fbsvc@erabeacon-customer.iam.gserviceaccount.com`
3. Ensure it has proper Firebase roles

### 3. Project Configuration
There might be project-level restrictions.

**Check:**
1. Firebase Console > Project Settings > General
2. Verify project ID matches: `erabeacon-customer`
3. Check if project is active and not suspended

### 4. API Quotas and Limits
The project might have exceeded FCM quotas.

**Check:**
1. Google Cloud Console > APIs & Services > Quotas
2. Look for Firebase Cloud Messaging quotas
3. Check if any limits are exceeded

## Testing Steps

1. **Enable FCM API** (most likely cause):
   ```bash
   # Using gcloud CLI (if available)
   gcloud services enable fcm.googleapis.com --project=erabeacon-customer
   ```

2. **Test with a simple message**:
   Try the send-notification endpoint with minimal payload

3. **Check logs**:
   Look for detailed error messages in the server logs
