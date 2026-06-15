"""Candidate management API routes"""
from typing import Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, Query
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
from app.domain.entities.candidate import Candidate
from app.core.logging import get_logger
from app.core.exceptions import NotFoundException


logger = get_logger(__name__)
router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("/resume/{resume_id}", response_model=CandidateResponse)
async def get_candidate(
    resume_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get candidate by resume ID, enriched with resume data"""
    candidate = await candidate_service.get_candidate_by_resume_id(resume_id)
    if not candidate:
        candidate = await candidate_service.get_or_create_candidate(resume_id)
    resume = await Resume.get(resume_id)
    return _build_candidate_response(candidate, {resume_id: resume} if resume else {})


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
    resume = await Resume.get(resume_id)
    return _build_candidate_response(candidate, {resume_id: resume} if resume else {})


@router.post("/resume/{resume_id}/tags", response_model=CandidateResponse)
async def add_tag(
    resume_id: str,
    tag_data: AddTagRequest,
    current_user: User = Depends(get_current_user)
):
    """Add a tag to a candidate"""
    candidate = await candidate_service.add_tag(resume_id=resume_id, tag=tag_data.tag, user=current_user)
    resume = await Resume.get(resume_id)
    return _build_candidate_response(candidate, {resume_id: resume} if resume else {})


@router.delete("/resume/{resume_id}/tags/{tag}", response_model=CandidateResponse)
async def remove_tag(
    resume_id: str,
    tag: str,
    current_user: User = Depends(get_current_user)
):
    """Remove a tag from a candidate"""
    candidate = await candidate_service.remove_tag(resume_id=resume_id, tag=tag, user=current_user)
    resume = await Resume.get(resume_id)
    return _build_candidate_response(candidate, {resume_id: resume} if resume else {})


@router.post("/resume/{resume_id}/assign", response_model=CandidateResponse)
async def assign_candidate(
    resume_id: str,
    assign_data: AssignRequest,
    current_user: User = Depends(get_current_user)
):
    """Assign candidate to an HR specialist"""
    candidate = await candidate_service.assign_to_user(
        resume_id=resume_id, assigned_user_id=assign_data.assigned_to_user_id, user=current_user
    )
    resume = await Resume.get(resume_id)
    return _build_candidate_response(candidate, {resume_id: resume} if resume else {})


@router.post("/resume/{resume_id}/rating", response_model=CandidateResponse)
async def add_rating(
    resume_id: str,
    rating_data: AddRatingRequest,
    current_user: User = Depends(get_current_user)
):
    """Add or update a rating for a candidate"""
    candidate = await candidate_service.add_rating(resume_id=resume_id, rating=rating_data.rating, user=current_user)
    resume = await Resume.get(resume_id)
    return _build_candidate_response(candidate, {resume_id: resume} if resume else {})


@router.patch("/resume/{resume_id}/notes", response_model=CandidateResponse)
async def update_notes(
    resume_id: str,
    notes_data: UpdateNotesRequest,
    current_user: User = Depends(get_current_user)
):
    """Update candidate notes"""
    candidate = await candidate_service.update_notes(resume_id=resume_id, notes=notes_data.notes, user=current_user)
    resume = await Resume.get(resume_id)
    return _build_candidate_response(candidate, {resume_id: resume} if resume else {})


@router.patch("/resume/{resume_id}/folder", response_model=CandidateResponse)
async def set_folder(
    resume_id: str,
    folder_data: SetFolderRequest,
    current_user: User = Depends(get_current_user)
):
    """Set candidate folder"""
    candidate = await candidate_service.set_folder(resume_id=resume_id, folder=folder_data.folder, user=current_user)
    resume = await Resume.get(resume_id)
    return _build_candidate_response(candidate, {resume_id: resume} if resume else {})


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


def _build_candidate_response(candidate, resume_map: dict) -> CandidateResponse:
    """Build CandidateResponse enriched with resume fields."""
    r = resume_map.get(candidate.resume_id)
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
        status_changed_at=candidate.status_changed_at.isoformat() if candidate.status_changed_at else None,
        name=r.name if r else None,
        title=r.title if r else None,
        city=r.city if r else None,
        age=r.age if r else None,
        salary=r.salary if r else None,
        currency=r.currency if r else None,
        ai_score=r.ai_score if r else None,
        match_percentage=r.match_percentage if r else None,
        hh_id=r.hh_id if r else None,
        preliminary_score=r.preliminary_score if r else None,
        match_explanation=r.match_explanation if r else None,
        recommendation=r.recommendation if r else None,
        strengths=r.strengths if r else None,
        weaknesses=r.weaknesses if r else None,
        red_flags=r.red_flags if r else None,
        interview_focus=r.interview_focus if r else None,
        career_trajectory=r.career_trajectory if r else None,
        search_id=r.search_id if r else None,
    )


@router.get("", response_model=CandidateListResponse)
async def get_all_candidates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=500),
    current_user: User = Depends(get_current_user)
):
    """Get all candidates with pagination, enriched with resume data"""
    result = await candidate_service.get_all_candidates(
        user=current_user,
        page=page,
        page_size=page_size
    )

    resume_ids = [c.resume_id for c in result["candidates"]]
    resumes = await Resume.find({"_id": {"$in": [ObjectId(rid) for rid in resume_ids if rid]}}).to_list()
    resume_map = {str(r.id): r for r in resumes}

    return CandidateListResponse(
        candidates=[_build_candidate_response(c, resume_map) for c in result["candidates"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"]
    )


@router.get("/status/{status}", response_model=CandidateListResponse)
async def get_candidates_by_status(
    status: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=500),
    current_user: User = Depends(get_current_user)
):
    """Get candidates by status, enriched with resume data"""
    result = await candidate_service.get_candidates_by_status(
        status=status,
        user=current_user,
        page=page,
        page_size=page_size
    )

    resume_ids = [c.resume_id for c in result["candidates"]]
    resumes = await Resume.find({"_id": {"$in": [ObjectId(rid) for rid in resume_ids if rid]}}).to_list()
    resume_map = {str(r.id): r for r in resumes}

    candidate_list = [_build_candidate_response(c, resume_map) for c in result["candidates"]]
    
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
    page_size: int = Query(20, ge=1, le=500),
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
    from app.domain.entities.search import Resume, Search

    statuses = ["new", "reviewed", "shortlisted", "interview_scheduled", "interviewed", "offer_sent", "hired", "rejected", "on_hold"]

    # Build base query
    base_query = {}
    if vacancy_id:
        base_query["vacancy_ids"] = vacancy_id

    # Fetch ALL candidates in one query, then split by status
    all_candidates = await Candidate.find(base_query).sort(-Candidate.updated_at).limit(500).to_list()

    # Filter by user ownership if not hr_manager/admin
    if not current_user.can_view_all_searches():
        user_searches = await Search.find({"user_id": str(current_user.id)}).to_list()
        user_search_ids = {str(s.id) for s in user_searches}

        # Bulk-load all resumes for search_id lookup
        all_resume_ids = [c.resume_id for c in all_candidates if c.resume_id]
        owner_resumes = await Resume.find(
            {"_id": {"$in": [ObjectId(rid) for rid in all_resume_ids if rid]}}
        ).to_list()
        search_id_map = {str(r.id): r.search_id for r in owner_resumes}

        filtered = []
        for candidate in all_candidates:
            if candidate.assigned_to_user_id == str(current_user.id):
                filtered.append(candidate)
            elif not candidate.assigned_to_user_id:
                sid = search_id_map.get(candidate.resume_id)
                if sid and sid in user_search_ids:
                    filtered.append(candidate)
        all_candidates = filtered

    # Bulk-load resumes for enrichment
    resume_ids = [c.resume_id for c in all_candidates if c.resume_id]
    resumes = await Resume.find(
        {"_id": {"$in": [ObjectId(rid) for rid in resume_ids if rid]}}
    ).to_list()
    resume_map = {str(r.id): r for r in resumes}

    # Group by status
    kanban_data = {s: [] for s in statuses}
    for candidate in all_candidates:
        if candidate.status not in kanban_data:
            continue
        r = resume_map.get(candidate.resume_id)
        if r:
            kanban_data[candidate.status].append({
                "resume_id": candidate.resume_id,
                "name": r.name,
                "title": r.title,
                "ai_score": r.ai_score,
                "match_percentage": r.match_percentage,
                "status": candidate.status,
                "tags": candidate.tags,
                "assigned_to_user_id": candidate.assigned_to_user_id,
                "average_rating": candidate.average_rating,
                "match_explanation": r.match_explanation,
                "recommendation": r.recommendation,
            })

    return kanban_data
