"""Candidate management API routes"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from app.api.v1.schemas.candidate import (
    CandidateResponse,
    InteractionResponse,
    UpdateStatusRequest,
    AddTagRequest,
    AssignRequest,
    AddRatingRequest,
    UpdateNotesRequest,
    SetFolderRequest,
    CandidateListResponse,
    InteractionListResponse
)
from app.application.services.candidate_service import candidate_service
from app.api.middleware.auth import get_current_user
from app.domain.entities.user import User
from app.domain.entities.search import Resume
from app.core.logging import get_logger
from app.core.exceptions import NotFoundException


logger = get_logger(__name__)
router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("/resume/{resume_id}", response_model=CandidateResponse)
async def get_candidate(
    resume_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get candidate by resume ID"""
    candidate = await candidate_service.get_candidate_by_resume_id(resume_id)
    if not candidate:
        # Create candidate if it doesn't exist
        candidate = await candidate_service.get_or_create_candidate(resume_id)
    
    return CandidateResponse(
        resume_id=candidate.resume_id,
        status=candidate.status,
        tags=candidate.tags,
        folder=candidate.folder,
        assigned_to_user_id=candidate.assigned_to_user_id,
        ratings=candidate.ratings,
        average_rating=candidate.average_rating,
        notes=candidate.notes,
        vacancy_ids=candidate.vacancy_ids,
        created_at=candidate.created_at.isoformat(),
        updated_at=candidate.updated_at.isoformat(),
        status_changed_at=candidate.status_changed_at.isoformat() if candidate.status_changed_at else None
    )


@router.patch("/resume/{resume_id}/status", response_model=CandidateResponse)
async def update_candidate_status(
    resume_id: str,
    status_data: UpdateStatusRequest,
    current_user: User = Depends(get_current_user)
):
    """Update candidate status"""
    # Verify resume exists
    resume = await Resume.get(resume_id)
    if not resume:
        raise NotFoundException("Resume not found")
    
    candidate = await candidate_service.update_candidate_status(
        resume_id=resume_id,
        new_status=status_data.status,
        user=current_user
    )
    
    return CandidateResponse(
        resume_id=candidate.resume_id,
        status=candidate.status,
        tags=candidate.tags,
        folder=candidate.folder,
        assigned_to_user_id=candidate.assigned_to_user_id,
        ratings=candidate.ratings,
        average_rating=candidate.average_rating,
        notes=candidate.notes,
        vacancy_ids=candidate.vacancy_ids,
        created_at=candidate.created_at.isoformat(),
        updated_at=candidate.updated_at.isoformat(),
        status_changed_at=candidate.status_changed_at.isoformat() if candidate.status_changed_at else None
    )


@router.post("/resume/{resume_id}/tags", response_model=CandidateResponse)
async def add_tag(
    resume_id: str,
    tag_data: AddTagRequest,
    current_user: User = Depends(get_current_user)
):
    """Add a tag to a candidate"""
    candidate = await candidate_service.add_tag(
        resume_id=resume_id,
        tag=tag_data.tag,
        user=current_user
    )
    
    return CandidateResponse(
        resume_id=candidate.resume_id,
        status=candidate.status,
        tags=candidate.tags,
        folder=candidate.folder,
        assigned_to_user_id=candidate.assigned_to_user_id,
        ratings=candidate.ratings,
        average_rating=candidate.average_rating,
        notes=candidate.notes,
        vacancy_ids=candidate.vacancy_ids,
        created_at=candidate.created_at.isoformat(),
        updated_at=candidate.updated_at.isoformat(),
        status_changed_at=candidate.status_changed_at.isoformat() if candidate.status_changed_at else None
    )


@router.delete("/resume/{resume_id}/tags/{tag}", response_model=CandidateResponse)
async def remove_tag(
    resume_id: str,
    tag: str,
    current_user: User = Depends(get_current_user)
):
    """Remove a tag from a candidate"""
    candidate = await candidate_service.remove_tag(
        resume_id=resume_id,
        tag=tag,
        user=current_user
    )
    
    return CandidateResponse(
        resume_id=candidate.resume_id,
        status=candidate.status,
        tags=candidate.tags,
        folder=candidate.folder,
        assigned_to_user_id=candidate.assigned_to_user_id,
        ratings=candidate.ratings,
        average_rating=candidate.average_rating,
        notes=candidate.notes,
        vacancy_ids=candidate.vacancy_ids,
        created_at=candidate.created_at.isoformat(),
        updated_at=candidate.updated_at.isoformat(),
        status_changed_at=candidate.status_changed_at.isoformat() if candidate.status_changed_at else None
    )


