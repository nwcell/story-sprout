import os
import sys
from logging.config import dictConfig
from pathlib import Path

from celery import Celery
from celery.signals import setup_logging
from celery_typed import register_pydantic_serializer
from django.conf import settings

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("story_sprout")

register_pydantic_serializer()  # One line setup as per README!

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.autodiscover_tasks(["apps.ai"])


@setup_logging.connect
def config_loggers(*args, **kwargs):
    """Configure Celery workers to use Django logging settings."""
    import logging

    # Apply Django's LOGGING configuration
    dictConfig(settings.LOGGING)

    # Test that logging is working immediately after setup
    test_logger = logging.getLogger("apps")
    test_logger.info("🔧 Celery worker logging initialized via setup_logging signal")

    # Also test the specific task logger
    task_logger = logging.getLogger("apps.ai.tasks")
    task_logger.info("🔧 Task logger configured and ready")
