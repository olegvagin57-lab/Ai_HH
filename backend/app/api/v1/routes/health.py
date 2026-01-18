"""Health check API routes"""
from fastapi import APIRouter
from app.infrastructure.database.mongodb import check_mongodb_health
from app.core.logging import get_logger
from app.config import settings
import httpx
import asyncio


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


async def check_cloudflare_worker_health() -> dict:
    """Check Cloudflare Worker (AI service) health"""
    if not settings.cloudflare_worker_url:
        return {"status": "not_configured", "available": False}
    
    try:
        # Simple health check - try to reach the worker
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Try a simple GET request to check if worker is reachable
            response = await client.get(settings.cloudflare_worker_url, timeout=5.0)
            # Worker might return 404 for root, but that's OK - it means it's reachable
            available = response.status_code < 500
            return {
                "status": "healthy" if available else "unhealthy",
                "available": available,
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }
    except httpx.TimeoutException:
        return {"status": "timeout", "available": False}
    except Exception as e:
        logger.warning("Cloudflare Worker health check failed", error=str(e))
        return {"status": "unhealthy", "available": False, "error": str(e)}


@router.get("")
async def health_check():
    """General health check with detailed service status"""
    mongodb_healthy = await check_mongodb_health()
    redis_healthy = await check_redis_health()
    cloudflare_worker = await check_cloudflare_worker_health()
    
    # Core services (MongoDB, Redis) are critical
    core_healthy = mongodb_healthy and redis_healthy
    # External services (Cloudflare Worker) are not critical for basic operation
    overall_healthy = core_healthy
    status = "healthy" if overall_healthy else "unhealthy"
    
    return {
        "status": status,
        "version": "1.0.0",
        "services": {
            "mongodb": {
                "status": "healthy" if mongodb_healthy else "unhealthy",
                "critical": True
            },
            "redis": {
                "status": "healthy" if redis_healthy else "unhealthy",
                "critical": True
            },
            "cloudflare_worker": {
                "status": cloudflare_worker.get("status", "unknown"),
                "available": cloudflare_worker.get("available", False),
                "critical": False
            }
        }
    }


@router.get("/ready")
async def readiness_check():
    """Readiness probe for Kubernetes - checks critical services"""
    mongodb_healthy = await check_mongodb_health()
    redis_healthy = await check_redis_health()
    
    if not mongodb_healthy or not redis_healthy:
        from fastapi import status
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not ready",
                "services": {
                    "mongodb": "healthy" if mongodb_healthy else "unhealthy",
                    "redis": "healthy" if redis_healthy else "unhealthy"
                }
            }
        )
    
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """Liveness probe for Kubernetes - just checks if app is running"""
    return {"status": "alive"}


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with all service information"""
    mongodb_healthy = await check_mongodb_health()
    redis_healthy = await check_redis_health()
    cloudflare_worker = await check_cloudflare_worker_health()
    
    # Check Celery if available
    celery_healthy = True
    try:
        from celery_app.celery import celery_app
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        celery_healthy = stats is not None
    except Exception as e:
        logger.warning("Celery health check failed", error=str(e))
        celery_healthy = False
    
    core_healthy = mongodb_healthy and redis_healthy
    overall_healthy = core_healthy
    
    return {
        "status": "healthy" if overall_healthy else "unhealthy",
        "version": "1.0.0",
        "environment": settings.environment,
        "timestamp": asyncio.get_event_loop().time(),
        "services": {
            "mongodb": {
                "status": "healthy" if mongodb_healthy else "unhealthy",
                "critical": True,
                "url": settings.mongodb_url.split("@")[-1] if "@" in settings.mongodb_url else settings.mongodb_url
            },
            "redis": {
                "status": "healthy" if redis_healthy else "unhealthy",
                "critical": True,
                "url": settings.redis_url.split("@")[-1] if "@" in settings.redis_url else settings.redis_url
            },
            "cloudflare_worker": cloudflare_worker,
            "celery": {
                "status": "healthy" if celery_healthy else "unhealthy",
                "critical": False
            }
        }
    }
