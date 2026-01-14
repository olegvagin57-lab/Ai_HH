"""Collaboration API schemas"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class CommentCreate(BaseModel):
    """Create comment request"""
    content: str = Field(..., min_length=1, max_length=5000)
    parent_comment_id: Optional[str] = None
    is_internal: bool = True


class CommentUpdate(BaseModel):
    """Update comment request"""
    content: str = Field(..., min_length=1, max_length=5000)


class CommentResponse(BaseModel):
    """Comment response"""
    id: str
    resume_id: str
    user_id: str
    content: str
    mentions: List[str]
    parent_comment_id: Optional[str] = None
    is_internal: bool
    created_at: str
    updated_at: str


class CommentListResponse(BaseModel):
    """Comment list response"""
    comments: List[CommentResponse]
    total: int


class ActivityItem(BaseModel):
    """Activity feed item"""
    type: str
    id: str
    resume_id: str
    user_id: str
    content: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None
    created_at: str


class ActivityFeedResponse(BaseModel):
    """Activity feed response"""
    activities: List[ActivityItem]
    total: int


class RatingsSummaryResponse(BaseModel):
    """Ratings summary response"""
    average_rating: Optional[float] = None
    total_ratings: int
    ratings_breakdown: Dict[int, int]
