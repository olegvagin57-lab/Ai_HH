"""User management API routes"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, Query, status
from app.api.v1.schemas.user import UserUpdate, UserListResponse
from app.api.v1.schemas.auth import UserResponse
from app.dependencies import get_auth_service
from app.application.services.auth_service import AuthService
from app.api.middleware.auth import get_current_active_user, require_role
from app.domain.entities.user import User
from app.core.logging import get_logger
from app.core.exceptions import NotFoundException, ForbiddenException, ValidationException


logger = get_logger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role("admin"))
):
    """List all users (admin only)"""
    skip = (page - 1) * page_size
    
    users = await User.find_all().skip(skip).limit(page_size).to_list()
    total = await User.find_all().count()
    
    user_list = []
    for user in users:
        user_list.append({
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "company_name": user.company_name,
            "position": user.position,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "role_names": user.role_names,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None
        })
    
    return UserListResponse(
        users=user_list,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_role("admin")),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get user by ID (admin only)"""
    user = await auth_service.get_user_by_id(user_id)
    
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


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(require_role("admin")),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Update user (admin only)"""
    user = await auth_service.get_user_by_id(user_id)
    
    # Update fields
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.company_name is not None:
        user.company_name = user_update.company_name
    if user_update.position is not None:
        user.position = user_update.position
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    if user_update.role_names is not None:
        # Validate roles exist
        from app.domain.entities.user import Role
        existing_roles = await Role.find({"name": {"$in": user_update.role_names}}).to_list()
        existing_role_names = {role.name for role in existing_roles}
        invalid_roles = set(user_update.role_names) - existing_role_names
        if invalid_roles:
            raise ValidationException(f"Invalid roles: {', '.join(invalid_roles)}")
        user.role_names = user_update.role_names
    
    user.updated_at = datetime.utcnow()
    await user.save()
    
    logger.info("User updated", user_id=str(user.id), updated_by=str(current_user.id))
    
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


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_role("admin")),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Delete user (admin only)"""
    user = await auth_service.get_user_by_id(user_id)
    
    # Prevent self-deletion
    if str(user.id) == str(current_user.id):
        raise ForbiddenException("Cannot delete yourself")
    
    await user.delete()
    
    logger.info("User deleted", user_id=str(user.id), deleted_by=str(current_user.id))
