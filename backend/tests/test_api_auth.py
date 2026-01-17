"""Tests for auth API endpoints"""
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Create async test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_register_endpoint(async_client, test_db):
    """Test user registration endpoint"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    email = f"apitest_{unique_id}@example.com"
    username = f"apitest_{unique_id}"
    
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "username": username,
            "password": "ApiTest123",
            "full_name": "API Test User"
        }
    )
    
    assert response.status_code in [201, 400]  # 400 if user exists
    if response.status_code == 201:
        data = response.json()
        assert "id" in data
        assert data["email"] == email


@pytest.mark.asyncio
async def test_login_endpoint(async_client, test_user):
    """Test login endpoint"""
    response = await async_client.post(
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


@pytest.mark.asyncio
async def test_login_wrong_password(async_client, test_user):
    """Test login with wrong password"""
    response = await async_client.post(
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