@router.post("/resume/{resume_id}/assign", response_model=CandidateResponse)
async def assign_candidate(
    resume_id: str,
    assign_data: AssignRequest,
    current_user: User = Depends(get_current_user)
):
    """Assign candidate to an HR specialist"""
    candidate = await candidate_service.assign_to_user(
        resume_id=resume_id,
        assigned_user_id=assign_data.assigned_to_user_id,
        user=current_user
    )
    
    return CandidateResponse(
        resume_id=candidate.resume_id,
        status=candidate.status,
        tags=candidate.tags,
        folder=candidate.folder,
        assigned_to_user_id=candidate.assigned_to_user_id,
        ratings=candidate.ratings,
        average_rating=candidate.average_rating,
        notes=candidate.notes,
        vacancy_ids=candidate.vacancy_ids,
        created_at=candidate.created_at.isoformat(),
        updated_at=candidate.updated_at.isoformat(),
        status_changed_at=candidate.status_changed_at.isoformat() if candidate.status_changed_at else None
    )


@router.post("/resume/{resume_id}/rating", response_model=CandidateResponse)
async def add_rating(
    resume_id: str,
    rating_data: AddRatingRequest,
    current_user: User = Depends(get_current_user)
):
    """Add or update a rating for a candidate"""
    candidate = await candidate_service.add_rating(
        resume_id=resume_id,
        rating=rating_data.rating,
        user=current_user
    )
    
    return CandidateResponse(
        resume_id=candidate.resume_id,
        status=candidate.status,
        tags=candidate.tags,
        folder=candidate.folder,
        assigned_to_user_id=candidate.assigned_to_user_id,
        ratings=candidate.ratings,
        average_rating=candidate.average_rating,
        notes=candidate.notes,
        vacancy_ids=candidate.vacancy_ids,
        created_at=candidate.created_at.isoformat(),
        updated_at=candidate.updated_at.isoformat(),
        status_changed_at=candidate.status_changed_at.isoformat() if candidate.status_changed_at else None
    )


@router.patch("/resume/{resume_id}/notes", response_model=CandidateResponse)
async def update_notes(
    resume_id: str,
    notes_data: UpdateNotesRequest,
    current_user: User = Depends(get_current_user)
):
    """Update candidate notes"""
    candidate = await candidate_service.update_notes(
        resume_id=resume_id,
        notes=notes_data.notes,
        user=current_user
    )
    
    return CandidateResponse(
        resume_id=candidate.resume_id,
        status=candidate.status,
        tags=candidate.tags,
        folder=candidate.folder,
        assigned_to_user_id=candidate.assigned_to_user_id,
        ratings=candidate.ratings,
        average_rating=candidate.average_rating,
        notes=candidate.notes,
        vacancy_ids=candidate.vacancy_ids,
        created_at=candidate.created_at.isoformat(),
        updated_at=candidate.updated_at.isoformat(),
        status_changed_at=candidate.status_changed_at.isoformat() if candidate.status_changed_at else None
    )


@router.patch("/resume/{resume_id}/folder", response_model=CandidateResponse)
async def set_folder(
    resume_id: str,
    folder_data: SetFolderRequest,
    current_user: User = Depends(get_current_user)
):
    """Set candidate folder"""
    candidate = await candidate_service.set_folder(
        resume_id=resume_id,
        folder=folder_data.folder,
        user=current_user
    )
    
    return CandidateResponse(
        resume_id=candidate.resume_id,
        status=candidate.status,
        tags=candidate.tags,
        folder=candidate.folder,
        assigned_to_user_id=candidate.assigned_to_user_id,
        ratings=candidate.ratings,
        average_rating=candidate.average_rating,
        notes=candidate.notes,
        vacancy_ids=candidate.vacancy_ids,
        created_at=candidate.created_at.isoformat(),
        updated_at=candidate.updated_at.isoformat(),
        status_changed_at=candidate.status_changed_at.isoformat() if candidate.status_changed_at else None
    )


