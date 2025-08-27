import datetime
import os

from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a JSON snapshot of the database"

    def handle(self, *args, **options):
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = settings.SNAPSHOTS_DIR / f"full-{timestamp}.json"
        os.makedirs(settings.SNAPSHOTS_DIR, exist_ok=True)

        management.call_command(
            "dumpdata",
            "--natural-foreign",
            "--natural-primary",
            "--indent",
            "2",
            "--exclude",
            "contenttypes",
            "--exclude",
            "auth.permission",
            "--exclude",
            "admin.logentry",
            "--exclude",
            "sessions",
            stdout=open(filename, "w"),  # noqa: SIM115, SIM117
        )
        self.stdout.write(self.style.SUCCESS(f"Snapshot saved to {filename}"))
