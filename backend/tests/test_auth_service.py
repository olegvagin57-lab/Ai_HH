"""Tests for auth service"""
import pytest
from app.application.services.auth_service import AuthService
from app.core.exceptions import ValidationException, UnauthorizedException


@pytest.mark.asyncio
async def test_register_user(auth_service: AuthService):
    """Test user registration"""
    user = await auth_service.register_user(
        email="newuser@example.com",
        username="newuser",
        password="SecurePass123",
        full_name="New User"
    )
    
    assert user.email == "newuser@example.com"
    assert user.username == "newuser"
    assert user.full_name == "New User"
    assert user.is_active is True
    assert "viewer" in user.role_names


@pytest.mark.asyncio
async def test_register_user_weak_password(auth_service: AuthService):
    """Test registration with weak password"""
    with pytest.raises(ValidationException):
        await auth_service.register_user(
            email="user@example.com",
            username="user",
            password="weak"
        )


@pytest.mark.asyncio
async def test_register_duplicate_email(auth_service: AuthService, test_user):
    """Test registration with duplicate email"""
    with pytest.raises(ValidationException):
        await auth_service.register_user(
            email=test_user.email,
            username="different",
            password="SecurePass123"
        )


@pytest.mark.asyncio
async def test_authenticate_user(auth_service: AuthService, test_user):
    """Test user authentication"""
    user = await auth_service.authenticate_user(
        test_user.email,
        "TestPassword123"
    )
    
    assert user is not None
    assert user.email == test_user.email


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(auth_service: AuthService, test_user):
    """Test authentication with wrong password"""
    user = await auth_service.authenticate_user(
        test_user.email,
        "WrongPassword"
    )
    
    assert user is None


@pytest.mark.asyncio
async def test_create_user_session(auth_service: AuthService, test_user):
    """Test session creation"""
    tokens = await auth_service.create_user_session(
        test_user,
        ip_address="127.0.0.1",
        user_agent="test-agent"
    )
    
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_access_token(auth_service: AuthService, test_user):
    """Test token refresh"""
    # Create session
    tokens = await auth_service.create_user_session(test_user)
    refresh_token = tokens["refresh_token"]
    
    # Refresh token
    new_tokens = await auth_service.refresh_access_token(refresh_token)
    
    assert "access_token" in new_tokens
    assert new_tokens["access_token"] != tokens["access_token"]


@pytest.mark.asyncio
async def test_refresh_invalid_token(auth_service: AuthService):
    """Test refresh with invalid token"""
    with pytest.raises(UnauthorizedException):
        await auth_service.refresh_access_token("invalid_token")
