"""
Test script for the Era Beacon Notification Scheduler.

This script provides various testing scenarios for the scheduler functionality
including authentication, notification sending, and business hours validation.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
import os

# Add the scheduler directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scheduler import EraBeaconScheduler


class TestEraBeaconScheduler(unittest.TestCase):
    """Test cases for the EraBeaconScheduler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test config file
        self.test_config = """
[scheduler]
threshold_minutes = 15
api_base_url = https://era-beacon-api.onrender.com/v1
auth_username = test_user
auth_password = test_pass
weekday_start_hour = 9
weekday_end_hour = 17

[logging]
level = DEBUG
format = %(asctime)s - %(name)s - %(levelname)s - %(message)s
file = test_scheduler.log
"""
        
        with open('test_config.ini', 'w') as f:
            f.write(self.test_config)
            
        self.scheduler = EraBeaconScheduler('test_config.ini')
        
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists('test_config.ini'):
            os.remove('test_config.ini')
        if os.path.exists('test_scheduler.log'):
            os.remove('test_scheduler.log')
            
    def test_config_loading(self):
        """Test configuration loading."""
        self.assertEqual(self.scheduler.threshold_minutes, 15)
        self.assertEqual(self.scheduler.username, 'test_user')
        self.assertEqual(self.scheduler.password, 'test_pass')
        self.assertEqual(self.scheduler.start_hour, 9)
        self.assertEqual(self.scheduler.end_hour, 17)
        
    @patch('scheduler.datetime')
    def test_business_hours_weekday_within_hours(self, mock_datetime):
        """Test business hours check for weekday within hours."""
        # Mock Monday at 10:00 AM
        mock_datetime.now.return_value = datetime(2025, 7, 21, 10, 0)  # Monday
        mock_datetime.now.return_value.weekday.return_value = 0  # Monday
        mock_datetime.now.return_value.hour = 10
        
        self.assertTrue(self.scheduler._is_business_hours())
        
    @patch('scheduler.datetime')
    def test_business_hours_weekday_outside_hours(self, mock_datetime):
        """Test business hours check for weekday outside hours."""
        # Mock Monday at 8:00 AM (before business hours)
        mock_datetime.now.return_value = datetime(2025, 7, 21, 8, 0)  # Monday
        mock_datetime.now.return_value.weekday.return_value = 0  # Monday
        mock_datetime.now.return_value.hour = 8
        
        self.assertFalse(self.scheduler._is_business_hours())
        
    @patch('scheduler.datetime')
    def test_business_hours_weekend(self, mock_datetime):
        """Test business hours check for weekend."""
        # Mock Saturday at 10:00 AM
        mock_datetime.now.return_value = datetime(2025, 7, 26, 10, 0)  # Saturday
        mock_datetime.now.return_value.weekday.return_value = 5  # Saturday
        mock_datetime.now.return_value.hour = 10
        
        self.assertFalse(self.scheduler._is_business_hours())
        
    @patch('scheduler.requests.post')
    def test_authentication_success(self, mock_post):
        """Test successful authentication."""
        # Mock successful authentication response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test_token_123',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response
        
        result = self.scheduler.authenticate()
        
        self.assertTrue(result)
        self.assertEqual(self.scheduler.access_token, 'test_token_123')
        self.assertIsNotNone(self.scheduler.token_expires_at)
        
    @patch('scheduler.requests.post')
    def test_authentication_failure(self, mock_post):
        """Test failed authentication."""
        # Mock failed authentication response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = 'Invalid credentials'
        mock_post.return_value = mock_response
        
        result = self.scheduler.authenticate()
        
        self.assertFalse(result)
        self.assertIsNone(self.scheduler.access_token)
        
    @patch('scheduler.requests.post')
    def test_notification_success(self, mock_post):
        """Test successful notification sending."""
        # Setup authentication
        self.scheduler.access_token = 'valid_token'
        self.scheduler.token_expires_at = datetime.now().replace(hour=23, minute=59)
        
        # Mock business hours
        with patch.object(self.scheduler, '_is_business_hours', return_value=True):
            # Mock successful notification response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'success': True,
                'message': 'Processed 2 employees',
                'total_employees': 2,
                'notifications_sent': 1,
                'notifications_failed': 1
            }
            mock_post.return_value = mock_response
            
            result = self.scheduler.send_absence_notification()
            
            self.assertTrue(result['success'])
            self.assertEqual(result['message'], 'Notification sent successfully')
            
    def test_notification_outside_business_hours(self):
        """Test notification skipping outside business hours."""
        with patch.object(self.scheduler, '_is_business_hours', return_value=False):
            result = self.scheduler.send_absence_notification()
            
            self.assertFalse(result['success'])
            self.assertTrue(result.get('skipped', False))
            self.assertEqual(result['message'], 'Outside business hours')
            
    @patch('scheduler.requests.post')
    def test_token_refresh_on_401(self, mock_post):
        """Test token refresh when receiving 401 Unauthorized."""
        # Setup expired token
        self.scheduler.access_token = 'expired_token'
        self.scheduler.token_expires_at = datetime.now().replace(hour=23, minute=59)
        
        with patch.object(self.scheduler, '_is_business_hours', return_value=True):
            # Mock 401 response
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.text = 'Unauthorized'
            mock_post.return_value = mock_response
            
            result = self.scheduler.send_absence_notification()
            
            self.assertFalse(result['success'])
            self.assertIsNone(self.scheduler.access_token)  # Token should be cleared


