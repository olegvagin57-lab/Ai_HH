"""Candidate management entities"""
from typing import List, Optional, Dict, Any
from beanie import Document
from pydantic import Field
from datetime import datetime
from pymongo import IndexModel


class Interaction(Document):
    """History of interactions with a candidate"""
    resume_id: str  # Reference to Resume
    user_id: str  # User who performed the action
    action_type: str  # e.g., "status_changed", "comment_added", "tag_added", "rating_added"
    action_data: Dict[str, Any] = Field(default_factory=dict)  # Additional data for the action
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "interactions"
        indexes = [
            IndexModel([("resume_id", 1)], name="resume_id_1"),
            IndexModel([("user_id", 1)], name="user_id_1"),
            IndexModel([("created_at", -1)], name="created_at_-1"),
        ]


class Candidate(Document):
    """Extended candidate information (extends Resume)"""
    resume_id: str  # Reference to Resume (one-to-one relationship)
    
    # Status pipeline
    status: str = Field(default="new")  # new, reviewed, shortlisted, interview_scheduled, interviewed, offer_sent, hired, rejected, on_hold
    
    # Organization
    tags: List[str] = Field(default_factory=list)  # Tags like "Senior", "Remote", "Urgent"
    folder: Optional[str] = None  # Folder/collection name
    
    # Assignment
    assigned_to_user_id: Optional[str] = None  # Assigned HR specialist
    
    # Ratings
    ratings: Dict[str, int] = Field(default_factory=dict)  # {user_id: rating (1-5)}
    average_rating: Optional[float] = None  # Calculated average rating
    
    # Notes
    notes: Optional[str] = None  # General notes about the candidate
    
    # Vacancy associations
    vacancy_ids: List[str] = Field(default_factory=list)  # Vacancies this candidate is associated with
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status_changed_at: Optional[datetime] = None
    
    class Settings:
        name = "candidates"
        indexes = [
            IndexModel([("resume_id", 1)], name="resume_id_1", unique=True),  # One candidate per resume
            IndexModel([("status", 1)], name="status_1"),
            IndexModel([("assigned_to_user_id", 1)], name="assigned_to_user_id_1"),
            IndexModel([("folder", 1)], name="folder_1"),
            IndexModel([("tags", 1)], name="tags_1"),
            IndexModel([("vacancy_ids", 1)], name="vacancy_ids_1"),
        ]
    
    def update_status(self, new_status: str) -> None:
        """Update candidate status"""
        self.status = new_status
        self.status_changed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the candidate"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the candidate"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()
    
    def add_rating(self, user_id: str, rating: int) -> None:
        """Add or update a rating from a user"""
        if 1 <= rating <= 5:
            self.ratings[user_id] = rating
            self._calculate_average_rating()
            self.updated_at = datetime.utcnow()
    
    def _calculate_average_rating(self) -> None:
        """Calculate average rating"""
        if self.ratings:
            self.average_rating = sum(self.ratings.values()) / len(self.ratings)
        else:
            self.average_rating = None
    
    def add_to_vacancy(self, vacancy_id: str) -> None:
        """Add candidate to a vacancy"""
        if vacancy_id not in self.vacancy_ids:
            self.vacancy_ids.append(vacancy_id)
            self.updated_at = datetime.utcnow()
    
    def remove_from_vacancy(self, vacancy_id: str) -> None:
        """Remove candidate from a vacancy"""
        if vacancy_id in self.vacancy_ids:
            self.vacancy_ids.remove(vacancy_id)
            self.updated_at = datetime.utcnow()
