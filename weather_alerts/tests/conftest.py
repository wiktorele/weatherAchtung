"""Pytest configuration and shared fixtures"""
import pytest
from fastapi.testclient import TestClient
from weather_alerts.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "location": "Berlin,DE",
        "preferences": {
            "min_temp": 5.0,
            "max_temp": 30.0,
            "severe_weather": True,
            "rain_alerts": False
        }
    }


@pytest.fixture(autouse=True)
def clear_data():
    """Clear in-memory storage before each test"""
    from weather_alerts.api.users import users_db
    from weather_alerts.api.alerts import alerts_db

    users_db.clear()
    alerts_db.clear()

    yield  # Run the test

    # Cleanup after test
    users_db.clear()
    alerts_db.clear()