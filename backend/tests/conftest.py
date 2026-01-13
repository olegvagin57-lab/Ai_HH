"""Pytest configuration and fixtures"""
import pytest
import asyncio
from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import settings
from app.domain.entities.user import User, Role, Permission, UserSession
from app.domain.entities.search import Search, Resume, Concept
from app.application.services.auth_service import AuthService


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db() -> AsyncGenerator:
    """Create test database connection"""
    # Use test database
    test_db_name = f"{settings.mongodb_database}_test"
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[test_db_name]
    
    # Initialize Beanie
    await init_beanie(
        database=database,
        document_models=[
            User, Role, Permission, UserSession,
            Search, Resume, Concept
        ]
    )
    
    yield database
    
    # Cleanup
    await client.drop_database(test_db_name)
    client.close()


@pytest.fixture
async def auth_service() -> AuthService:
    """Create auth service instance"""
    return AuthService()


@pytest.fixture
async def test_user(test_db, auth_service: AuthService) -> User:
    """Create test user"""
    user = await auth_service.register_user(
        email="test@example.com",
        username="testuser",
        password="TestPassword123",
        full_name="Test User"
    )
    return user


@pytest.fixture
async def admin_user(test_db, auth_service: AuthService) -> User:
    """Create admin user"""
    user = await auth_service.register_user(
        email="admin@example.com",
        username="admin",
        password="AdminPassword123",
        full_name="Admin User",
        role_names=["admin"]
    )
    return user
