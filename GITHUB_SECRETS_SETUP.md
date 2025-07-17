# Using GitHub Secrets for FCM Service Account

## Setup GitHub Secrets (Recommended for CI/CD)

1. Go to your GitHub repository: https://github.com/rhizano/era-beacon-api
2. Navigate to Settings > Secrets and variables > Actions
3. Click "New repository secret"
4. Create a secret named `FCM_SERVICE_ACCOUNT_KEY` 
5. Paste the entire contents of `service-account-key.json` as the value

## Update your deployment scripts to use the secret:

```yaml
# .github/workflows/deploy.yml
- name: Create service account key file
  run: echo '${{ secrets.FCM_SERVICE_ACCOUNT_KEY }}' > service-account-key.json
```

## Environment Variables for Production

Instead of committing the file, use these environment variables:

```bash
# Set in your production environment
export FCM_PROJECT_ID="erabeacon-customer"
export FCM_CLIENT_EMAIL="firebase-adminsdk-fbsvc@erabeacon-customer.iam.gserviceaccount.com"
export FCM_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n..."
```

This approach keeps your credentials secure while allowing deployment automation.
