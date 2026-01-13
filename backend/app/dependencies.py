"""Dependency injection container"""
from app.application.services.auth_service import AuthService


def get_auth_service() -> AuthService:
    """Get auth service instance"""
    return AuthService()
