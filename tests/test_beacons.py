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
            "longitude": -118.243683
        },
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["beacon_id"] == "TEST-BEACON-123"
    assert data["location_name"] == "Test Location"


def test_get_all_beacons(test_client):
    """Test getting all beacons."""
    headers = get_auth_headers(test_client)
    
    # Create a beacon first
    test_client.post(
        "/v1/beacons",
        json={
            "beacon_id": "TEST-BEACON-LIST",
            "location_name": "Test Location"
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
            "location_name": "Test Location"
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
        json={"beacon_id": "DUPLICATE-BEACON", "location_name": "Test Location"},
        headers=headers
    )
    
    # Try to create duplicate
    response = test_client.post(
        "/v1/beacons",
        json={"beacon_id": "DUPLICATE-BEACON", "location_name": "Test Location"},
        headers=headers
    )
    assert response.status_code == 409


def test_unauthorized_access(test_client):
    """Test accessing beacon endpoints without authentication."""
    response = test_client.get("/v1/beacons")
    assert response.status_code == 401
