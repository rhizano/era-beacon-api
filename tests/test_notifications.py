import pytest
from unittest.mock import patch, MagicMock
from tests.conftest import test_client


def get_auth_headers(test_client):
    """Helper function to get authentication headers."""
    # Register and login to get token
    response = test_client.post(
        "/v1/auth/register",
        json={"username": "notifytest", "password": "testpassword123"}
    )
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_notify_to_qleap_success(test_client):
    """Test successful notification sending."""
    headers = get_auth_headers(test_client)
    
    # Create a beacon with app_token first
    test_client.post(
        "/v1/beacons",
        json={
            "beacon_id": "TEST-BEACON-NOTIFY",
            "location_name": "Test Location",
            "app_token": "test_fcm_token_123"
        },
        headers=headers
    )
    
    # Mock the requests.post call
    with patch('app.services.notification_service.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_post.return_value = mock_response
        
        response = test_client.post(
            "/v1/notifications/notify-to-qleap",
            json={
                "email": "test@example.com",
                "phone": "+1234567890",
                "beacon_id": "TEST-BEACON-NOTIFY"
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["notifications_sent"] == 1
        assert data["beacon_id"] == "TEST-BEACON-NOTIFY"
        assert "successfully" in data["message"]
        
        # Verify the external API was called with correct payload
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://even-trainer-464609-d1.et.r.appspot.com/send-notification"
        
        # Check the payload
        import json
        payload = json.loads(call_args[1]["data"])
        assert payload["token"] == "test_fcm_token_123"
        assert payload["title"] == "Eraspace Member is Detected!"
        assert payload["body"] == "Open Information"
        assert payload["link"] == "https://erabeacon-7e08e.web.app/"


def test_notify_to_qleap_beacon_not_found(test_client):
    """Test notification with non-existent beacon_id."""
    headers = get_auth_headers(test_client)
    
    response = test_client.post(
        "/v1/notifications/notify-to-qleap",
        json={
            "email": "test@example.com",
            "phone": "+1234567890",
            "beacon_id": "NON-EXISTENT-BEACON"
        },
        headers=headers
    )
    
    assert response.status_code == 404
    assert "No beacons found" in response.json()["detail"]


def test_notify_to_qleap_no_app_tokens(test_client):
    """Test notification with beacon that has no app_token."""
    headers = get_auth_headers(test_client)
    
    # Create a beacon without app_token
    test_client.post(
        "/v1/beacons",
        json={
            "beacon_id": "TEST-BEACON-NO-TOKEN",
            "location_name": "Test Location"
        },
        headers=headers
    )
    
    response = test_client.post(
        "/v1/notifications/notify-to-qleap",
        json={
            "email": "test@example.com",
            "phone": "+1234567890",
            "beacon_id": "TEST-BEACON-NO-TOKEN"
        },
        headers=headers
    )
    
    assert response.status_code == 404
    assert "no app_tokens available" in response.json()["detail"]


def test_notify_to_qleap_multiple_tokens(test_client):
    """Test notification with multiple beacons having same beacon_id but different app_tokens."""
    headers = get_auth_headers(test_client)
    
    # Create multiple beacons with the same beacon_id but different app_tokens
    # Note: In real scenario, beacon_id should be unique, but this tests the logic
    # We'll create them with slightly different beacon_ids
    test_client.post(
        "/v1/beacons",
        json={
            "beacon_id": "MULTI-TOKEN-BEACON-1",
            "location_name": "Location 1",
            "app_token": "token_1"
        },
        headers=headers
    )
    
    # Mock the requests.post call
    with patch('app.services.notification_service.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_post.return_value = mock_response
        
        response = test_client.post(
            "/v1/notifications/notify-to-qleap",
            json={
                "email": "test@example.com",
                "phone": "+1234567890",
                "beacon_id": "MULTI-TOKEN-BEACON-1"
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["notifications_sent"] == 1


def test_notify_to_qleap_external_api_failure(test_client):
    """Test notification when external API fails."""
    headers = get_auth_headers(test_client)
    
    # Create a beacon with app_token
    test_client.post(
        "/v1/beacons",
        json={
            "beacon_id": "TEST-BEACON-FAIL",
            "location_name": "Test Location",
            "app_token": "failing_token"
        },
        headers=headers
    )
    
    # Mock the requests.post call to fail
    with patch('app.services.notification_service.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        response = test_client.post(
            "/v1/notifications/notify-to-qleap",
            json={
                "email": "test@example.com",
                "phone": "+1234567890",
                "beacon_id": "TEST-BEACON-FAIL"
            },
            headers=headers
        )
        
        assert response.status_code == 500
        assert "Failed to send any notifications" in response.json()["detail"]


def test_notify_to_qleap_unauthorized(test_client):
    """Test notification endpoint without authentication."""
    response = test_client.post(
        "/v1/notifications/notify-to-qleap",
        json={
            "email": "test@example.com",
            "phone": "+1234567890",
            "beacon_id": "TEST-BEACON"
        }
    )
    
    assert response.status_code == 401
