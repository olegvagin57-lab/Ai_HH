"""Global error handler middleware"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.exceptions import AppException
from app.core.logging import get_logger


logger = get_logger(__name__)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle application exceptions"""
    logger.error(
        "Application error",
        error_type=exc.__class__.__name__,
        status_code=exc.status_code,
        message=exc.message,
        details=exc.details,
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "details": exc.details,
            "path": request.url.path
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    logger.warning(
        "HTTP error",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors"""
    errors = exc.errors()
    logger.warning(
        "Validation error",
        path=request.url.path,
        method=request.method,
        errors=errors
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "Validation error",
            "details": errors,
            "path": request.url.path
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions"""
    logger.error(
        "Unhandled exception",
        exception_type=exc.__class__.__name__,
        error=str(exc),
        path=request.url.path,
        method=request.method,
        exc_info=True
    )
    
    # Don't expose internal errors in production
    from app.config import settings
    if settings.debug:
        error_message = str(exc)
    else:
        error_message = "Internal server error"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": error_message,
            "path": request.url.path
        }
    )
