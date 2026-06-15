"""Vacancy management API routes"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from app.api.v1.schemas.vacancy import (
    VacancyCreate,
    VacancyUpdate,
    AutoMatchingSettings,
    VacancyResponse,
    VacancyListResponse
)
from app.application.services.vacancy_service import vacancy_service
from app.api.middleware.auth import get_current_user
from app.domain.entities.user import User
from app.domain.entities.search import Resume
from app.core.logging import get_logger
from app.core.exceptions import NotFoundException


logger = get_logger(__name__)
router = APIRouter(prefix="/vacancies", tags=["vacancies"])


@router.post("", response_model=VacancyResponse, status_code=status.HTTP_201_CREATED)
async def create_vacancy(
    vacancy_data: VacancyCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new vacancy"""
    vacancy = await vacancy_service.create_vacancy(
        user=current_user,
        title=vacancy_data.title,
        description=vacancy_data.description,
        requirements=vacancy_data.requirements,
        city=vacancy_data.city,
        search_query=vacancy_data.search_query,
        search_city=vacancy_data.search_city,
        remote=vacancy_data.remote,
        salary_min=vacancy_data.salary_min,
        salary_max=vacancy_data.salary_max,
        currency=vacancy_data.currency
    )
    
    return VacancyResponse(
        id=str(vacancy.id),
        user_id=vacancy.user_id,
        title=vacancy.title,
        description=vacancy.description,
        requirements=vacancy.requirements,
        city=vacancy.city,
        remote=vacancy.remote,
        salary_min=vacancy.salary_min,
        salary_max=vacancy.salary_max,
        currency=vacancy.currency,
        status=vacancy.status,
        search_query=vacancy.search_query,
        search_city=vacancy.search_city,
        auto_matching_enabled=vacancy.auto_matching_enabled,
        auto_matching_frequency=vacancy.auto_matching_frequency,
        auto_matching_min_score=vacancy.auto_matching_min_score,
        auto_matching_max_notifications=vacancy.auto_matching_max_notifications,
        last_auto_match_at=vacancy.last_auto_match_at.isoformat() if vacancy.last_auto_match_at else None,
        auto_match_count=vacancy.auto_match_count,
        candidate_ids=vacancy.candidate_ids,
        search_ids=vacancy.search_ids,
        created_at=vacancy.created_at.isoformat(),
        updated_at=vacancy.updated_at.isoformat(),
        closed_at=vacancy.closed_at.isoformat() if vacancy.closed_at else None
    )


