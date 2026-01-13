"""Search API schemas"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class SearchCreate(BaseModel):
    """Create search request"""
    query: str = Field(..., min_length=1, max_length=500)
    city: str = Field(..., min_length=1, max_length=100)


class SearchResponse(BaseModel):
    """Search response"""
    id: str
    user_id: str
    query: str
    city: str
    status: str
    total_found: int
    analyzed_count: int
    created_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


class ResumeResponse(BaseModel):
    """Resume response"""
    id: str
    search_id: str
    hh_id: Optional[str] = None
    name: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None
    title: Optional[str] = None
    salary: Optional[int] = None
    currency: Optional[str] = None
    preliminary_score: Optional[float] = None
    ai_score: Optional[int] = None
    ai_summary: Optional[str] = None
    ai_questions: List[str] = Field(default_factory=list)
    ai_generated_detected: bool = False
    analyzed: bool = False
    created_at: str


class ResumeListResponse(BaseModel):
    """Resume list response"""
    resumes: List[ResumeResponse]
    total: int
    page: int
    page_size: int


class SearchListResponse(BaseModel):
    """Search list response"""
    searches: List[SearchResponse]
    total: int
    page: int
    page_size: int
