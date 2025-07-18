#!/usr/bin/env python3
"""
Test script to validate PresenceLog model import
"""
import sys
import os

print("Testing PresenceLog model import...")

try:
    # Add the app directory to Python path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
    
    from app.models.presence_log import PresenceLog
    print("✅ PresenceLog model imports successfully")
    print(f"✅ Table name: {PresenceLog.__tablename__}")
    print("✅ Model definition is valid")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("🎉 Model test completed successfully!")
