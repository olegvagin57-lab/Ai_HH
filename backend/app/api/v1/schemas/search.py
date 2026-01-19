"""Search API schemas"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class SearchCreate(BaseModel):
    """Create search request"""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query (max 1000 characters)")
    city: str = Field(..., min_length=1, max_length=100, description="City name (max 100 characters)")


class SearchResponse(BaseModel):
    """Search response"""
    id: str
    user_id: str
    query: str
    city: str
    status: str
    total_found: int
    analyzed_count: int
    processed_count: int = 0  # Progress: how many resumes processed
    total_to_process: int = 0  # Progress: total resumes to process
    created_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


class EvaluationDetailsResponse(BaseModel):
    """Evaluation details for a category"""
    score: float
    details: str


class ResumeResponse(BaseModel):
    """Resume response with semantic analysis"""
    id: str
    search_id: str
    hh_id: Optional[str] = None
    hh_url: Optional[str] = None  # Link to HeadHunter resume
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
    evaluation_details: Optional[Dict[str, Any]] = None
    match_percentage: Optional[float] = None
    match_explanation: Optional[str] = None  # Detailed explanation why candidate matches
    strengths: List[str] = Field(default_factory=list)  # Key strengths
    weaknesses: List[str] = Field(default_factory=list)  # Areas for improvement
    recommendation: Optional[str] = None  # AI recommendation
    red_flags: List[str] = Field(default_factory=list)
    interview_focus: Optional[str] = None  # What to focus on during interview
    career_trajectory: Optional[str] = None  # Career trajectory analysis
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
