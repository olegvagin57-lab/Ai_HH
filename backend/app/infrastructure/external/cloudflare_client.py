"""Cloudflare Worker client for Gemini API with circuit breaker"""
import asyncio
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import httpx
from app.config import settings
from app.core.logging import get_logger
from app.core.exceptions import ExternalServiceException
from app.core.metrics import track_ai_request, track_external_service_request


logger = get_logger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker for external service calls"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self._lock = asyncio.Lock()
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        async with self._lock:
            # Check if we should attempt recovery
            if self.state == CircuitState.OPEN:
                if self.last_failure_time:
                    elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                    if elapsed >= self.timeout:
                        self.state = CircuitState.HALF_OPEN
                        self.success_count = 0
                        logger.info("Circuit breaker entering HALF_OPEN state")
                    else:
                        raise ExternalServiceException(
                            "cloudflare_worker",
                            "Circuit breaker is OPEN. Service unavailable."
                        )
        
        try:
            # Execute the function
            result = await func(*args, **kwargs)
            
            # On success
            async with self._lock:
                if self.state == CircuitState.HALF_OPEN:
                    self.success_count += 1
                    if self.success_count >= self.success_threshold:
                        self.state = CircuitState.CLOSED
                        self.failure_count = 0
                        logger.info("Circuit breaker CLOSED. Service recovered.")
                elif self.state == CircuitState.CLOSED:
                    self.failure_count = 0
            
            return result
            
        except Exception as e:
            # On failure
            async with self._lock:
                self.failure_count += 1
                self.last_failure_time = datetime.utcnow()
                
                if self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.OPEN
                    self.success_count = 0
                    logger.warning("Circuit breaker OPENED. Service still failing.")
                elif self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold:
                    self.state = CircuitState.OPEN
                    logger.warning("Circuit breaker OPENED. Too many failures.")
            
            raise


class CloudflareWorkerClient:
    """Client for Cloudflare Worker (Gemini API proxy)"""
    
    def __init__(self):
        self.worker_url = settings.cloudflare_worker_url
        self.timeout = 30.0
        self.max_retries = 3
        self.retry_delay = 1.0
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60,
            success_threshold=2
        )
    
    async def _make_request(
        self,
        endpoint: str,
        data: Dict[str, Any],
        method: str = "POST"
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        url = f"{self.worker_url}/{endpoint}"
        
        async def _request():
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                for attempt in range(self.max_retries):
                    try:
                        if method == "POST":
                            response = await client.post(url, json=data)
                        else:
                            response = await client.get(url, params=data)
                        
                        response.raise_for_status()
                        return response.json()
                        
                    except httpx.TimeoutException:
                        if attempt == self.max_retries - 1:
                            raise ExternalServiceException(
                                "cloudflare_worker",
                                f"Request timeout after {self.max_retries} attempts"
                            )
                        await asyncio.sleep(self.retry_delay * (attempt + 1))
                        
                    except httpx.HTTPStatusError as e:
                        if e.response.status_code >= 500:
                            # Retry on server errors
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(self.retry_delay * (attempt + 1))
                                continue
                        raise ExternalServiceException(
                            "cloudflare_worker",
                            f"HTTP error: {e.response.status_code} - {e.response.text}"
                        )
                    except Exception as e:
                        raise ExternalServiceException(
                            "cloudflare_worker",
                            f"Request failed: {str(e)}"
                        )
        
        # Execute with circuit breaker
        start_time = asyncio.get_event_loop().time()
        try:
            result = await self.circuit_breaker.call(_request)
            duration = asyncio.get_event_loop().time() - start_time
            track_ai_request("cloudflare_worker", "success", duration)
            track_external_service_request("cloudflare_worker", "success")
            return result
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            track_ai_request("cloudflare_worker", "error", duration)
            track_external_service_request("cloudflare_worker", "error")
            raise
    
    async def extract_concepts(self, query: str) -> List[List[str]]:
        """
        Extract concepts from search query
        Returns: List of concept arrays, e.g. [["concept1", "synonym1"], ["concept2", "synonym2"]]
        """
        try:
            data = {"query": query}
            response = await self._make_request("extract_concepts", data)
            
            # Parse response
            concepts = response.get("concepts", [])
            if not isinstance(concepts, list):
                raise ExternalServiceException(
                    "cloudflare_worker",
                    "Invalid response format: concepts must be a list"
                )
            
            logger.info("Concepts extracted", query=query, count=len(concepts))
            return concepts
            
        except ExternalServiceException:
            raise
        except Exception as e:
            logger.error("Failed to extract concepts", error=str(e), exc_info=True)
            raise ExternalServiceException(
                "cloudflare_worker",
                f"Failed to extract concepts: {str(e)}"
            )
    
    async def analyze_resume(
        self,
        resume_text: str,
        concepts: List[List[str]],
        vacancy_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze resume using AI with detailed semantic evaluation and explanations
        Returns: {
            "score": int (1-10),
            "summary": str,  # Detailed explanation why this candidate is suitable
            "match_explanation": str,  # Detailed explanation of match with requirements
            "strengths": List[str],  # Key strengths of the candidate
            "weaknesses": List[str],  # Areas for improvement
            "questions": List[str],
            "ai_generated_detected": bool,
            "evaluation_details": {
                "technical_skills": {"score": float, "details": str, "explanation": str},
                "experience": {"score": float, "details": str, "explanation": str},
                "education": {"score": float, "details": str, "explanation": str},
                "soft_skills": {"score": float, "details": str, "explanation": str}
            },
            "match_percentage": float (0-100),
            "red_flags": List[str],
            "recommendation": str  # Why this candidate is recommended (or not)
        }
        """
        try:
            data = {
                "resume_text": resume_text,
                "concepts": concepts
            }
            if vacancy_requirements:
                data["vacancy_requirements"] = vacancy_requirements
            
            response = await self._make_request("analyze_resume", data)
            
            # Validate response
            required_fields = ["score", "summary", "questions", "ai_generated_detected"]
            for field in required_fields:
                if field not in response:
                    raise ExternalServiceException(
                        "cloudflare_worker",
                        f"Invalid response format: missing field '{field}'"
                    )
            
            # Ensure all fields are present (with defaults if not)
            if "evaluation_details" not in response:
                response["evaluation_details"] = None
            if "match_percentage" not in response:
                response["match_percentage"] = None
            if "red_flags" not in response:
                response["red_flags"] = []
            if "match_explanation" not in response:
                response["match_explanation"] = response.get("summary", "")
            if "strengths" not in response:
                response["strengths"] = []
            if "weaknesses" not in response:
                response["weaknesses"] = []
            if "recommendation" not in response:
                response["recommendation"] = response.get("summary", "")
            
            logger.info("Resume analyzed with semantic evaluation", score=response.get("score"))
            return response
            
        except ExternalServiceException:
            raise
        except Exception as e:
            logger.error("Failed to analyze resume", error=str(e), exc_info=True)
            raise ExternalServiceException(
                "cloudflare_worker",
                f"Failed to analyze resume: {str(e)}"
            )


# Global client instance
cloudflare_client = CloudflareWorkerClient()
