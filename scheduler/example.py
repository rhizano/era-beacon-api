"""
Example usage script for the Era Beacon Notification Scheduler.

This script demonstrates various ways to use the scheduler including:
- Running once for testing
- Starting the continuous scheduler
- Custom configuration
"""

import sys
import os
from datetime import datetime

# Add the scheduler directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scheduler import EraBeaconScheduler


def test_authentication():
    """Test authentication with the Era Beacon API."""
    print("Testing authentication...")
    
    scheduler = EraBeaconScheduler()
    success = scheduler.authenticate()
    
    if success:
        print(f"✓ Authentication successful!")
        print(f"  Token: {scheduler.access_token[:20]}...")
        print(f"  Expires: {scheduler.token_expires_at}")
    else:
        print("✗ Authentication failed!")
        
    return success


def test_notification():
    """Test sending a notification once."""
    print("\nTesting notification (one-time)...")
    
    scheduler = EraBeaconScheduler()
    result = scheduler.run_once()
    
    if result['success']:
        print("✓ Notification test successful!")
        if 'data' in result:
            data = result['data']
            print(f"  Total employees: {data.get('total_employees', 'N/A')}")
            print(f"  Notifications sent: {data.get('notifications_sent', 'N/A')}")
            print(f"  Notifications failed: {data.get('notifications_failed', 'N/A')}")
    elif result.get('skipped'):
        print("ⓘ Notification skipped (outside business hours)")
    else:
        print(f"✗ Notification test failed: {result['message']}")
        if 'error' in result:
            print(f"  Error: {result['error']}")


def check_business_hours():
    """Check if current time is within business hours."""
    print("\nChecking business hours...")
    
    scheduler = EraBeaconScheduler()
    is_business_hours = scheduler._is_business_hours()
    now = datetime.now()
    
    print(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')} ({now.strftime('%A')})")
    print(f"Business hours: Weekdays {scheduler.start_hour}:00-{scheduler.end_hour}:00")
    
    if is_business_hours:
        print("✓ Currently within business hours")
    else:
        print("ⓘ Currently outside business hours")
        
    return is_business_hours


def start_scheduler():
    """Start the continuous scheduler."""
    print("\nStarting continuous scheduler...")
    print("Press Ctrl+C to stop")
    
    scheduler = EraBeaconScheduler()
    scheduler.start()


def main():
    """Main function with user menu."""
    print("Era Beacon Notification Scheduler - Example Usage")
    print("=" * 50)
    
    while True:
        print("\nChoose an option:")
        print("1. Test authentication")
        print("2. Test notification (one-time)")
        print("3. Check business hours")
        print("4. Start continuous scheduler")
        print("5. Run all tests")
        print("6. Exit")
        
        try:
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                test_authentication()
                
            elif choice == '2':
                test_notification()
                
            elif choice == '3':
                check_business_hours()
                
            elif choice == '4':
                start_scheduler()
                break
                
            elif choice == '5':
                print("\nRunning all tests...")
                test_authentication()
                check_business_hours()
                test_notification()
                
            elif choice == '6':
                print("Goodbye!")
                break
                
            else:
                print("Invalid choice. Please enter a number between 1 and 6.")
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
