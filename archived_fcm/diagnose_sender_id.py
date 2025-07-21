#!/usr/bin/env python3
"""
SenderId Mismatch Diagnostic Script
This script helps identify and resolve SenderId mismatch errors
"""
import json
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def check_firebase_project_config():
    """Check Firebase project configuration"""
    print("=== Firebase Project Configuration ===")
    
    try:
        with open('service-account-key.json', 'r') as f:
            service_account = json.load(f)
        
        project_id = service_account.get('project_id')
        client_id = service_account.get('client_id')
        client_email = service_account.get('client_email')
        
        print(f"✅ Project ID: {project_id}")
        print(f"✅ Client ID (Project Number): {client_id}")
        print(f"✅ Service Account Email: {client_email}")
        
        # Extract project number from client email if available
        if client_email and '@' in client_email:
            domain_part = client_email.split('@')[1]
            if '.iam.gserviceaccount.com' in domain_part:
                print(f"✅ Project matches service account domain")
            else:
                print(f"⚠️  Unusual service account domain: {domain_part}")
        
        return {
            'project_id': project_id,
            'project_number': client_id,  # Client ID is often the project number
            'client_email': client_email
        }
        
    except FileNotFoundError:
        print("❌ service-account-key.json not found")
        return None
    except json.JSONDecodeError:
        print("❌ Invalid JSON in service-account-key.json")
        return None
    except Exception as e:
        print(f"❌ Error reading service account: {str(e)}")
        return None

def check_environment_config():
    """Check environment configuration"""
    print("\n=== Environment Configuration ===")
    
    from app.core.config import settings
    
    print(f"FCM Project ID: {settings.fcm_project_id}")
    print(f"Service Account Path: {settings.fcm_service_account_key_path}")
    print(f"FCM Server Key: {'Set' if settings.fcm_server_key else 'Not Set'}")

def generate_sender_id_fix_guide(project_config):
    """Generate specific fix instructions"""
    if not project_config:
        return
    
    print("\n=== SenderId Mismatch Fix Guide ===")
    print(f"Your Firebase Project Number (SenderId): {project_config['project_number']}")
    print(f"Your Firebase Project ID: {project_config['project_id']}")
    
    print("\n🔧 CLIENT APP CONFIGURATION REQUIRED:")
    print("Your client app (mobile/web) must use these exact values:")
    print()
    
    print("📱 ANDROID (google-services.json):")
    print("Check that your google-services.json contains:")
    print(f'  "project_info": {{')
    print(f'    "project_number": "{project_config["project_number"]}",')
    print(f'    "project_id": "{project_config["project_id"]}"')
    print(f'  }}')
    print()
    
    print("🌐 WEB (Firebase Config):")
    print("Your Firebase web config should have:")
    print(f'  messagingSenderId: "{project_config["project_number"]}"')
    print(f'  projectId: "{project_config["project_id"]}"')
    print()
    
    print("🍎 iOS (GoogleService-Info.plist):")
    print("Check that your GoogleService-Info.plist contains:")
    print(f'  <key>PROJECT_NUMBER</key>')
    print(f'  <string>{project_config["project_number"]}</string>')
    print(f'  <key>PROJECT_ID</key>')
    print(f'  <string>{project_config["project_id"]}</string>')
    print()
    
    print("⚡ QUICK FIX STEPS:")
    print("1. Update your client app configuration files with the values above")
    print("2. Rebuild and redeploy your client app")
    print("3. Generate new FCM registration tokens from the updated client")
    print("4. Use the new tokens for testing")
    print("5. Old tokens from the previous project will NOT work")

def main():
    print("🔍 SenderId Mismatch Diagnostic Tool")
    print("=" * 50)
    
    # Check project config
    project_config = check_firebase_project_config()
    
    # Check environment
    check_environment_config()
    
    # Generate fix guide
    generate_sender_id_fix_guide(project_config)
    
    print("\n" + "=" * 50)
    print("✅ Diagnostic complete!")
    print("📋 Follow the CLIENT APP CONFIGURATION steps above to fix the SenderId mismatch")

if __name__ == "__main__":
    main()
