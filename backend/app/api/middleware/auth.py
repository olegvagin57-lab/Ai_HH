"""Authentication middleware"""
from fastapi import Request, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import security_service
from app.core.logging import get_logger
from app.core.exceptions import UnauthorizedException
from app.domain.entities.user import User


logger = get_logger(__name__)
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current authenticated user from JWT token"""
    logger.info("get_current_user called", 
                has_credentials=credentials is not None,
                credentials_type=type(credentials).__name__ if credentials else None)
    try:
        if not credentials:
            logger.error("No credentials provided")
            raise UnauthorizedException("No credentials provided")
        
        token = credentials.credentials
        logger.debug("Token received", token_length=len(token) if token else 0)
        
        # Verify token
        payload = security_service.verify_token(token, token_type="access")
        if not payload:
            logger.warning("Token verification failed")
            raise UnauthorizedException("Invalid or expired token")
        
        # Get user ID from token
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("No user ID in token payload", payload_keys=list(payload.keys()))
            raise UnauthorizedException("Invalid token payload")
        
        logger.debug("Fetching user from database", user_id=user_id)
        # Get user from database
        user = await User.get(user_id)
        if not user:
            logger.warning("User not found in database", user_id=user_id)
            raise UnauthorizedException("User not found")
        
        if not user.is_active:
            logger.warning("User is inactive", user_id=user_id, username=user.username)
            raise UnauthorizedException("User is inactive")
        
        logger.info("User authenticated successfully", user_id=str(user.id), username=user.username)
        return user
    except Exception as e:
        logger.error("Error in get_current_user", error=str(e), error_type=type(e).__name__, exc_info=True)
        raise


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    logger.info("get_current_active_user called", 
                current_user_type=type(current_user).__name__,
                is_user_instance=isinstance(current_user, User))
    
    # Check if we got a function instead of User object (dependency resolution issue)
    if not isinstance(current_user, User):
        logger.error("get_current_active_user received non-User object", 
                    received_type=type(current_user).__name__,
                    received_value=str(current_user)[:100])
        raise UnauthorizedException("Authentication failed: invalid user object")
    
    if not current_user.is_active:
        logger.warning("User is inactive", user_id=str(current_user.id))
        raise UnauthorizedException("User is inactive")
    
    logger.debug("Active user verified", user_id=str(current_user.id))
    return current_user


def require_permission(permission: str):
    """Dependency to require specific permission"""
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.is_active:
            raise UnauthorizedException("User is inactive")
        has_permission = await current_user.has_permission(permission)
        if not has_permission:
            from app.core.exceptions import ForbiddenException
            raise ForbiddenException(f"Permission required: {permission}")
        return current_user
    return permission_checker


def require_role(role: str):
    """Dependency to require specific role"""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.is_active:
            raise UnauthorizedException("User is inactive")
        if not current_user.has_role(role):
            from app.core.exceptions import ForbiddenException
            raise ForbiddenException(f"Role required: {role}")
        return current_user
    return role_checker
