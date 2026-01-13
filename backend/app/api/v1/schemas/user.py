"""User management API schemas"""
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class UserUpdate(BaseModel):
    """User update request"""
    full_name: Optional[str] = Field(None, max_length=200)
    company_name: Optional[str] = Field(None, max_length=200)
    position: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None
    role_names: Optional[List[str]] = None


class UserListResponse(BaseModel):
    """User list response"""
    users: List[dict]
    total: int
    page: int
    page_size: int
