"""Celery application configuration"""
from celery import Celery
from app.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)

# Create Celery app
celery_app = Celery(
    "hh_analyzer",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["celery_app.tasks.search_tasks", "celery_app.tasks.ai_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

logger.info("Celery app configured", broker=settings.redis_url)
