"""Tests for user management API endpoints"""
import pytest
from fastapi import status


def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "Weather Alert System API" in response.json()["message"]


def test_create_user(client, sample_user_data):
    """Test creating a new user"""
    response = client.post("/api/v1/users/", json=sample_user_data)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["email"] == sample_user_data["email"]
    assert data["location"] == sample_user_data["location"]
    assert "user_id" in data
    assert "created_at" in data
    assert data["last_alert"] is None


def test_create_user_duplicate_email(client, sample_user_data):
    """Test that duplicate emails are rejected"""
    # Create first user
    client.post("/api/v1/users/", json=sample_user_data)

    # Try to create another with same email
    response = client.post("/api/v1/users/", json=sample_user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]


def test_create_user_invalid_data(client):
    """Test that invalid data is rejected"""
    invalid_data = {
        "email": "not-an-email",  # Invalid email format
        "location": "Berlin"
        # Missing preferences
    }

    response = client.post("/api/v1/users/", json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_user(client, sample_user_data):
    """Test getting a user by ID"""
    # Create user first
    create_response = client.post("/api/v1/users/", json=sample_user_data)
    user_id = create_response.json()["user_id"]

    # Get the user
    response = client.get(f"/api/v1/users/{user_id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["user_id"] == user_id
    assert data["email"] == sample_user_data["email"]


def test_get_user_not_found(client):
    """Test getting a non-existent user"""
    response = client.get("/api/v1/users/nonexistent-id")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_users(client, sample_user_data):
    """Test listing all users"""
    # Create multiple users
    for i in range(3):
        user_data = sample_user_data.copy()
        user_data["email"] = f"user{i}@example.com"
        client.post("/api/v1/users/", json=user_data)

    # List users
    response = client.get("/api/v1/users/")

    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert len(users) == 3


def test_list_users_pagination(client, sample_user_data):
    """Test user list pagination"""
    # Create 5 users
    for i in range(5):
        user_data = sample_user_data.copy()
        user_data["email"] = f"user{i}@example.com"
        client.post("/api/v1/users/", json=user_data)

    # Get first 2 users
    response = client.get("/api/v1/users/?limit=2&offset=0")
    assert len(response.json()) == 2

    # Get next 2 users
    response = client.get("/api/v1/users/?limit=2&offset=2")
    assert len(response.json()) == 2


def test_update_user(client, sample_user_data):
    """Test updating user preferences"""
    # Create user
    create_response = client.post("/api/v1/users/", json=sample_user_data)
    user_id = create_response.json()["user_id"]

    # Update preferences
    update_data = {
        "location": "London,UK",
        "preferences": {
            "min_temp": 10.0,
            "max_temp": 25.0,
            "severe_weather": False,
            "rain_alerts": True
        }
    }

    response = client.put(f"/api/v1/users/{user_id}", json=update_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["location"] == "London,UK"
    assert data["preferences"]["rain_alerts"] is True


def test_update_user_partial(client, sample_user_data):
    """Test partial update (only location)"""
    # Create user
    create_response = client.post("/api/v1/users/", json=sample_user_data)
    user_id = create_response.json()["user_id"]

    # Update only location
    update_data = {"location": "Paris,FR"}

    response = client.put(f"/api/v1/users/{user_id}", json=update_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["location"] == "Paris,FR"
    # Preferences should remain unchanged
    assert data["preferences"]["min_temp"] == 5.0


def test_update_user_not_found(client):
    """Test updating non-existent user"""
    update_data = {"location": "Paris,FR"}
    response = client.put("/api/v1/users/nonexistent-id", json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_user(client, sample_user_data):
    """Test deleting a user"""
    # Create user
    create_response = client.post("/api/v1/users/", json=sample_user_data)
    user_id = create_response.json()["user_id"]

    # Delete user
    response = client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify user is gone
    get_response = client.get(f"/api/v1/users/{user_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_user_not_found(client):
    """Test deleting non-existent user"""
    response = client.delete("/api/v1/users/nonexistent-id")
    assert response.status_code == status.HTTP_404_NOT_FOUND