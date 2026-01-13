"""Search domain entities"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from beanie import Document, Indexed
from pydantic import Field
from pymongo import IndexModel


class Concept(Document):
    """Extracted concepts from search query"""
    search_id: str
    concepts: List[List[str]]  # Array of arrays: [["concept1", "synonym1"], ["concept2", "synonym2"]]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "concepts"
        indexes = [
            IndexModel([("search_id", 1)]),
        ]


class Resume(Document):
    """Resume entity"""
    search_id: str
    hh_id: Optional[str] = None  # HeadHunter resume ID
    
    # Basic info
    name: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None
    title: Optional[str] = None
    
    # Salary
    salary: Optional[int] = None
    currency: Optional[str] = None
    
    # Raw data from HeadHunter
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Scoring
    preliminary_score: Optional[float] = None
    ai_score: Optional[int] = Field(default=None, ge=1, le=10)
    
    # AI Analysis
    ai_summary: Optional[str] = None
    ai_questions: List[str] = Field(default_factory=list)
    ai_generated_detected: bool = False
    analyzed: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "resumes"
        indexes = [
            IndexModel([("search_id", 1)]),
            IndexModel([("hh_id", 1)], unique=True, sparse=True),  # Unique index, sparse allows null values
            IndexModel([("ai_score", -1)]),  # Descending for sorting
            IndexModel([("preliminary_score", -1)]),
        ]


class Search(Document):
    """Search entity"""
    user_id: str
    city: str
    query: str
    
    # Status
    status: str = Field(default="pending")  # pending, processing, completed, failed
    
    # Results
    total_found: int = 0
    analyzed_count: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Error handling
    error_message: Optional[str] = None
    
    # Settings
    settings: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "searches"
        indexes = [
            IndexModel([("user_id", 1)]),
            IndexModel([("status", 1)]),
            IndexModel([("created_at", -1)]),  # Descending for recent first
        ]
