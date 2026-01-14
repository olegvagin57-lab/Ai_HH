"""Vacancy management API routes"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
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