@router.get("", response_model=VacancyListResponse)
async def list_vacancies(
    status: Optional[str] = Query(None, pattern="^(draft|active|paused|closed|filled)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """List vacancies"""
    result = await vacancy_service.list_vacancies(
        user=current_user,
        status=status,
        page=page,
        page_size=page_size
    )
    
    vacancy_list = []
    for vacancy in result["vacancies"]:
        vacancy_list.append(VacancyResponse(
            id=str(vacancy.id),
            user_id=vacancy.user_id,
            title=vacancy.title,
            description=vacancy.description,
            requirements=vacancy.requirements,
            city=vacancy.city,
            remote=vacancy.remote,
            salary_min=vacancy.salary_min,
            salary_max=vacancy.salary_max,
            currency=vacancy.currency,
            status=vacancy.status,
            search_query=vacancy.search_query,
            search_city=vacancy.search_city,
            auto_matching_enabled=vacancy.auto_matching_enabled,
            auto_matching_frequency=vacancy.auto_matching_frequency,
            auto_matching_min_score=vacancy.auto_matching_min_score,
            auto_matching_max_notifications=vacancy.auto_matching_max_notifications,
            last_auto_match_at=vacancy.last_auto_match_at.isoformat() if vacancy.last_auto_match_at else None,
            auto_match_count=vacancy.auto_match_count,
            candidate_ids=vacancy.candidate_ids,
            search_ids=vacancy.search_ids,
            created_at=vacancy.created_at.isoformat(),
            updated_at=vacancy.updated_at.isoformat(),
            closed_at=vacancy.closed_at.isoformat() if vacancy.closed_at else None
        ))
    
    return VacancyListResponse(
        vacancies=vacancy_list,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"]
    )


@router.get("/{vacancy_id}", response_model=VacancyResponse)
async def get_vacancy(
    vacancy_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get vacancy by ID"""
    vacancy = await vacancy_service.get_vacancy(vacancy_id, current_user)
    
    return VacancyResponse(
        id=str(vacancy.id),
        user_id=vacancy.user_id,
        title=vacancy.title,
        description=vacancy.description,
        requirements=vacancy.requirements,
        city=vacancy.city,
        remote=vacancy.remote,
        salary_min=vacancy.salary_min,
        salary_max=vacancy.salary_max,
        currency=vacancy.currency,
        status=vacancy.status,
        search_query=vacancy.search_query,
        search_city=vacancy.search_city,
        auto_matching_enabled=vacancy.auto_matching_enabled,
        auto_matching_frequency=vacancy.auto_matching_frequency,
        auto_matching_min_score=vacancy.auto_matching_min_score,
        auto_matching_max_notifications=vacancy.auto_matching_max_notifications,
        last_auto_match_at=vacancy.last_auto_match_at.isoformat() if vacancy.last_auto_match_at else None,
        auto_match_count=vacancy.auto_match_count,
        candidate_ids=vacancy.candidate_ids,
        search_ids=vacancy.search_ids,
        created_at=vacancy.created_at.isoformat(),
        updated_at=vacancy.updated_at.isoformat(),
        closed_at=vacancy.closed_at.isoformat() if vacancy.closed_at else None
    )


@router.patch("/{vacancy_id}", response_model=VacancyResponse)
async def update_vacancy(
    vacancy_id: str,
    vacancy_data: VacancyUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update vacancy"""
    vacancy = await vacancy_service.update_vacancy(
        vacancy_id=vacancy_id,
        user=current_user,
        title=vacancy_data.title,
        description=vacancy_data.description,
        requirements=vacancy_data.requirements,
        city=vacancy_data.city,
        remote=vacancy_data.remote,
        salary_min=vacancy_data.salary_min,
        salary_max=vacancy_data.salary_max,
        currency=vacancy_data.currency,
        search_query=vacancy_data.search_query,
        search_city=vacancy_data.search_city
    )
    
    return VacancyResponse(
        id=str(vacancy.id),
        user_id=vacancy.user_id,
        title=vacancy.title,
        description=vacancy.description,
        requirements=vacancy.requirements,
        city=vacancy.city,
        remote=vacancy.remote,
        salary_min=vacancy.salary_min,
        salary_max=vacancy.salary_max,
        currency=vacancy.currency,
        status=vacancy.status,
        search_query=vacancy.search_query,
        search_city=vacancy.search_city,
        auto_matching_enabled=vacancy.auto_matching_enabled,
        auto_matching_frequency=vacancy.auto_matching_frequency,
        auto_matching_min_score=vacancy.auto_matching_min_score,
        auto_matching_max_notifications=vacancy.auto_matching_max_notifications,
        last_auto_match_at=vacancy.last_auto_match_at.isoformat() if vacancy.last_auto_match_at else None,
        auto_match_count=vacancy.auto_match_count,
        candidate_ids=vacancy.candidate_ids,
        search_ids=vacancy.search_ids,
        created_at=vacancy.created_at.isoformat(),
        updated_at=vacancy.updated_at.isoformat(),
        closed_at=vacancy.closed_at.isoformat() if vacancy.closed_at else None
    )


@router.patch("/{vacancy_id}/status", response_model=VacancyResponse)
async def update_vacancy_status(
    vacancy_id: str,
    status: str = Query(..., pattern="^(active|paused|closed|filled)$"),
    current_user: User = Depends(get_current_user)
):
    """Update vacancy status"""
    vacancy = await vacancy_service.update_vacancy_status(
        vacancy_id=vacancy_id,
        status=status,
        user=current_user
    )
    
    return VacancyResponse(
        id=str(vacancy.id),
        user_id=vacancy.user_id,
        title=vacancy.title,
        description=vacancy.description,
        requirements=vacancy.requirements,
        city=vacancy.city,
        remote=vacancy.remote,
        salary_min=vacancy.salary_min,
        salary_max=vacancy.salary_max,
        currency=vacancy.currency,
        status=vacancy.status,
        search_query=vacancy.search_query,
        search_city=vacancy.search_city,
        auto_matching_enabled=vacancy.auto_matching_enabled,
        auto_matching_frequency=vacancy.auto_matching_frequency,
        auto_matching_min_score=vacancy.auto_matching_min_score,
        auto_matching_max_notifications=vacancy.auto_matching_max_notifications,
        last_auto_match_at=vacancy.last_auto_match_at.isoformat() if vacancy.last_auto_match_at else None,
        auto_match_count=vacancy.auto_match_count,
        candidate_ids=vacancy.candidate_ids,
        search_ids=vacancy.search_ids,
        created_at=vacancy.created_at.isoformat(),
        updated_at=vacancy.updated_at.isoformat(),
        closed_at=vacancy.closed_at.isoformat() if vacancy.closed_at else None
    )


@router.patch("/{vacancy_id}/auto-matching", response_model=VacancyResponse)
async def update_auto_matching_settings(
    vacancy_id: str,
    settings: AutoMatchingSettings,
    current_user: User = Depends(get_current_user)
):
    """Update auto-matching settings"""
    vacancy = await vacancy_service.update_auto_matching_settings(
        vacancy_id=vacancy_id,
        user=current_user,
        enabled=settings.enabled,
        frequency=settings.frequency,
        min_score=settings.min_score,
        max_notifications=settings.max_notifications
    )
    
    return VacancyResponse(
        id=str(vacancy.id),
        user_id=vacancy.user_id,
        title=vacancy.title,
        description=vacancy.description,
        requirements=vacancy.requirements,
        city=vacancy.city,
        remote=vacancy.remote,
        salary_min=vacancy.salary_min,
        salary_max=vacancy.salary_max,
        currency=vacancy.currency,
        status=vacancy.status,
        search_query=vacancy.search_query,
        search_city=vacancy.search_city,
        auto_matching_enabled=vacancy.auto_matching_enabled,
        auto_matching_frequency=vacancy.auto_matching_frequency,
        auto_matching_min_score=vacancy.auto_matching_min_score,
        auto_matching_max_notifications=vacancy.auto_matching_max_notifications,
        last_auto_match_at=vacancy.last_auto_match_at.isoformat() if vacancy.last_auto_match_at else None,
        auto_match_count=vacancy.auto_match_count,
        candidate_ids=vacancy.candidate_ids,
        search_ids=vacancy.search_ids,
        created_at=vacancy.created_at.isoformat(),
        updated_at=vacancy.updated_at.isoformat(),
        closed_at=vacancy.closed_at.isoformat() if vacancy.closed_at else None
    )


@router.post("/{vacancy_id}/candidates/{resume_id}", response_model=VacancyResponse)
async def add_candidate_to_vacancy(
    vacancy_id: str,
    resume_id: str,
    current_user: User = Depends(get_current_user)
):
    """Add candidate to vacancy"""
    vacancy = await vacancy_service.add_candidate_to_vacancy(
        vacancy_id=vacancy_id,
        resume_id=resume_id,
        user=current_user
    )
    
    return VacancyResponse(
        id=str(vacancy.id),
        user_id=vacancy.user_id,
        title=vacancy.title,
        description=vacancy.description,
        requirements=vacancy.requirements,
        city=vacancy.city,
        remote=vacancy.remote,
        salary_min=vacancy.salary_min,
        salary_max=vacancy.salary_max,
        currency=vacancy.currency,
        status=vacancy.status,
        search_query=vacancy.search_query,
        search_city=vacancy.search_city,
        auto_matching_enabled=vacancy.auto_matching_enabled,
        auto_matching_frequency=vacancy.auto_matching_frequency,
        auto_matching_min_score=vacancy.auto_matching_min_score,
        auto_matching_max_notifications=vacancy.auto_matching_max_notifications,
        last_auto_match_at=vacancy.last_auto_match_at.isoformat() if vacancy.last_auto_match_at else None,
        auto_match_count=vacancy.auto_match_count,
        candidate_ids=vacancy.candidate_ids,
        search_ids=vacancy.search_ids,
        created_at=vacancy.created_at.isoformat(),
        updated_at=vacancy.updated_at.isoformat(),
        closed_at=vacancy.closed_at.isoformat() if vacancy.closed_at else None
    )


@router.delete("/{vacancy_id}/candidates/{resume_id}", response_model=VacancyResponse)
async def remove_candidate_from_vacancy(
    vacancy_id: str,
    resume_id: str,
    current_user: User = Depends(get_current_user)
):
    """Remove candidate from vacancy"""
    vacancy = await vacancy_service.remove_candidate_from_vacancy(
        vacancy_id=vacancy_id,
        resume_id=resume_id,
        user=current_user
    )
    
    return VacancyResponse(
        id=str(vacancy.id),
        user_id=vacancy.user_id,
        title=vacancy.title,
        description=vacancy.description,
        requirements=vacancy.requirements,
        city=vacancy.city,
        remote=vacancy.remote,
        salary_min=vacancy.salary_min,
        salary_max=vacancy.salary_max,
        currency=vacancy.currency,
        status=vacancy.status,
        search_query=vacancy.search_query,
        search_city=vacancy.search_city,
        auto_matching_enabled=vacancy.auto_matching_enabled,
        auto_matching_frequency=vacancy.auto_matching_frequency,
        auto_matching_min_score=vacancy.auto_matching_min_score,
        auto_matching_max_notifications=vacancy.auto_matching_max_notifications,
        last_auto_match_at=vacancy.last_auto_match_at.isoformat() if vacancy.last_auto_match_at else None,
        auto_match_count=vacancy.auto_match_count,
        candidate_ids=vacancy.candidate_ids,
        search_ids=vacancy.search_ids,
        created_at=vacancy.created_at.isoformat(),
        updated_at=vacancy.updated_at.isoformat(),
        closed_at=vacancy.closed_at.isoformat() if vacancy.closed_at else None
    )


@router.get("/{vacancy_id}/candidates")
async def get_vacancy_candidates(
    vacancy_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("ai_score"),
    sort_order: str = Query("desc"),
    current_user: User = Depends(get_current_user)
):
    """Get candidates (resumes) linked to a vacancy"""
    from bson import ObjectId
    from app.domain.entities.vacancy import Vacancy as VacancyModel
    vacancy = await VacancyModel.get(vacancy_id)
    if not vacancy:
        raise NotFoundException("Vacancy not found")

    candidate_ids = vacancy.candidate_ids or []
    total = len(candidate_ids)

    if not candidate_ids:
        return {"resumes": [], "total": 0, "page": page, "page_size": page_size}

    valid_ids = []
    for rid in candidate_ids:
        try:
            valid_ids.append(ObjectId(rid))
        except Exception:
            pass

    resumes = await Resume.find({"_id": {"$in": valid_ids}}).to_list()

    reverse = sort_order == "desc"
    if sort_by == "ai_score":
        resumes.sort(key=lambda r: (r.ai_score or 0), reverse=reverse)
    elif sort_by == "match_percentage":
        resumes.sort(key=lambda r: (r.match_percentage or 0), reverse=reverse)
    elif sort_by == "created_at":
        resumes.sort(key=lambda r: r.created_at, reverse=reverse)

    start = (page - 1) * page_size
    page_resumes = resumes[start:start + page_size]

    result = []
    for r in page_resumes:
        hh_url = f"https://hh.ru/resume/{r.hh_id}" if r.hh_id else None
        result.append({
            "id": str(r.id),
            "hh_id": r.hh_id,
            "hh_url": hh_url,
            "name": r.name,
            "age": r.age,
            "city": r.city,
            "title": r.title,
            "salary": r.salary,
            "currency": r.currency,
            "ai_score": r.ai_score,
            "match_percentage": r.match_percentage,
            "ai_summary": r.ai_summary,
            "match_explanation": r.match_explanation,
            "strengths": r.strengths or [],
            "weaknesses": r.weaknesses or [],
            "recommendation": r.recommendation,
            "red_flags": r.red_flags or [],
            "ai_questions": r.ai_questions or [],
            "evaluation_details": r.evaluation_details,
            "interview_focus": getattr(r, "interview_focus", None),
            "career_trajectory": getattr(r, "career_trajectory", None),
            "analyzed": r.analyzed,
        })

    return {"resumes": result, "total": total, "page": page, "page_size": page_size}
