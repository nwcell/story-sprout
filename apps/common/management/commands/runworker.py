import shlex
import subprocess

import psutil
from django.core.management.base import BaseCommand
from django.utils import autoreload

CELERY_CMD = "celery -A core worker -l info --pool=solo -n dev_worker@localhost"


def kill_existing_workers():
    """Kill any existing Celery workers to ensure only one runs."""
    killed = []
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            if proc.info["name"] and "python" in proc.info["name"].lower():
                cmdline = " ".join(proc.info["cmdline"] or [])
                if "celery" in cmdline and "worker" in cmdline and "core" in cmdline:
                    print(f"Killing existing Celery worker (PID: {proc.info['pid']})")
                    proc.kill()
                    killed.append(proc.info["pid"])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if killed:
        print(f"Killed {len(killed)} existing worker(s): {killed}")
    else:
        print("No existing workers found")

    return len(killed)


def run_worker():
    # Always kill existing workers first
    kill_existing_workers()

    print(f"Starting single Celery worker: {CELERY_CMD}")
    return subprocess.call(shlex.split(CELERY_CMD))


class Command(BaseCommand):
    help = "Run Celery worker with auto-reload (dev only)"

    def handle(self, *args, **opts):
        self.stdout.write("Starting Celery worker with auto-reload…")
        autoreload.run_with_reloader(run_worker)
