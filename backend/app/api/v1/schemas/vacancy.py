"""Vacancy API schemas"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class VacancyCreate(BaseModel):
    """Create vacancy request"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    requirements: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1, max_length=100)
    search_query: str = Field(..., min_length=1, max_length=500)
    search_city: str = Field(..., min_length=1, max_length=100)
    remote: bool = False
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    currency: str = Field(default="RUR", max_length=10)


class VacancyUpdate(BaseModel):
    """Update vacancy request"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    requirements: Optional[str] = None
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    search_query: Optional[str] = Field(None, min_length=1, max_length=500)
    search_city: Optional[str] = Field(None, min_length=1, max_length=100)
    remote: Optional[bool] = None
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)


class AutoMatchingSettings(BaseModel):
    """Auto-matching settings"""
    enabled: Optional[bool] = None
    frequency: Optional[str] = Field(None, pattern="^(daily|twice_weekly|weekly|manual)$")
    min_score: Optional[int] = Field(None, ge=1, le=10)
    max_notifications: Optional[int] = Field(None, ge=1, le=50)


class VacancyResponse(BaseModel):
    """Vacancy response"""
    id: str
    user_id: str
    title: str
    description: str
    requirements: str
    city: str
    remote: bool
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: str
    status: str
    search_query: str
    search_city: str
    auto_matching_enabled: bool
    auto_matching_frequency: str
    auto_matching_min_score: int
    auto_matching_max_notifications: int
    last_auto_match_at: Optional[str] = None
    auto_match_count: int
    candidate_ids: List[str]
    search_ids: List[str]
    created_at: str
    updated_at: str
    closed_at: Optional[str] = None


class VacancyListResponse(BaseModel):
    """Vacancy list response"""
    vacancies: List[VacancyResponse]
    total: int
    page: int
    page_size: int
