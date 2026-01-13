"""Search API routes"""
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
        
        logger.debug("Creating search", user_id=str(current_user.id))
        search = await search_service.create_search(
            user=current_user,
            query=search_data.query,
            city=search_data.city
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
            created_at=search.created_at.isoformat(),
            completed_at=search.completed_at.isoformat() if search.completed_at else None,
            error_message=search.error_message
        )
        
        logger.info("Response built, returning to client immediately", search_id=str(search.id))
        
        # Trigger Celery task in separate thread to avoid ANY blocking
        # This ensures response is returned immediately even if Redis is unavailable
        import threading
        
        def trigger_celery_in_thread():
            """Trigger Celery task in separate thread - completely non-blocking"""
            try:
                logger.debug("Triggering Celery task in background thread", search_id=str(search.id))
                # Use delay() - if Redis is unavailable, it will fail quickly in this thread
                task_result = process_search_task.delay(str(search.id))
                logger.info("Celery task queued successfully", 
                           search_id=str(search.id),
                           task_id=getattr(task_result, 'id', None))
            except Exception as e:
                # Log but don't fail - search is already created
                logger.warning("Celery task failed (Redis unavailable, non-critical)", 
                             error=str(e),
                             error_type=type(e).__name__,
                             search_id=str(search.id))
        
        # Start thread as daemon - won't block main process
        thread = threading.Thread(target=trigger_celery_in_thread, daemon=True)
        thread.start()
        logger.debug("Background thread started for Celery task", search_id=str(search.id))
        
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
    search = await search_service.get_search(search_id, current_user)
    
    return SearchResponse(
        id=str(search.id),
        user_id=str(search.user_id),
        query=search.query,
        city=search.city,
        status=search.status,
        total_found=search.total_found,
        analyzed_count=search.analyzed_count,
        created_at=search.created_at.isoformat(),
        completed_at=search.completed_at.isoformat() if search.completed_at else None,
        error_message=search.error_message
    )


@router.get("/{search_id}/status", response_model=SearchResponse)
async def get_search_status(
    search_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get search status"""
    search = await search_service.get_search(search_id, current_user)
    
    return SearchResponse(
        id=str(search.id),
        user_id=str(search.user_id),
        query=search.query,
        city=search.city,
        status=search.status,
        total_found=search.total_found,
        analyzed_count=search.analyzed_count,
        created_at=search.created_at.isoformat(),
        completed_at=search.completed_at.isoformat() if search.completed_at else None,
        error_message=search.error_message
    )


@router.get("/{search_id}/resumes", response_model=ResumeListResponse)
async def get_search_resumes(
    search_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("ai_score", regex="^(ai_score|preliminary_score|created_at)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: User = Depends(get_current_user)
):
    """Get resumes for a search"""
    result = await search_service.get_search_resumes(
        search_id=search_id,
        user=current_user,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    resume_list = []
    for resume in result["resumes"]:
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
            created_at=resume.created_at.isoformat()
        ))
    
    return ResumeListResponse(
        resumes=resume_list,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"]
    )
