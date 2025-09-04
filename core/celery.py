import os

from celery import Celery
from celery_typed import register_preserializer
from celery_typed.codecs import PydanticModelDump
from pydantic import BaseModel

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("story_sprout")

# Register exactly as shown in blog post - at module level
register_preserializer(PydanticModelDump)(BaseModel)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Explicitly import task modules to ensure registration
app.autodiscover_tasks(["apps.ai"])
