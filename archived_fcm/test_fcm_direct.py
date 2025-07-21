#!/usr/bin/env python3
"""
Direct FCM test script to debug 403 errors
"""
import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.fcm_service import FCMService
from app.core.config import settings

async def test_fcm_direct():
    """Test FCM service directly"""
    
    print("=== FCM Direct Test ===")
    print(f"Project ID: {settings.fcm_project_id}")
    print(f"Service Account Path: {settings.fcm_service_account_key_path}")
    print(f"Server Key: {'Set' if settings.fcm_server_key else 'Not Set'}")
    
    # Initialize FCM service
    fcm_service = FCMService()
    
    # Test 1: Check permissions
    print("\n=== Testing Service Account Permissions ===")
    try:
        permissions = await fcm_service.check_service_account_permissions()
        print(f"Permissions check result: {permissions}")
    except Exception as e:
        print(f"Permission check error: {str(e)}")
    
    # Test 2: Try to send a test notification with properly formatted token
    print("\n=== Testing FCM Send Notification ===")
    try:
        # Use a more realistic token format (still fake but properly formatted)
        # Real FCM tokens are usually 152+ characters long and base64-like
        test_token = "fGxqb2_VQFu9:APA91bE5nD8QhQr6mF5nP9wK8vL2xY4zS7rT3qU1w6eE9cH0jI5mL8nO4pQ7sT0uV3xY6zA9bC2eF5hI8kN1qT4wV7zA0cF3hI6kN9qT2uV5xY8zA1eF4hI7kN0qT3uV6xY9zA2eF"
        
        result = await fcm_service.send_to_token(
            token=test_token,
            title="Test Notification",
            body="Testing FCM API v1",
            data={"test": "true"}
        )
        print(f"Send result: {result}")
    except Exception as e:
        print(f"Send notification error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fcm_direct())
