"""User domain entities"""
from datetime import datetime
from typing import List, Optional
from beanie import Document, Indexed
from pydantic import Field, field_validator
from pydantic import EmailStr
from pymongo import IndexModel


class Permission(Document):
    """Permission entity"""
    name: Indexed(str, unique=True)
    display_name: str
    description: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "permissions"
        indexes = [
            IndexModel([("name", 1)], name="name_1", unique=True),
        ]


class Role(Document):
    """Role entity"""
    name: Indexed(str, unique=True)
    display_name: str
    description: Optional[str] = None
    permission_names: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "roles"
        indexes = [
            IndexModel([("name", 1)], name="name_1", unique=True),
        ]
    
    def has_permission(self, permission: str) -> bool:
        """Check if role has specific permission"""
        return permission in self.permission_names


class User(Document):
    """User entity"""
    email: Indexed(str, unique=True)
    username: Indexed(str, unique=True)
    full_name: Optional[str] = None
    hashed_password: str
    
    # Status fields
    is_active: bool = True
    is_verified: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Company info
    company_name: Optional[str] = None
    position: Optional[str] = None
    
    # Roles (list of role names)
    role_names: List[str] = Field(default_factory=list)
    
    class Settings:
        name = "users"
        indexes = [
            IndexModel([("email", 1)], name="email_1", unique=True),
            IndexModel([("username", 1)], name="username_1", unique=True),
            IndexModel([("is_active", 1)], name="is_active_1"),
        ]
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has specific role"""
        return role_name in self.role_names
    
    async def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission through roles"""
        from app.domain.entities.user import Role
        roles = await Role.find({"name": {"$in": self.role_names}}).to_list()
        for role in roles:
            if role.has_permission(permission):
                return True
        return False
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.has_role("admin")
    
    def can_create_searches(self) -> bool:
        """Check if user can create searches"""
        return any(role in self.role_names for role in ["admin", "hr_manager", "hr_specialist"])
    
    def can_view_all_searches(self) -> bool:
        """Check if user can view all searches"""
        return any(role in self.role_names for role in ["admin", "hr_manager"])
    
    def can_export_all_searches(self) -> bool:
        """Check if user can export all searches"""
        return any(role in self.role_names for role in ["admin", "hr_manager"])
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format"""
        from email_validator import validate_email, EmailNotValidError
        import re
        # Basic email regex check first
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError(f"Invalid email format: {v}")
        # Try full validation with check_deliverability=False to avoid DNS checks
        try:
            validate_email(v, check_deliverability=False)
            return v.lower().strip()
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email format: {v}")


class UserSession(Document):
    """User session entity"""
    user_id: str  # User document ID
    session_token: Indexed(str, unique=True)
    refresh_token: Optional[Indexed(str, unique=True)] = None
    
    # Session info
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    last_used: datetime = Field(default_factory=datetime.utcnow)
    
    # Status
    is_active: bool = True
    
    class Settings:
        name = "user_sessions"
        indexes = [
            IndexModel([("session_token", 1)], name="session_token_1", unique=True),
            IndexModel([("refresh_token", 1)], name="refresh_token_1", unique=True, sparse=True),
            IndexModel([("user_id", 1)], name="user_id_1"),
            IndexModel([("expires_at", 1)], name="expires_at_1", expireAfterSeconds=0),  # TTL index
        ]
