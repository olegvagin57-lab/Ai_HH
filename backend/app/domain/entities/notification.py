"""Notification entities"""
from typing import Optional, Dict, Any
from beanie import Document
from pydantic import Field
from datetime import datetime
from pymongo import IndexModel


class Notification(Document):
    """User notification"""
    user_id: str  # User who should receive the notification
    type: str  # notification type: new_candidate, status_changed, comment_added, auto_match_found, etc.
    title: str  # Notification title
    message: str  # Notification message
    data: Dict[str, Any] = Field(default_factory=dict)  # Additional data (resume_id, vacancy_id, etc.)
    read: bool = False  # Whether notification has been read
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None
    
    class Settings:
        name = "notifications"
        indexes = [
            IndexModel([("user_id", 1)], name="user_id_1"),
            IndexModel([("read", 1)], name="read_1"),
            IndexModel([("created_at", -1)], name="created_at_-1"),
            IndexModel([("user_id", 1), ("read", 1)], name="user_id_1_read_1"),  # Compound index for unread notifications
        ]
    
    def mark_as_read(self) -> None:
        """Mark notification as read"""
        self.read = True
        self.read_at = datetime.utcnow()
