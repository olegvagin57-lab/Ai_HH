"""Custom exceptions for the application"""
from typing import Dict, Any, Optional
from fastapi import status


class AppException(Exception):
    """Base application exception"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(AppException):
    """Validation error exception"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST, details=details)


class NotFoundException(AppException):
    """Resource not found exception"""
    
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND, details=details)


class UnauthorizedException(AppException):
    """Unauthorized access exception"""
    
    def __init__(self, message: str = "Unauthorized", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED, details=details)


class ForbiddenException(AppException):
    """Forbidden access exception"""
    
    def __init__(self, message: str = "Forbidden", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN, details=details)


class RateLimitExceededException(AppException):
    """Rate limit exceeded exception"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=status.HTTP_429_TOO_MANY_REQUESTS, details=details)
        self.retry_after = retry_after or 60


class ExternalServiceException(AppException):
    """External service error exception"""
    
    def __init__(
        self,
        service_name: str,
        message: str = "External service error",
        details: Optional[Dict[str, Any]] = None
    ):
        full_message = f"{service_name}: {message}"
        super().__init__(full_message, status_code=status.HTTP_502_BAD_GATEWAY, details=details)
        self.service_name = service_name
