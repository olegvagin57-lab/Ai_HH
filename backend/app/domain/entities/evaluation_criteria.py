"""Evaluation criteria entities"""
from typing import Dict, Optional, List, Any
from beanie import Document
from pydantic import Field
from datetime import datetime
from pymongo import IndexModel


class EvaluationCriteria(Document):
    """Evaluation criteria configuration for vacancies"""
    vacancy_id: Optional[str] = None  # If None, it's a default/global criteria
    name: str  # Criteria name (e.g., "Python Developer")
    
    # Category weights (sum should be 1.0)
    weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "technical_skills": 0.4,
            "experience": 0.3,
            "education": 0.2,
            "soft_skills": 0.1
        }
    )
    
    # Category-specific settings
    technical_skills: Dict[str, Any] = Field(default_factory=dict)  # Required skills, technologies
    experience: Dict[str, Any] = Field(default_factory=dict)  # Min years, relevant industries
    education: Dict[str, Any] = Field(default_factory=dict)  # Required degrees, certifications
    soft_skills: Dict[str, Any] = Field(default_factory=dict)  # Communication, leadership, etc.
    
    # Red flags configuration
    red_flags: List[str] = Field(default_factory=lambda: [
        "ai_generated",
        "incomplete_resume",
        "suspicious_data",
        "job_hopping",
        "skill_mismatch"
    ])
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "evaluation_criteria"
        indexes = [
            IndexModel([("vacancy_id", 1)], name="vacancy_id_1"),
        ]
