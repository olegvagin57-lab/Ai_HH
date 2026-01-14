"""Comments and collaboration API routes"""
from fastapi import APIRouter, Depends, Query, status
from app.api.v1.schemas.collaboration import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    CommentListResponse,
    ActivityFeedResponse,
    ActivityItem,
    RatingsSummaryResponse
)
from app.application.services.collaboration_service import collaboration_service
from app.api.middleware.auth import get_current_user
from app.domain.entities.user import User
from app.core.logging import get_logger
from app.core.exceptions import NotFoundException


logger = get_logger(__name__)
router = APIRouter(prefix="/comments", tags=["collaboration"])


@router.post("/resume/{resume_id}", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    resume_id: str,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a comment on a candidate"""
    comment = await collaboration_service.create_comment(
        resume_id=resume_id,
        user=current_user,
        content=comment_data.content,
        parent_comment_id=comment_data.parent_comment_id,
        is_internal=comment_data.is_internal
    )
    
    return CommentResponse(
        id=str(comment.id),
        resume_id=comment.resume_id,
        user_id=comment.user_id,
        content=comment.content,
        mentions=comment.mentions,
        parent_comment_id=comment.parent_comment_id,
        is_internal=comment.is_internal,
        created_at=comment.created_at.isoformat(),
        updated_at=comment.updated_at.isoformat()
    )


@router.get("/resume/{resume_id}", response_model=CommentListResponse)
async def get_comments(
    resume_id: str,
    limit: int = Query(50, ge=1, le=200),
    include_replies: bool = Query(True),
    current_user: User = Depends(get_current_user)
):
    """Get comments for a candidate"""
    comments = await collaboration_service.get_comments(
        resume_id=resume_id,
        limit=limit,
        include_replies=include_replies
    )
    
    comment_list = []
    for comment in comments:
        comment_list.append(CommentResponse(
            id=str(comment.id),
            resume_id=comment.resume_id,
            user_id=comment.user_id,
            content=comment.content,
            mentions=comment.mentions,
            parent_comment_id=comment.parent_comment_id,
            is_internal=comment.is_internal,
            created_at=comment.created_at.isoformat(),
            updated_at=comment.updated_at.isoformat()
        ))
    
    return CommentListResponse(
        comments=comment_list,
        total=len(comment_list)
    )


@router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: str,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a comment"""
    comment = await collaboration_service.update_comment(
        comment_id=comment_id,
        user=current_user,
        content=comment_data.content
    )
    
    return CommentResponse(
        id=str(comment.id),
        resume_id=comment.resume_id,
        user_id=comment.user_id,
        content=comment.content,
        mentions=comment.mentions,
        parent_comment_id=comment.parent_comment_id,
        is_internal=comment.is_internal,
        created_at=comment.created_at.isoformat(),
        updated_at=comment.updated_at.isoformat()
    )


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a comment"""
    await collaboration_service.delete_comment(
        comment_id=comment_id,
        user=current_user
    )


@router.get("/activity/feed", response_model=ActivityFeedResponse)
async def get_activity_feed(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user)
):
    """Get activity feed"""
    activities = await collaboration_service.get_activity_feed(
        user=current_user,
        limit=limit
    )
    
    activity_list = []
    for activity in activities:
        activity_list.append(ActivityItem(
            type=activity["type"],
            id=activity["id"],
            resume_id=activity["resume_id"],
            user_id=activity["user_id"],
            content=activity.get("content"),
            action_data=activity.get("action_data"),
            created_at=activity["created_at"]
        ))
    
    return ActivityFeedResponse(
        activities=activity_list,
        total=len(activity_list)
    )


@router.get("/resume/{resume_id}/ratings", response_model=RatingsSummaryResponse)
async def get_ratings_summary(
    resume_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get ratings summary for a candidate"""
    summary = await collaboration_service.get_candidate_ratings_summary(resume_id)
    
    return RatingsSummaryResponse(
        average_rating=summary["average_rating"],
        total_ratings=summary["total_ratings"],
        ratings_breakdown=summary["ratings_breakdown"]
    )
