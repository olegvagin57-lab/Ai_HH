"""Notifications API routes"""
from fastapi import APIRouter, Depends, Query, status
from app.api.v1.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    MarkReadResponse,
    MarkAllReadResponse
)
from app.application.services.notification_service import notification_service
from app.api.middleware.auth import get_current_user
from app.domain.entities.user import User
from app.core.logging import get_logger
from app.core.exceptions import NotFoundException


logger = get_logger(__name__)
router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    unread_only: bool = Query(False),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user)
):
    """Get notifications for current user"""
    result = await notification_service.get_user_notifications(
        user_id=str(current_user.id),
        unread_only=unread_only,
        limit=limit,
        page=page
    )
    
    notification_list = []
    for notification in result["notifications"]:
        notification_list.append(NotificationResponse(
            id=str(notification.id),
            user_id=notification.user_id,
            type=notification.type,
            title=notification.title,
            message=notification.message,
            data=notification.data,
            read=notification.read,
            created_at=notification.created_at.isoformat(),
            read_at=notification.read_at.isoformat() if notification.read_at else None
        ))
    
    return NotificationListResponse(
        notifications=notification_list,
        total=result["total"],
        page=result["page"],
        limit=result["limit"],
        unread_count=result["unread_count"]
    )


@router.patch("/{notification_id}/read", response_model=MarkReadResponse)
async def mark_notification_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """Mark notification as read"""
    notification = await notification_service.mark_as_read(
        notification_id=notification_id,
        user_id=str(current_user.id)
    )
    
    return MarkReadResponse(
        notification_id=str(notification.id),
        read=notification.read
    )


@router.post("/read-all", response_model=MarkAllReadResponse)
async def mark_all_as_read(
    current_user: User = Depends(get_current_user)
):
    """Mark all notifications as read"""
    count = await notification_service.mark_all_as_read(str(current_user.id))
    
    return MarkAllReadResponse(marked_count=count)


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a notification"""
    await notification_service.delete_notification(
        notification_id=notification_id,
        user_id=str(current_user.id)
    )
