import shlex
import subprocess

from django.core.management.base import BaseCommand
from django.utils import autoreload

CELERY_CMD = "celery -A core worker -l info --pool=solo"


def run_worker():
    return subprocess.call(shlex.split(CELERY_CMD))


class Command(BaseCommand):
    help = "Run Celery worker with auto-reload (dev only)"

    def handle(self, *args, **opts):
        self.stdout.write("Starting Celery worker with auto-reload…")
        autoreload.run_with_reloader(run_worker)
