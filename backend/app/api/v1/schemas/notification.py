"""Notification API schemas"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class NotificationResponse(BaseModel):
    """Notification response"""
    id: str
    user_id: str
    type: str
    title: str
    message: str
    data: Dict[str, Any]
    read: bool
    created_at: str
    read_at: Optional[str] = None


class NotificationListResponse(BaseModel):
    """Notification list response"""
    notifications: List[NotificationResponse]
    total: int
    page: int
    limit: int
    unread_count: int


class MarkReadResponse(BaseModel):
    """Mark as read response"""
    notification_id: str
    read: bool


class MarkAllReadResponse(BaseModel):
    """Mark all as read response"""
    marked_count: int
