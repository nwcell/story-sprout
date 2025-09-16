import os
import sys
from logging.config import dictConfig
from pathlib import Path

from celery import Celery
from celery.signals import setup_logging
from celery_typed import register_preserializer
from celery_typed.codecs import PydanticModelDump
from django.conf import settings
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("story_sprout")

register_preserializer(PydanticModelDump)(BaseModel)

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.autodiscover_tasks(["apps.ai"])


@setup_logging.connect
def configure_celery_logging(*args, **kwargs):
    dictConfig(settings.LOGGING)
