import pytest
from tests.conftest import test_client


def get_auth_headers(test_client):
    """Helper function to get authentication headers."""
    # Register and login to get token
    response = test_client.post(
        "/v1/auth/register",
        json={"username": "beacontest", "password": "testpassword123"}
    )
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_beacon(test_client):
    """Test creating a beacon."""
    headers = get_auth_headers(test_client)
    
    response = test_client.post(
        "/v1/beacons",
        json={
            "beacon_id": "TEST-BEACON-123",
            "location_name": "Test Location",
            "latitude": 34.052235,
            "longitude": -118.243683,
            "app_token": "eXQJ8V9K5fD:APA91bH_test_token"
        },
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["beacon_id"] == "TEST-BEACON-123"
    assert data["location_name"] == "Test Location"
    assert data["app_token"] == "eXQJ8V9K5fD:APA91bH_test_token"


def test_get_all_beacons(test_client):
    """Test getting all beacons."""
    headers = get_auth_headers(test_client)
    
    # Create a beacon first
    test_client.post(
        "/v1/beacons",
        json={
            "beacon_id": "TEST-BEACON-LIST",
            "location_name": "Test Location",
            "app_token": "test_token_list"
        },
        headers=headers
    )
    
    response = test_client.get("/v1/beacons", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_beacon_by_id(test_client):
    """Test getting a beacon by ID."""
    headers = get_auth_headers(test_client)
    
    # Create a beacon first
    test_client.post(
        "/v1/beacons",
        json={
            "beacon_id": "TEST-BEACON-GET",
            "location_name": "Test Location",
            "app_token": "test_token_get"
        },
        headers=headers
    )
    
    response = test_client.get("/v1/beacons/TEST-BEACON-GET", headers=headers)
    assert response.status_code == 200
    assert response.json()["beacon_id"] == "TEST-BEACON-GET"


def test_create_duplicate_beacon(test_client):
    """Test creating a beacon with duplicate beacon_id."""
    headers = get_auth_headers(test_client)
    
    # Create first beacon
    test_client.post(
        "/v1/beacons",
        json={"beacon_id": "DUPLICATE-BEACON", "location_name": "Test Location", "app_token": "test_token_dup"},
        headers=headers
    )
    
    # Try to create duplicate
    response = test_client.post(
        "/v1/beacons",
        json={"beacon_id": "DUPLICATE-BEACON", "location_name": "Test Location", "app_token": "test_token_dup2"},
        headers=headers
    )
    assert response.status_code == 409


def test_unauthorized_access(test_client):
    """Test accessing beacon endpoints without authentication."""
    response = test_client.get("/v1/beacons")
    assert response.status_code == 401


def test_update_beacon_app_token(test_client):
    """Test updating a beacon's app_token."""
    headers = get_auth_headers(test_client)
    
    # Create a beacon first
    test_client.post(
        "/v1/beacons",
        json={
            "beacon_id": "TEST-BEACON-UPDATE-TOKEN",
            "location_name": "Test Location",
            "app_token": "old_token"
        },
        headers=headers
    )
    
    # Update the app_token
    response = test_client.put(
        "/v1/beacons/TEST-BEACON-UPDATE-TOKEN",
        json={"app_token": "new_updated_token"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["app_token"] == "new_updated_token"
    assert data["beacon_id"] == "TEST-BEACON-UPDATE-TOKEN"


def test_create_beacon_without_app_token(test_client):
    """Test creating a beacon without app_token (should be optional)."""
    headers = get_auth_headers(test_client)
    
    response = test_client.post(
        "/v1/beacons",
        json={
            "beacon_id": "TEST-BEACON-NO-TOKEN",
            "location_name": "Test Location Without Token"
        },
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["beacon_id"] == "TEST-BEACON-NO-TOKEN"
    assert data["app_token"] is None
