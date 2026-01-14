"""Candidate API schemas"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class CandidateResponse(BaseModel):
    """Candidate response"""
    resume_id: str
    status: str
    tags: List[str]
    folder: Optional[str] = None
    assigned_to_user_id: Optional[str] = None
    ratings: Dict[str, int]
    average_rating: Optional[float] = None
    notes: Optional[str] = None
    vacancy_ids: List[str]
    created_at: str
    updated_at: str
    status_changed_at: Optional[str] = None


class InteractionResponse(BaseModel):
    """Interaction response"""
    id: str
    resume_id: str
    user_id: str
    action_type: str
    action_data: Dict[str, Any]
    created_at: str


class UpdateStatusRequest(BaseModel):
    """Update candidate status request"""
    status: str = Field(..., pattern="^(new|reviewed|shortlisted|interview_scheduled|interviewed|offer_sent|hired|rejected|on_hold)$")


class AddTagRequest(BaseModel):
    """Add tag request"""
    tag: str = Field(..., min_length=1, max_length=50)


class AssignRequest(BaseModel):
    """Assign candidate request"""
    assigned_to_user_id: str


class AddRatingRequest(BaseModel):
    """Add rating request"""
    rating: int = Field(..., ge=1, le=5)


class UpdateNotesRequest(BaseModel):
    """Update notes request"""
    notes: str = Field(default="")


class SetFolderRequest(BaseModel):
    """Set folder request"""
    folder: Optional[str] = Field(None, max_length=100)


class CandidateListResponse(BaseModel):
    """Candidate list response"""
    candidates: List[CandidateResponse]
    total: int
    page: int
    page_size: int


class InteractionListResponse(BaseModel):
    """Interaction list response"""
    interactions: List[InteractionResponse]
    total: int
