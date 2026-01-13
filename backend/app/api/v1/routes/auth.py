"""Authentication API routes"""
from fastapi import APIRouter, Depends, Request, status
from fastapi.security import HTTPBearer
from app.api.v1.schemas.auth import (
    UserRegister,
    UserLogin,
    LoginResponse,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse
)
from app.dependencies import get_auth_service
from app.application.services.auth_service import AuthService
from app.api.middleware.auth import get_current_active_user
from app.domain.entities.user import User
from app.core.logging import get_logger
from app.core.exceptions import ValidationException


logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user"""
    logger.info("Registration request", 
                email=user_data.email,
                username=user_data.username)
    try:
        logger.debug("Calling auth_service.register_user")
        user = await auth_service.register_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name,
            company_name=user_data.company_name,
            position=user_data.position
        )
        
        logger.info("User registered successfully", 
                   user_id=str(user.id),
                   email=user.email,
                   username=user.username)
        
        return UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            company_name=user.company_name,
            position=user.position,
            is_active=user.is_active,
            is_verified=user.is_verified,
            role_names=user.role_names,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None
        )
    except ValidationException as ve:
        logger.warning("Validation error during registration", error=str(ve))
        raise
    except Exception as e:
        logger.error("Registration error", 
                    error=str(e), 
                    error_type=type(e).__name__,
                    exc_info=True)
        raise ValidationException("Registration failed")


@router.post("/login", response_model=LoginResponse)
async def login_user(
    credentials: UserLogin,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Authenticate user and return tokens"""
    logger.info("Login request", 
                email_or_username=credentials.email_or_username)
    
    try:
        # Get client info
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        logger.debug("Client info", ip_address=ip_address)
        
        # Authenticate user
        logger.debug("Authenticating user")
        user = await auth_service.authenticate_user(
            credentials.email_or_username,
            credentials.password
        )
        
        if not user:
            logger.warning("Authentication failed", 
                         email_or_username=credentials.email_or_username)
            raise ValidationException("Incorrect email/username or password")
        
        logger.info("User authenticated", 
                   user_id=str(user.id),
                   username=user.username)
        
        # Create session
        logger.debug("Creating user session")
        tokens = await auth_service.create_user_session(
            user, ip_address, user_agent
        )
        
        logger.info("Login successful", 
                   user_id=str(user.id),
                   has_access_token=bool(tokens.get("access_token")))
        
        # Convert user to response
        user_response = UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            company_name=user.company_name,
            position=user.position,
            is_active=user.is_active,
            is_verified=user.is_verified,
            role_names=user.role_names,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None
        )
        
        return LoginResponse(
            **tokens,
            user=user_response
        )
    except ValidationException as ve:
        logger.warning("Validation error during login", error=str(ve))
        raise
    except Exception as e:
        logger.error("Login error", 
                    error=str(e), 
                    error_type=type(e).__name__,
                    exc_info=True)
        raise


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Refresh access token"""
    tokens = await auth_service.refresh_access_token(token_data.refresh_token)
    return TokenResponse(**tokens)


@router.post("/logout")
async def logout_user(
    current_user: User = Depends(get_current_active_user),
    credentials: HTTPBearer = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Logout user"""
    token = credentials.credentials
    await auth_service.logout(token)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        company_name=current_user.company_name,
        position=current_user.position,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        role_names=current_user.role_names,
        created_at=current_user.created_at.isoformat(),
        last_login=current_user.last_login.isoformat() if current_user.last_login else None
    )
