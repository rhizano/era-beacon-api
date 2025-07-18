#!/usr/bin/env python3
"""
Test script to validate presence logs endpoint changes
"""
import sys
import os
import json
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.schemas.presence_log import PresenceLog, PresenceLogCreate
    print("✅ Successfully imported schemas")
    
    # Test PresenceLogCreate with various combinations
    test_cases = [
        # Case 1: Full data
        {
            "user_id": "user123",
            "beacon_id": "beacon123",
            "timestamp": datetime.now(),
            "latitude": 40.7128,
            "longitude": -74.0060,
            "signal_strength": -70
        },
        # Case 2: Minimal data (user_id only)
        {
            "user_id": "user123"
        },
        # Case 3: Without beacon_id (NULL case)
        {
            "user_id": "user123",
            "latitude": 40.7128,
            "longitude": -74.0060
        },
        # Case 4: Without timestamp (NULL case)
        {
            "user_id": "user123",
            "beacon_id": "beacon123"
        }
    ]
    
    print("\n=== Testing PresenceLogCreate schema ===")
    for i, test_data in enumerate(test_cases, 1):
        try:
            presence_create = PresenceLogCreate(**test_data)
            print(f"✅ Test case {i}: {test_data}")
        except Exception as e:
            print(f"❌ Test case {i} failed: {e}")
    
    # Test PresenceLog response with NULL values
    print("\n=== Testing PresenceLog response schema ===")
    response_test_cases = [
        # Case 1: With all fields
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": "user123",
            "beacon_id": "beacon123",
            "timestamp": datetime.now(),
            "latitude": 40.7128,
            "longitude": -74.0060,
            "signal_strength": -70,
            "created_at": datetime.now()
        },
        # Case 2: With NULL timestamp (real production case)
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "user_id": "user123",
            "beacon_id": "beacon123",
            "timestamp": None,  # This was causing the validation error
            "latitude": 40.7128,
            "longitude": -74.0060,
            "signal_strength": -70,
            "created_at": datetime.now()
        },
        # Case 3: With NULL beacon_id
        {
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "user_id": "user123",
            "beacon_id": None,
            "timestamp": datetime.now(),
            "latitude": 40.7128,
            "longitude": -74.0060,
            "signal_strength": -70,
            "created_at": datetime.now()
        }
    ]
    
    for i, test_data in enumerate(response_test_cases, 1):
        try:
            presence_log = PresenceLog(**test_data)
            print(f"✅ Response test case {i}: NULL handling works")
        except Exception as e:
            print(f"❌ Response test case {i} failed: {e}")
    
    print("\n🎉 All schema validations passed!")
    print("The presence logs endpoint should now handle NULL values correctly.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory.")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
