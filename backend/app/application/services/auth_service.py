"""Authentication service"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.core.security import security_service
from app.core.logging import get_logger
from app.core.exceptions import ValidationException, UnauthorizedException, NotFoundException
from app.domain.entities.user import User, Role, Permission, UserSession
from app.config import settings


logger = get_logger(__name__)


class AuthService:
    """Service for authentication and authorization"""
    
    async def initialize_default_roles_and_permissions(self) -> None:
        """Initialize default roles and permissions"""
        # Define permissions
        permissions = [
            {"name": "search:create", "display_name": "Create Search", "category": "search"},
            {"name": "search:view", "display_name": "View Search", "category": "search"},
            {"name": "search:view_all", "display_name": "View All Searches", "category": "search"},
            {"name": "search:export", "display_name": "Export Search", "category": "search"},
            {"name": "search:export_all", "display_name": "Export All Searches", "category": "search"},
            {"name": "user:view", "display_name": "View User", "category": "user"},
            {"name": "user:manage", "display_name": "Manage Users", "category": "user"},
            {"name": "admin:access", "display_name": "Admin Access", "category": "admin"},
        ]
        
        # Create permissions
        for perm_data in permissions:
            existing = await Permission.find_one({"name": perm_data["name"]})
            if not existing:
                await Permission(**perm_data).create()
                logger.info("Created permission", permission=perm_data["name"])
        
        # Define roles
        roles = [
            {
                "name": "admin",
                "display_name": "Administrator",
                "description": "Full system access",
                "permission_names": [p["name"] for p in permissions]
            },
            {
                "name": "hr_manager",
                "display_name": "HR Manager",
                "description": "Can create searches, view all searches, export all",
                "permission_names": [
                    "search:create", "search:view", "search:view_all",
                    "search:export", "search:export_all", "user:view"
                ]
            },
            {
                "name": "hr_specialist",
                "display_name": "HR Specialist",
                "description": "Can create searches and view own searches",
                "permission_names": ["search:create", "search:view", "search:export"]
            },
            {
                "name": "viewer",
                "display_name": "Viewer",
                "description": "Can only view searches",
                "permission_names": ["search:view"]
            }
        ]
        
        # Create roles
        for role_data in roles:
            existing = await Role.find_one({"name": role_data["name"]})
            if not existing:
                await Role(**role_data).create()
                logger.info("Created role", role=role_data["name"])
    
    async def register_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
        company_name: Optional[str] = None,
        position: Optional[str] = None,
        role_names: Optional[list] = None
    ) -> User:
        """Register a new user"""
        # Validate password
        is_valid, message = security_service.validate_password_strength(password)
        if not is_valid:
            raise ValidationException(message)
        
        # Check if user exists
        existing_email = await User.find_one({"email": email})
        if existing_email:
            raise ValidationException("User with this email already exists")
        
        existing_username = await User.find_one({"username": username})
        if existing_username:
            raise ValidationException("User with this username already exists")
        
        # Hash password
        hashed_password = security_service.get_password_hash(password)
        
        # Default role - give hr_specialist to allow search creation
        if not role_names:
            role_names = ["hr_specialist"]
            logger.info("Assigning default role", role="hr_specialist")
        
        # Create user
        user = User(
            email=email,
            username=username,
            full_name=full_name,
            company_name=company_name,
            position=position,
            hashed_password=hashed_password,
            role_names=role_names,
            is_active=True,
            is_verified=False
        )
        
        await user.create()
        logger.info("User registered", user_id=str(user.id), email=email, username=username)
        
        return user
    
    async def authenticate_user(self, email_or_username: str, password: str) -> Optional[User]:
        """Authenticate user by email/username and password"""
        # Find user by email or username
        user = await User.find_one({
            "$or": [
                {"email": email_or_username},
                {"username": email_or_username}
            ]
        })
        
        if not user:
            return None
        
        # Check if user is active
        if not user.is_active:
            return None
        
        # Verify password
        if not security_service.verify_password(password, user.hashed_password):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        await user.save()
        
        logger.info("User authenticated", user_id=str(user.id), email=user.email)
        
        return user
    
    async def create_user_session(
        self,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, str]:
        """Create user session and return tokens"""
        # Create access token
        access_token = security_service.create_access_token(
            {"sub": str(user.id), "email": user.email, "username": user.username}
        )
        
        # Create refresh token
        refresh_token = security_service.create_refresh_token(
            {"sub": str(user.id)}
        )
        
        # Create session
        expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        session = UserSession(
            user_id=str(user.id),
            session_token=access_token,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at
        )
        
        await session.create()
        
        logger.info("User session created", user_id=str(user.id), session_id=str(session.id))
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """Refresh access token using refresh token"""
        # Verify refresh token
        payload = security_service.verify_token(refresh_token, token_type="refresh")
        if not payload:
            raise UnauthorizedException("Invalid refresh token")
        
        # Get user ID
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid token payload")
        
        # Find session
        session = await UserSession.find_one({"refresh_token": refresh_token, "is_active": True})
        if not session:
            raise UnauthorizedException("Session not found")
        
        # Check if session expired
        if session.expires_at < datetime.utcnow():
            session.is_active = False
            await session.save()
            raise UnauthorizedException("Session expired")
        
        # Get user
        user = await User.get(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")
        
        # Create new access token
        access_token = security_service.create_access_token(
            {"sub": str(user.id), "email": user.email, "username": user.username}
        )
        
        # Update session
        session.session_token = access_token
        session.last_used = datetime.utcnow()
        await session.save()
        
        logger.info("Access token refreshed", user_id=str(user.id))
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,  # Return same refresh token
            "token_type": "bearer"
        }
    
    async def logout(self, session_token: str) -> None:
        """Logout user by invalidating session"""
        session = await UserSession.find_one({"session_token": session_token})
        if session:
            session.is_active = False
            await session.save()
            logger.info("User logged out", session_id=str(session.id))
    
    async def get_user_by_id(self, user_id: str) -> User:
        """Get user by ID"""
        user = await User.get(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user
