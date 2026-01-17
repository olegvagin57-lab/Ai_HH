"""Rate limiting middleware"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
from app.core.logging import get_logger
from app.core.exceptions import RateLimitExceededException

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None


logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis or in-memory storage"""
    
    def __init__(self, app, redis_client=None):
        super().__init__(app)
        self.redis_client = redis_client
        self.enabled = settings.rate_limit_enabled
        self.per_minute = settings.rate_limit_per_minute
        self.per_hour = settings.rate_limit_per_hour
        self._memory_limits = {}  # In-memory fallback
    
    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/health/live", "/health/ready", "/metrics"]:
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check rate limits
        try:
            if self.redis_client and REDIS_AVAILABLE:
                allowed = await self._check_redis_limits(client_id)
            else:
                allowed = await self._check_memory_limits(client_id)
            
            if not allowed:
                logger.warning(
                    "Rate limit exceeded",
                    client_id=client_id,
                    path=request.url.path
                )
                raise RateLimitExceededException(
                    "Rate limit exceeded. Please try again later.",
                    retry_after=60
                )
        except RateLimitExceededException:
            raise
        except Exception as e:
            # If rate limiting fails, log but don't block request
            logger.error("Rate limiting error", error=str(e))
            # Allow request to proceed if rate limiting fails
        
        return await call_next(request)
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try to get user ID from request state
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # Fallback to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    async def _check_redis_limits(self, client_id: str) -> bool:
        """Check rate limits using Redis"""
        if not self.redis_client or not REDIS_AVAILABLE:
            return True
        
        try:
            minute_key = f"rate_limit:minute:{client_id}"
            hour_key = f"rate_limit:hour:{client_id}"
            
            # Check per-minute limit
            minute_count = await self.redis_client.get(minute_key)
            if minute_count and int(minute_count) >= self.per_minute:
                return False
            
            # Check per-hour limit
            hour_count = await self.redis_client.get(hour_key)
            if hour_count and int(hour_count) >= self.per_hour:
                return False
            
            # Increment counters
            pipe = self.redis_client.pipeline()
            pipe.incr(minute_key)
            pipe.expire(minute_key, 60)
            pipe.incr(hour_key)
            pipe.expire(hour_key, 3600)
            await pipe.execute()
            
            return True
        except Exception as e:
            logger.error("Redis rate limiting error", error=str(e))
            # Allow request if Redis fails
            return True
    
    async def _check_memory_limits(self, client_id: str) -> bool:
        """Fallback in-memory rate limiting"""
        now = int(time.time())
        minute_key = f"{client_id}:minute"
        hour_key = f"{client_id}:hour"
        
        # Clean old entries
        if minute_key in self._memory_limits:
            if now - self._memory_limits[minute_key]['time'] > 60:
                del self._memory_limits[minute_key]
        
        if hour_key in self._memory_limits:
            if now - self._memory_limits[hour_key]['time'] > 3600:
                del self._memory_limits[hour_key]
        
        # Check limits
        if minute_key in self._memory_limits:
            if self._memory_limits[minute_key]['count'] >= self.per_minute:
                return False
        
        if hour_key in self._memory_limits:
            if self._memory_limits[hour_key]['count'] >= self.per_hour:
                return False
        
        # Increment counters
        if minute_key not in self._memory_limits:
            self._memory_limits[minute_key] = {'count': 0, 'time': now}
        self._memory_limits[minute_key]['count'] += 1
        
        if hour_key not in self._memory_limits:
            self._memory_limits[hour_key] = {'count': 0, 'time': now}
        self._memory_limits[hour_key]['count'] += 1
        
        return True
