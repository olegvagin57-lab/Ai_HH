"""Search API routes"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from app.api.v1.schemas.search import (
    SearchCreate,
    SearchResponse,
    ResumeListResponse,
    ResumeResponse,
    SearchListResponse
)
from app.application.services.search_service import search_service
from app.api.middleware.auth import get_current_user, require_permission
from app.domain.entities.user import User
from app.domain.entities.search import Search, Resume
from app.core.logging import get_logger
from app.core.exceptions import NotFoundException
from celery_app.tasks.search_tasks import process_search_task


logger = get_logger(__name__)
router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=SearchResponse, status_code=status.HTTP_201_CREATED)
async def create_search(
    search_data: SearchCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new search"""
    logger.info("create_search called", 
                user_id=str(current_user.id) if isinstance(current_user, User) else "unknown",
                query=search_data.query[:50] if search_data.query else None,
                city=search_data.city)
    
    try:
        # Verify we have a valid User object
        if not isinstance(current_user, User):
            logger.error("create_search received invalid user object", 
                        received_type=type(current_user).__name__)
            raise ValueError(f"Invalid user object: {type(current_user)}")
        
        # Validate input data
        query = search_data.query.strip() if search_data.query else ""
        city = search_data.city.strip() if search_data.city else ""
        
        if not query:
            from app.core.exceptions import ValidationException
            raise ValidationException("Query cannot be empty")
        
        if not city:
            from app.core.exceptions import ValidationException
            raise ValidationException("City cannot be empty")
        
        logger.debug("Creating search", user_id=str(current_user.id))
        search = await search_service.create_search(
            user=current_user,
            query=query,
            city=city
        )
        
        logger.info("Search created successfully", 
                   search_id=str(search.id),
                   status=search.status)
        
        # Build response first
        response = SearchResponse(
            id=str(search.id),
            user_id=str(search.user_id),
            query=search.query,
            city=search.city,
            status=search.status,
            total_found=search.total_found,
            analyzed_count=search.analyzed_count,
            processed_count=getattr(search, 'processed_count', 0),
            total_to_process=getattr(search, 'total_to_process', 0),
            created_at=search.created_at.isoformat(),
            completed_at=search.completed_at.isoformat() if search.completed_at else None,
            error_message=search.error_message
        )
        
        logger.info("Response built, returning to client immediately", search_id=str(search.id))
        
        # Trigger Celery task immediately - use delay() for simplicity
        # This ensures task is queued and worker will process it automatically
        try:
            logger.debug("Triggering Celery task", search_id=str(search.id))
            # Use delay() - simplest way to queue task
            task_result = process_search_task.delay(str(search.id))
            logger.info("Celery task queued successfully", 
                       search_id=str(search.id),
                       task_id=task_result.id,
                       task_state=task_result.state)
        except Exception as e:
            # Log but don't fail - search is already created
            # Task will be processed when worker is available
            logger.warning("Celery task failed to queue (will retry)", 
                         error=str(e),
                         error_type=type(e).__name__,
                         search_id=str(search.id))
            # Don't raise - search is created, processing will happen automatically
        
        return response
    except Exception as e:
        logger.error("Error creating search", 
                    error=str(e), 
                    error_type=type(e).__name__,
                    exc_info=True)
        raise


