"""Prometheus metrics collection"""
from prometheus_client import Counter, Histogram, Gauge
from typing import Optional


# API metrics
api_requests_total = Counter(
    "api_requests_total",
    "Total number of API requests",
    ["method", "endpoint", "status_code"]
)

api_request_duration = Histogram(
    "api_request_duration_seconds",
    "API request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# Search metrics
searches_total = Counter(
    "searches_total",
    "Total number of searches",
    ["status"]
)

resumes_analyzed_total = Counter(
    "resumes_analyzed_total",
    "Total number of resumes analyzed",
    ["analysis_type"]
)

# AI service metrics
ai_requests_total = Counter(
    "ai_requests_total",
    "Total number of AI service requests",
    ["service", "status"]
)

ai_request_duration = Histogram(
    "ai_request_duration_seconds",
    "AI service request duration in seconds",
    ["service"]
)

# External service metrics
external_service_requests_total = Counter(
    "external_service_requests_total",
    "Total number of external service requests",
    ["service", "status"]
)

# Active connections
active_connections = Gauge(
    "active_connections",
    "Number of active connections",
    ["type"]
)


def track_api_call(
    method: str,
    endpoint: str,
    status_code: int,
    duration: float
) -> None:
    """Track API call metrics"""
    api_requests_total.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    api_request_duration.labels(method=method, endpoint=endpoint).observe(duration)


def track_search_created(status: str) -> None:
    """Track search creation"""
    searches_total.labels(status=status).inc()


def track_resume_analyzed(analysis_type: str) -> None:
    """Track resume analysis"""
    resumes_analyzed_total.labels(analysis_type=analysis_type).inc()


def track_ai_request(service: str, status: str, duration: Optional[float] = None) -> None:
    """Track AI service request"""
    ai_requests_total.labels(service=service, status=status).inc()
    if duration is not None:
        ai_request_duration.labels(service=service).observe(duration)


def track_external_service_request(service: str, status: str) -> None:
    """Track external service request"""
    external_service_requests_total.labels(service=service, status=status).inc()
