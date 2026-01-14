"""Comment entities for collaboration"""
from typing import Optional, List
from beanie import Document
from pydantic import Field
from datetime import datetime
from pymongo import IndexModel


class Comment(Document):
    """Comment on a candidate"""
    resume_id: str  # Reference to Resume
    user_id: str  # User who created the comment
    content: str  # Comment text
    mentions: List[str] = Field(default_factory=list)  # List of mentioned user IDs (@mentions)
    parent_comment_id: Optional[str] = None  # For threaded comments
    is_internal: bool = True  # Internal comment (not visible to candidate)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "comments"
        indexes = [
            IndexModel([("resume_id", 1)], name="resume_id_1"),
            IndexModel([("user_id", 1)], name="user_id_1"),
            IndexModel([("parent_comment_id", 1)], name="parent_comment_id_1"),
            IndexModel([("created_at", -1)], name="created_at_-1"),
        ]