@router.get("/resume/{resume_id}/interactions", response_model=InteractionListResponse)
async def get_interactions(
    resume_id: str,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user)
):
    """Get interaction history for a candidate"""
    interactions = await candidate_service.get_interactions(resume_id, limit)
    
    interaction_list = []
    for interaction in interactions:
        interaction_list.append(InteractionResponse(
            id=str(interaction.id),
            resume_id=interaction.resume_id,
            user_id=interaction.user_id,
            action_type=interaction.action_type,
            action_data=interaction.action_data,
            created_at=interaction.created_at.isoformat()
        ))
    
    return InteractionListResponse(
        interactions=interaction_list,
        total=len(interaction_list)
    )


@router.get("/status/{status}", response_model=CandidateListResponse)
async def get_candidates_by_status(
    status: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """Get candidates by status"""
    result = await candidate_service.get_candidates_by_status(
        status=status,
        user=current_user,
        page=page,
        page_size=page_size
    )
    
    candidate_list = []
    for candidate in result["candidates"]:
        candidate_list.append(CandidateResponse(
            resume_id=candidate.resume_id,
            status=candidate.status,
            tags=candidate.tags,
            folder=candidate.folder,
            assigned_to_user_id=candidate.assigned_to_user_id,
            ratings=candidate.ratings,
            average_rating=candidate.average_rating,
            notes=candidate.notes,
            vacancy_ids=candidate.vacancy_ids,
            created_at=candidate.created_at.isoformat(),
            updated_at=candidate.updated_at.isoformat(),
            status_changed_at=candidate.status_changed_at.isoformat() if candidate.status_changed_at else None
        ))
    
    return CandidateListResponse(
        candidates=candidate_list,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"]
    )


@router.get("/tags", response_model=CandidateListResponse)
async def get_candidates_by_tags(
    tags: str = Query(..., description="Comma-separated list of tags"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """Get candidates by tags"""
    tags_list = [t.strip() for t in tags.split(",") if t.strip()]
    
    result = await candidate_service.get_candidates_by_tags(
        tags=tags_list,
        page=page,
        page_size=page_size
    )
    
    candidate_list = []
    for candidate in result["candidates"]:
        candidate_list.append(CandidateResponse(
            resume_id=candidate.resume_id,
            status=candidate.status,
            tags=candidate.tags,
            folder=candidate.folder,
            assigned_to_user_id=candidate.assigned_to_user_id,
            ratings=candidate.ratings,
            average_rating=candidate.average_rating,
            notes=candidate.notes,
            vacancy_ids=candidate.vacancy_ids,
            created_at=candidate.created_at.isoformat(),
            updated_at=candidate.updated_at.isoformat(),
            status_changed_at=candidate.status_changed_at.isoformat() if candidate.status_changed_at else None
        ))
    
    return CandidateListResponse(
        candidates=candidate_list,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"]
    )


@router.get("/kanban")
async def get_kanban_data(
    vacancy_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get candidates organized by status for Kanban board"""
    from app.domain.entities.search import Resume
    
    # Get all statuses
    statuses = ["new", "reviewed", "shortlisted", "interview_scheduled", "interviewed", "offer_sent", "hired", "rejected", "on_hold"]
    
    kanban_data = {}
    
    for status in statuses:
        query_dict = {"status": status}
        
        # Filter by user if not admin
        if not current_user.can_view_all_searches():
            query_dict["assigned_to_user_id"] = str(current_user.id)
        
        # Filter by vacancy if provided
        if vacancy_id:
            query_dict["vacancy_ids"] = vacancy_id
        
        candidates = await Candidate.find(query_dict).sort(-Candidate.updated_at).limit(100).to_list()
        
        # Enrich with resume data
        candidates_with_resume = []
        for candidate in candidates:
            resume = await Resume.get(candidate.resume_id)
            if resume:
                candidates_with_resume.append({
                    "resume_id": candidate.resume_id,
                    "name": resume.name,
                    "title": resume.title,
                    "ai_score": resume.ai_score,
                    "match_percentage": resume.match_percentage,
                    "status": candidate.status,
                    "tags": candidate.tags,
                    "assigned_to_user_id": candidate.assigned_to_user_id,
                    "average_rating": candidate.average_rating,
                    "match_explanation": resume.match_explanation,
                    "recommendation": resume.recommendation
                })
        
        kanban_data[status] = candidates_with_resume
    
    return kanban_data
