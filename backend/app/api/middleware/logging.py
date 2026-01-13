"""Logging middleware with correlation ID"""
import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_logger, set_correlation_id, clear_correlation_id
from app.core.metrics import track_api_call


logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging with correlation ID"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        set_correlation_id(correlation_id)
        
        # Start timing
        start_time = time.time()
        
        # Extract request info
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else ""
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log request start
        logger.info(
            "Request started",
            method=method,
            path=path,
            query_params=query_params,
            client_ip=client_ip,
            user_agent=user_agent,
            correlation_id=correlation_id
        )
        
        try:
            # Process request
            response: Response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Extract user ID if available
            user_id = getattr(request.state, "user_id", None)
            
            # Track metrics
            track_api_call(
                method=method,
                endpoint=path,
                status_code=response.status_code,
                duration=duration
            )
            
            # Log successful request
            logger.info(
                "Request completed",
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
                user_id=user_id,
                correlation_id=correlation_id
            )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
            
        except Exception as e:
            # Calculate duration for failed request
            duration = time.time() - start_time
            
            # Track error metrics
            track_api_call(
                method=method,
                endpoint=path,
                status_code=500,
                duration=duration
            )
            
            # Log failed request
            logger.error(
                "Request failed",
                method=method,
                path=path,
                duration_ms=round(duration * 1000, 2),
                error=str(e),
                correlation_id=correlation_id,
                exc_info=True
            )
            
            # Re-raise the exception
            raise
            
        finally:
            # Clear correlation ID
            clear_correlation_id()
