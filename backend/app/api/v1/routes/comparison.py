"""Candidate comparison API routes"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from app.api.v1.schemas.search import ResumeResponse
from app.domain.entities.search import Resume
from app.api.middleware.auth import get_current_user
from app.domain.entities.user import User
from app.core.logging import get_logger
from app.core.exceptions import ValidationException
from pydantic import BaseModel


logger = get_logger(__name__)
router = APIRouter(prefix="/comparison", tags=["comparison"])


class ComparisonResponse(BaseModel):
    """Comparison response"""
    resumes: List[ResumeResponse]
    comparison_metrics: Dict[str, Any]


@router.post("", response_model=ComparisonResponse)
async def compare_candidates(
    resume_ids: List[str] = Query(..., min_length=2, max_length=5),
    current_user: User = Depends(get_current_user)
):
    """Compare multiple candidates side-by-side"""
    if len(resume_ids) < 2:
        raise ValidationException("At least 2 candidates required for comparison")
    if len(resume_ids) > 5:
        raise ValidationException("Maximum 5 candidates allowed for comparison")
    
    # Get all resumes
    resumes = []
    for resume_id in resume_ids:
        resume = await Resume.get(resume_id)
        if not resume:
            raise ValidationException(f"Resume not found: {resume_id}")
        resumes.append(resume)
    
    # Build comparison metrics
    comparison_metrics = {
        "ai_scores": {str(r.id): r.ai_score for r in resumes if r.ai_score},
        "match_percentages": {str(r.id): r.match_percentage for r in resumes if r.match_percentage},
        "preliminary_scores": {str(r.id): r.preliminary_score for r in resumes if r.preliminary_score},
        "average_ai_score": sum(r.ai_score for r in resumes if r.ai_score) / len([r for r in resumes if r.ai_score]) if any(r.ai_score for r in resumes) else None,
        "average_match_percentage": sum(r.match_percentage for r in resumes if r.match_percentage) / len([r for r in resumes if r.match_percentage]) if any(r.match_percentage for r in resumes) else None,
        "evaluation_categories": {}
    }
    
    # Compare evaluation details by category
    categories = ["technical_skills", "experience", "education", "soft_skills"]
    for category in categories:
        category_scores = {}
        for resume in resumes:
            if resume.evaluation_details and category in resume.evaluation_details:
                category_data = resume.evaluation_details[category]
                if isinstance(category_data, dict) and "score" in category_data:
                    category_scores[str(resume.id)] = category_data["score"]
        if category_scores:
            comparison_metrics["evaluation_categories"][category] = category_scores
    
    # Build resume responses
    resume_list = []
    for resume in resumes:
        resume_list.append(ResumeResponse(
            id=str(resume.id),
            search_id=str(resume.search_id),
            hh_id=resume.hh_id,
            name=resume.name,
            age=resume.age,
            city=resume.city,
            title=resume.title,
            salary=resume.salary,
            currency=resume.currency,
            preliminary_score=resume.preliminary_score,
            ai_score=resume.ai_score,
            ai_summary=resume.ai_summary,
            ai_questions=resume.ai_questions,
            ai_generated_detected=resume.ai_generated_detected,
            analyzed=resume.analyzed,
            evaluation_details=resume.evaluation_details,
            match_percentage=resume.match_percentage,
            match_explanation=resume.match_explanation,
            strengths=resume.strengths or [],
            weaknesses=resume.weaknesses or [],
            recommendation=resume.recommendation,
            red_flags=resume.red_flags or [],
            created_at=resume.created_at.isoformat()
        ))
    
    logger.info("Candidates compared", count=len(resumes), user_id=str(current_user.id))
    
    return ComparisonResponse(
        resumes=resume_list,
        comparison_metrics=comparison_metrics
    )
