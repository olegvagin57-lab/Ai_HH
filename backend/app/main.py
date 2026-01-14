"""FastAPI application entry point"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from prometheus_client import make_asgi_app

from app.config import settings
from app.core.logging import get_logger, configure_logging
from app.core.exceptions import AppException
from app.infrastructure.database.mongodb import connect_to_mongo, close_mongo_connection
from app.api.middleware.logging import LoggingMiddleware
from app.api.middleware.rate_limit import RateLimitMiddleware
from app.api.middleware.error_handler import (
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)

# Initialize logging
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting HH Resume Analyzer API", version="1.0.0")
    
    if settings.environment == "production" and settings.debug:
        logger.warning("Running in production with DEBUG=True")
    
    if settings.environment == "production" and settings.secret_key == "your-secret-key-here-change-in-production":
        logger.error("SECRET_KEY is not changed from default in production!")
    
    # Connect to MongoDB
    try:
        await connect_to_mongo()
        logger.info("MongoDB connection established")
    except Exception as e:
        logger.error("Failed to connect to MongoDB", error=str(e), exc_info=True)
        raise
    
    # Initialize default roles and permissions
    try:
        from app.application.services.auth_service import AuthService
        auth_service = AuthService()
        await auth_service.initialize_default_roles_and_permissions()
        logger.info("Default roles and permissions initialized")
    except Exception as e:
        logger.error("Failed to initialize roles and permissions", error=str(e), exc_info=True)
    
    yield
    
    # Shutdown
    logger.info("Shutting down HH Resume Analyzer API")
    await close_mongo_connection()


# Create FastAPI app
app = FastAPI(
    title="HH Resume Analyzer",
    description="AI-powered resume analysis system for HeadHunter",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan
)

# Add exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Add middleware (order matters!)
app.add_middleware(LoggingMiddleware)

# Add rate limiting middleware
try:
    import redis.asyncio as redis
    redis_client = None
    try:
        redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        logger.info("Redis connection established for rate limiting")
    except Exception as e:
        logger.warning("Redis connection failed, using in-memory rate limiting", error=str(e))
    app.add_middleware(RateLimitMiddleware, redis_client=redis_client)
except ImportError:
    logger.warning("Redis not available, using in-memory rate limiting")
    app.add_middleware(RateLimitMiddleware, redis_client=None)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include API routers
from app.api.v1.routes import auth, users, search, export, health, candidates, vacancy, comments, comparison, notifications, analytics, bulk_actions

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(export.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")
app.include_router(candidates.router, prefix="/api/v1")
app.include_router(vacancy.router, prefix="/api/v1")
app.include_router(comments.router, prefix="/api/v1")
app.include_router(comparison.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(bulk_actions.router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "HH Resume Analyzer API",
        "version": "1.0.0",
        "environment": settings.environment
    }

# Health check endpoint (basic)
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