class TestSchedulerIntegration:
    """
    Integration test class for manual testing with the actual API.
    
    Note: These tests require a running Era Beacon API and valid credentials.
    Run these manually when you want to test against the real API.
    """
    
    def __init__(self):
        self.scheduler = EraBeaconScheduler()
        
    def test_real_authentication(self):
        """Test authentication against the real API."""
        print("Testing real authentication...")
        result = self.scheduler.authenticate()
        
        if result:
            print(f"✓ Authentication successful. Token: {self.scheduler.access_token[:20]}...")
            print(f"✓ Token expires at: {self.scheduler.token_expires_at}")
        else:
            print("✗ Authentication failed")
            
        return result
        
    def test_real_notification(self):
        """Test notification sending against the real API."""
        print("Testing real notification...")
        
        # First authenticate
        if not self.test_real_authentication():
            print("✗ Cannot test notification without authentication")
            return False
            
        result = self.scheduler.send_absence_notification()
        
        if result['success']:
            print("✓ Notification sent successfully")
            if 'data' in result:
                data = result['data']
                print(f"  - Total employees: {data.get('total_employees', 'N/A')}")
                print(f"  - Notifications sent: {data.get('notifications_sent', 'N/A')}")
                print(f"  - Notifications failed: {data.get('notifications_failed', 'N/A')}")
        else:
            print(f"✗ Notification failed: {result['message']}")
            if 'error' in result:
                print(f"  Error: {result['error']}")
                
        return result['success']
        
    def test_business_hours_logic(self):
        """Test business hours logic with current time."""
        print("Testing business hours logic...")
        
        is_business_hours = self.scheduler._is_business_hours()
        now = datetime.now()
        
        print(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')} ({now.strftime('%A')})")
        print(f"Business hours: Weekdays {self.scheduler.start_hour}:00-{self.scheduler.end_hour}:00")
        print(f"Is business hours: {'✓ Yes' if is_business_hours else '✗ No'}")
        
        return is_business_hours


def run_unit_tests():
    """Run all unit tests."""
    print("Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)


def run_integration_tests():
    """Run integration tests against the real API."""
    print("\n" + "="*50)
    print("INTEGRATION TESTS (Real API)")
    print("="*50)
    
    tester = TestSchedulerIntegration()
    
    print("\n1. Testing business hours logic:")
    tester.test_business_hours_logic()
    
    print("\n2. Testing authentication:")
    auth_success = tester.test_real_authentication()
    
    if auth_success:
        print("\n3. Testing notification:")
        tester.test_real_notification()
    else:
        print("\n3. Skipping notification test (authentication failed)")
        
    print("\n" + "="*50)
    print("Integration tests completed")
    print("="*50)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test the Era Beacon Scheduler')
    parser.add_argument('--unit', action='store_true', help='Run unit tests')
    parser.add_argument('--integration', action='store_true', help='Run integration tests')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    
    args = parser.parse_args()
    
    if args.all or (not args.unit and not args.integration):
        run_unit_tests()
        run_integration_tests()
    elif args.unit:
        run_unit_tests()
    elif args.integration:
        run_integration_tests()
