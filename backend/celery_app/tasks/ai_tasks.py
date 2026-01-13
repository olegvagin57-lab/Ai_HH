"""Celery tasks for AI processing"""
from celery_app.celery import celery_app
from app.core.logging import get_logger


logger = get_logger(__name__)


# AI-specific tasks can be added here if needed
# Currently, AI processing is integrated into search_tasks
