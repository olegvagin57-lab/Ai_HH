"""Authentication API schemas"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=72)
    full_name: Optional[str] = Field(None, max_length=200)
    company_name: Optional[str] = Field(None, max_length=200)
    position: Optional[str] = Field(None, max_length=200)


class UserLogin(BaseModel):
    """User login request"""
    email_or_username: str
    password: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class UserResponse(BaseModel):
    """User response"""
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    position: Optional[str] = None
    is_active: bool
    is_verified: bool
    role_names: list[str]
    created_at: str
    last_login: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    """Login response with tokens and user"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