@router.get("", response_model=SearchListResponse)
async def list_searches(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """List searches"""
    skip = (page - 1) * page_size
    
    # Build query based on permissions
    if current_user.can_view_all_searches():
        query = Search.find_all()
    else:
        query = Search.find({"user_id": str(current_user.id)})
    
    searches = await query.sort(-Search.created_at).skip(skip).limit(page_size).to_list()
    total = await query.count()
    
    search_list = []
    for search in searches:
        search_list.append(SearchResponse(
            id=str(search.id),
            user_id=str(search.user_id),
            query=search.query,
            city=search.city,
            status=search.status,
            total_found=search.total_found,
            analyzed_count=search.analyzed_count,
            processed_count=getattr(search, 'processed_count', 0),
            total_to_process=getattr(search, 'total_to_process', 0),
            created_at=search.created_at.isoformat(),
            completed_at=search.completed_at.isoformat() if search.completed_at else None,
            error_message=search.error_message
        ))
    
    return SearchListResponse(
        searches=search_list,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{search_id}", response_model=SearchResponse)
async def get_search(
    search_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get search by ID"""
    try:
        logger.debug("Getting search", search_id=search_id, user_id=str(current_user.id))
        search = await search_service.get_search(search_id, current_user)
        
        return SearchResponse(
            id=str(search.id),
            user_id=str(search.user_id),
            query=search.query,
            city=search.city,
            status=search.status,
            total_found=search.total_found,
            analyzed_count=search.analyzed_count,
            processed_count=getattr(search, 'processed_count', 0),
            total_to_process=getattr(search, 'total_to_process', 0),
            created_at=search.created_at.isoformat(),
            completed_at=search.completed_at.isoformat() if search.completed_at else None,
            error_message=search.error_message
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error("Error getting search", 
                    search_id=search_id,
                    error=str(e),
                    error_type=type(e).__name__,
                    exc_info=True)
        raise


@router.get("/{search_id}/status", response_model=SearchResponse)
async def get_search_status(
    search_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get search status"""
    try:
        logger.debug("Getting search status", search_id=search_id, user_id=str(current_user.id))
        search = await search_service.get_search(search_id, current_user)
        
        return SearchResponse(
            id=str(search.id),
            user_id=str(search.user_id),
            query=search.query,
            city=search.city,
            status=search.status,
            total_found=search.total_found,
            analyzed_count=search.analyzed_count,
            processed_count=getattr(search, 'processed_count', 0),
            total_to_process=getattr(search, 'total_to_process', 0),
            created_at=search.created_at.isoformat(),
            completed_at=search.completed_at.isoformat() if search.completed_at else None,
            error_message=search.error_message
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error("Error getting search status", 
                    search_id=search_id,
                    error=str(e),
                    error_type=type(e).__name__,
                    exc_info=True)
        raise


@router.get("/{search_id}/resumes", response_model=ResumeListResponse)
async def get_search_resumes(
    search_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("ai_score", pattern="^(ai_score|preliminary_score|match_percentage|created_at)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    # Filter parameters
    min_salary: Optional[int] = Query(None, ge=0),
    max_salary: Optional[int] = Query(None, ge=0),
    min_age: Optional[int] = Query(None, ge=18, le=100),
    max_age: Optional[int] = Query(None, ge=18, le=100),
    min_experience_years: Optional[int] = Query(None, ge=0),
    skills: Optional[str] = Query(None, description="Comma-separated list of skills"),
    education: Optional[str] = Query(None),
    relocation_ready: Optional[bool] = Query(None),
    min_ai_score: Optional[int] = Query(None, ge=1, le=10),
    max_ai_score: Optional[int] = Query(None, ge=1, le=10),
    min_match_percentage: Optional[float] = Query(None, ge=0.0, le=100.0),
    max_match_percentage: Optional[float] = Query(None, ge=0.0, le=100.0),
    candidate_status: Optional[str] = Query(None, pattern="^(new|reviewed|shortlisted|interview_scheduled|interviewed|offer_sent|hired|rejected|on_hold)$"),
    has_red_flags: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get resumes for a search with filtering"""
    try:
        logger.debug("Getting search resumes", 
                    search_id=search_id,
                    user_id=str(current_user.id),
                    page=page,
                    page_size=page_size)
        
        # Parse skills list
        skills_list = None
        if skills:
            skills_list = [s.strip() for s in skills.split(",") if s.strip()]
        
        result = await search_service.get_search_resumes(
            search_id=search_id,
            user=current_user,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
            min_salary=min_salary,
            max_salary=max_salary,
            min_age=min_age,
            max_age=max_age,
            min_experience_years=min_experience_years,
            skills=skills_list,
            education=education,
            relocation_ready=relocation_ready,
            min_ai_score=min_ai_score,
            max_ai_score=max_ai_score,
            min_match_percentage=min_match_percentage,
            max_match_percentage=max_match_percentage,
            candidate_status=candidate_status,
            has_red_flags=has_red_flags
        )
        
        logger.debug("Resumes retrieved", 
                    search_id=search_id,
                    count=len(result.get("resumes", [])))
        
        resume_list = []
        for resume in result["resumes"]:
            # Generate HH URL if hh_id is available
            hh_url = None
            if resume.hh_id:
                hh_url = f"https://hh.ru/resume/{resume.hh_id}"
            
            resume_list.append(ResumeResponse(
                id=str(resume.id),
                search_id=str(resume.search_id),
                hh_id=resume.hh_id,
                hh_url=hh_url,
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
                interview_focus=getattr(resume, 'interview_focus', None),
                career_trajectory=getattr(resume, 'career_trajectory', None),
                created_at=resume.created_at.isoformat()
            ))
        
        logger.info("Resumes returned", 
                   search_id=search_id,
                   count=len(resume_list),
                   total=result["total"])
        
        return ResumeListResponse(
            resumes=resume_list,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"]
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error("Error getting search resumes", 
                    search_id=search_id,
                    error=str(e),
                    error_type=type(e).__name__,
                    exc_info=True)
        raise
