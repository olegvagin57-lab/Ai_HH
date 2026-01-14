"""Vacancy domain entities"""
from typing import List, Optional, Dict, Any
from beanie import Document
from pydantic import Field
from datetime import datetime
from pymongo import IndexModel


class Vacancy(Document):
    """Vacancy entity"""
    user_id: str  # User who created the vacancy
    title: str  # Job title
    description: str  # Job description
    requirements: str  # Job requirements
    
    # Location
    city: str
    remote: bool = False  # Remote work available
    
    # Salary
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: str = "RUR"
    
    # Status
    status: str = Field(default="draft")  # draft, active, paused, closed, filled
    
    # Search settings
    search_query: str  # Query for searching resumes
    search_city: str  # City for search
    
    # Auto-matching settings
    auto_matching_enabled: bool = False
    auto_matching_frequency: str = Field(default="weekly")  # daily, twice_weekly, weekly, manual
    auto_matching_min_score: int = Field(default=7, ge=1, le=10)  # Minimum AI score for notifications
    auto_matching_max_notifications: int = Field(default=10, ge=1, le=50)  # Max new candidates to notify about
    
    # Last auto-matching run
    last_auto_match_at: Optional[datetime] = None
    auto_match_count: int = 0  # Total candidates found via auto-matching
    
    # Associated candidates
    candidate_ids: List[str] = Field(default_factory=list)  # Resume IDs associated with this vacancy
    
    # Search history
    search_ids: List[str] = Field(default_factory=list)  # Search IDs (manual and automatic)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None
    
    class Settings:
        name = "vacancies"
        indexes = [
            IndexModel([("user_id", 1)], name="user_id_1"),
            IndexModel([("status", 1)], name="status_1"),
            IndexModel([("auto_matching_enabled", 1)], name="auto_matching_enabled_1"),
            IndexModel([("created_at", -1)], name="created_at_-1"),
        ]
    
    def activate(self) -> None:
        """Activate vacancy"""
        if self.status == "draft":
            self.status = "active"
            self.updated_at = datetime.utcnow()
    
    def pause(self) -> None:
        """Pause vacancy"""
        if self.status == "active":
            self.status = "paused"
            self.updated_at = datetime.utcnow()
    
    def close(self) -> None:
        """Close vacancy"""
        self.status = "closed"
        self.closed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def fill(self) -> None:
        """Mark vacancy as filled"""
        self.status = "filled"
        self.closed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def add_candidate(self, resume_id: str) -> None:
        """Add candidate to vacancy"""
        if resume_id not in self.candidate_ids:
            self.candidate_ids.append(resume_id)
            self.updated_at = datetime.utcnow()
    
    def remove_candidate(self, resume_id: str) -> None:
        """Remove candidate from vacancy"""
        if resume_id in self.candidate_ids:
            self.candidate_ids.remove(resume_id)
            self.updated_at = datetime.utcnow()
    
    def add_search(self, search_id: str) -> None:
        """Add search to vacancy history"""
        if search_id not in self.search_ids:
            self.search_ids.append(search_id)
            self.updated_at = datetime.utcnow()
