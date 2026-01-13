"""Health check API routes"""
from fastapi import APIRouter
from app.infrastructure.database.mongodb import check_mongodb_health
from app.core.logging import get_logger
from app.config import settings


logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["health"])


async def check_redis_health() -> bool:
    """Check Redis connection health"""
    try:
        import redis.asyncio as redis
        redis_client = redis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=2)
        await redis_client.ping()
        await redis_client.close()
        return True
    except ImportError:
        logger.warning("Redis not available (import failed)")
        return False
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        return False


@router.get("")
async def health_check():
    """General health check"""
    mongodb_healthy = await check_mongodb_health()
    redis_healthy = await check_redis_health()
    
    overall_healthy = mongodb_healthy and redis_healthy
    status = "healthy" if overall_healthy else "unhealthy"
    
    return {
        "status": status,
        "mongodb": "healthy" if mongodb_healthy else "unhealthy",
        "redis": "healthy" if redis_healthy else "unhealthy"
    }


@router.get("/ready")
async def readiness_check():
    """Readiness probe for Kubernetes"""
    mongodb_healthy = await check_mongodb_health()
    redis_healthy = await check_redis_health()
    
    if not mongodb_healthy or not redis_healthy:
        from fastapi import status
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not ready",
                "mongodb": "healthy" if mongodb_healthy else "unhealthy",
                "redis": "healthy" if redis_healthy else "unhealthy"
            }
        )
    
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """Liveness probe for Kubernetes"""
    return {"status": "alive"}
