"""Tests for auth API endpoints"""
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


def test_register_endpoint(client):
    """Test user registration endpoint"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "apitest@example.com",
            "username": "apitest",
            "password": "ApiTest123",
            "full_name": "API Test User"
        }
    )
    
    assert response.status_code in [201, 400]  # 400 if user exists
    if response.status_code == 201:
        data = response.json()
        assert "id" in data
        assert data["email"] == "apitest@example.com"


def test_login_endpoint(client, test_user):
    """Test login endpoint"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email_or_username": test_user.email,
            "password": "TestPassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data


def test_login_wrong_password(client, test_user):
    """Test login with wrong password"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email_or_username": test_user.email,
            "password": "WrongPassword"
        }
    )
    
    assert response.status_code == 400


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
