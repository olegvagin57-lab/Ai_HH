"""Health check API routes"""
from fastapi import APIRouter
from app.infrastructure.database.mongodb import check_mongodb_health
from app.core.logging import get_logger


logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """General health check"""
    mongodb_healthy = await check_mongodb_health()
    
    status = "healthy" if mongodb_healthy else "unhealthy"
    
    return {
        "status": status,
        "mongodb": "healthy" if mongodb_healthy else "unhealthy"
    }


@router.get("/ready")
async def readiness_check():
    """Readiness probe for Kubernetes"""
    mongodb_healthy = await check_mongodb_health()
    
    if not mongodb_healthy:
        from fastapi import status
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready", "mongodb": "unhealthy"}
        )
    
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """Liveness probe for Kubernetes"""
    return {"status": "alive"}
