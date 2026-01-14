"""Analytics API routes"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.application.services.analytics_service import analytics_service
from app.api.middleware.auth import get_current_user
from app.domain.entities.user import User
from app.core.logging import get_logger
from pydantic import BaseModel
from typing import Dict, Any, List


logger = get_logger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard")
async def get_dashboard(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get dashboard metrics"""
    metrics = await analytics_service.get_dashboard_metrics(
        user=current_user,
        days=days
    )
    return metrics


@router.get("/vacancy/{vacancy_id}")
async def get_vacancy_analytics(
    vacancy_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get analytics for a specific vacancy"""
    analytics = await analytics_service.get_vacancy_analytics(
        vacancy_id=vacancy_id,
        user=current_user
    )
    return analytics


@router.get("/funnel")
async def get_hiring_funnel(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get hiring funnel metrics"""
    funnel = await analytics_service.get_hiring_funnel(
        user=current_user,
        days=days
    )
    return funnel
