#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys
from pathlib import Path

from django.core.management import execute_from_command_line
from dotenv import find_dotenv, load_dotenv


def _bootstrap_paths() -> None:
    """Ensure `src/` is importable (works from project root or subdirs)."""
    # Typical layout: project-root/manage.py and project-root/src/...
    root = Path(__file__).resolve().parent
    candidates = [
        root / "src",
        root.parent / "src",  # if manage.py lives in a subdir
    ]
    for p in candidates:
        if p.exists():
            sys.path.insert(0, str(p))
            break


def _load_env() -> None:
    """Load .env.local (override) then .env."""
    # Load .env.local first if present, then .env (without overriding already-set vars)
    local_path = find_dotenv(".env.local", usecwd=True)
    if local_path:
        load_dotenv(local_path, override=True)
    load_dotenv(find_dotenv(usecwd=True), override=False)


def main():
    """Run administrative tasks."""
    _bootstrap_paths()
    _load_env()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    # Handle runserver with env defaults
    if len(sys.argv) == 2 and sys.argv[1] == "runserver":
        host = os.getenv("RUNSERVER_HOST")
        if host:
            sys.argv.append(host)

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
