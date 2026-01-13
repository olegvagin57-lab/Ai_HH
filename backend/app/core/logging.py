"""Structured logging configuration"""
import logging
import sys
from typing import Any, Dict, Optional
import structlog
from structlog.stdlib import LoggerFactory
from app.config import settings


def configure_logging() -> None:
    """Configure structured logging"""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )
    
    # Configure structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if settings.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """Get a logger instance"""
    return structlog.get_logger(name)


# Correlation ID context variable
_correlation_id: Optional[str] = None


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID for request tracing"""
    global _correlation_id
    _correlation_id = correlation_id
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)


def get_correlation_id() -> Optional[str]:
    """Get current correlation ID"""
    return _correlation_id


def clear_correlation_id() -> None:
    """Clear correlation ID"""
    global _correlation_id
    _correlation_id = None
    structlog.contextvars.clear_contextvars()


# Initialize logging on import
configure_logging()

# Global logger instance
logger = get_logger(__name__)
