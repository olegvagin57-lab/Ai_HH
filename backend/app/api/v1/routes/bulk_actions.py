"""Bulk actions API routes"""
from typing import List
from fastapi import APIRouter, Depends, Request
from app.api.middleware.auth import get_current_user
from app.domain.entities.user import User
from app.application.services.candidate_service import candidate_service
from app.core.logging import get_logger
from pydantic import BaseModel, Field
import json


logger = get_logger(__name__)
router = APIRouter(prefix="/bulk", tags=["bulk-actions"])


class BulkStatusUpdate(BaseModel):
    """Bulk status update request"""
    resume_ids: List[str] = Field(..., min_length=1, max_length=100)
    status: str = Field(..., pattern="^(new|reviewed|shortlisted|interview_scheduled|interviewed|offer_sent|hired|rejected|on_hold)$")


class BulkTagAdd(BaseModel):
    """Bulk tag add request"""
    resume_ids: List[str] = Field(..., min_length=1, max_length=100)
    tag: str = Field(..., min_length=1, max_length=50)


class BulkTagRemove(BaseModel):
    """Bulk tag remove request"""
    resume_ids: List[str] = Field(..., min_length=1, max_length=100)
    tag: str = Field(..., min_length=1, max_length=50)


class BulkAssign(BaseModel):
    """Bulk assign request"""
    resume_ids: List[str] = Field(..., min_length=1, max_length=100)
    assigned_to_user_id: str


class BulkFolderSet(BaseModel):
    """Bulk folder set request"""
    resume_ids: List[str] = Field(..., min_length=1, max_length=100)
    folder: str = Field(..., min_length=1, max_length=100)


class BulkResponse(BaseModel):
    """Bulk action response"""
    success_count: int
    failed_count: int
    errors: List[str] = Field(default_factory=list)


@router.post("/status", response_model=BulkResponse)
async def bulk_update_status(
    request: BulkStatusUpdate,
    current_user: User = Depends(get_current_user)
):
    """Bulk update candidate status"""
    success_count = 0
    failed_count = 0
    errors = []
    
    for resume_id in request.resume_ids:
        try:
            await candidate_service.update_candidate_status(
                resume_id=resume_id,
                new_status=request.status,
                user=current_user
            )
            success_count += 1
        except Exception as e:
            failed_count += 1
            errors.append(f"{resume_id}: {str(e)}")
    
    logger.info(
        "Bulk status update completed",
        success_count=success_count,
        failed_count=failed_count,
        user_id=str(current_user.id)
    )
    
    return BulkResponse(
        success_count=success_count,
        failed_count=failed_count,
        errors=errors
    )


@router.post("/tags", response_model=BulkResponse)
async def bulk_add_tags(
    request: BulkTagAdd,
    current_user: User = Depends(get_current_user)
):
    """Bulk add tags to candidates"""
    success_count = 0
    failed_count = 0
    errors = []
    
    for resume_id in request.resume_ids:
        try:
            await candidate_service.add_tag(
                resume_id=resume_id,
                tag=request.tag,
                user=current_user
            )
            success_count += 1
        except Exception as e:
            failed_count += 1
            errors.append(f"{resume_id}: {str(e)}")
    
    return BulkResponse(
        success_count=success_count,
        failed_count=failed_count,
        errors=errors
    )


@router.delete("/tags", response_model=BulkResponse)
async def bulk_remove_tags(
    http_request: Request,
    current_user: User = Depends(get_current_user)
):
    """Bulk remove tags from candidates"""
    # FastAPI doesn't parse body in DELETE requests automatically
    # So we need to parse it manually
    try:
        body = await http_request.body()
        if not body:
            from app.core.exceptions import ValidationException
            raise ValidationException("Request body is required")
        
        request_data = json.loads(body.decode('utf-8'))
        request = BulkTagRemove(**request_data)
    except json.JSONDecodeError as e:
        from app.core.exceptions import ValidationException
        raise ValidationException(f"Invalid JSON in request body: {str(e)}")
    except Exception as e:
        from app.core.exceptions import ValidationException
        raise ValidationException(f"Error parsing request body: {str(e)}")
    
    success_count = 0
    failed_count = 0
    errors = []
    
    for resume_id in request.resume_ids:
        try:
            await candidate_service.remove_tag(
                resume_id=resume_id,
                tag=request.tag,
                user=current_user
            )
            success_count += 1
        except Exception as e:
            failed_count += 1
            errors.append(f"{resume_id}: {str(e)}")
    
    return BulkResponse(
        success_count=success_count,
        failed_count=failed_count,
        errors=errors
    )


@router.post("/assign", response_model=BulkResponse)
async def bulk_assign(
    request: BulkAssign,
    current_user: User = Depends(get_current_user)
):
    """Bulk assign candidates to HR specialist"""
    success_count = 0
    failed_count = 0
    errors = []
    
    for resume_id in request.resume_ids:
        try:
            await candidate_service.assign_to_user(
                resume_id=resume_id,
                assigned_user_id=request.assigned_to_user_id,
                user=current_user
            )
            success_count += 1
        except Exception as e:
            failed_count += 1
            errors.append(f"{resume_id}: {str(e)}")
    
    return BulkResponse(
        success_count=success_count,
        failed_count=failed_count,
        errors=errors
    )


@router.post("/folder", response_model=BulkResponse)
async def bulk_set_folder(
    request: BulkFolderSet,
    current_user: User = Depends(get_current_user)
):
    """Bulk set folder for candidates"""
    success_count = 0
    failed_count = 0
    errors = []
    
    for resume_id in request.resume_ids:
        try:
            await candidate_service.set_folder(
                resume_id=resume_id,
                folder=request.folder,
                user=current_user
            )
            success_count += 1
        except Exception as e:
            failed_count += 1
            errors.append(f"{resume_id}: {str(e)}")
    
    return BulkResponse(
        success_count=success_count,
        failed_count=failed_count,
        errors=errors
    )
