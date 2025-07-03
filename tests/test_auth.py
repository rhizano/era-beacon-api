import pytest
from tests.conftest import test_client


def test_register_user(test_client):
    """Test user registration."""
    response = test_client.post(
        "/v1/auth/register",
        json={"username": "testuser", "password": "testpassword123"}
    )
    assert response.status_code == 201
    assert "token" in response.json()


def test_register_duplicate_user(test_client):
    """Test registering a user with existing username."""
    # Register first user
    test_client.post(
        "/v1/auth/register",
        json={"username": "duplicate", "password": "testpassword123"}
    )
    
    # Try to register same username again
    response = test_client.post(
        "/v1/auth/register",
        json={"username": "duplicate", "password": "testpassword123"}
    )
    assert response.status_code == 409


def test_login_user(test_client):
    """Test user login."""
    # Register user first
    test_client.post(
        "/v1/auth/register",
        json={"username": "logintest", "password": "testpassword123"}
    )
    
    # Login
    response = test_client.post(
        "/v1/auth/login",
        json={"username": "logintest", "password": "testpassword123"}
    )
    assert response.status_code == 200
    assert "token" in response.json()


def test_login_invalid_credentials(test_client):
    """Test login with invalid credentials."""
    response = test_client.post(
        "/v1/auth/login",
        json={"username": "nonexistent", "password": "wrongpassword"}
    )
    assert response.status_code == 401
