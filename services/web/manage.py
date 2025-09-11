#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys

from dotenv import load_dotenv


def main():
    """Run administrative tasks."""
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    load_dotenv()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

    # Handle runserver with env defaults
    if len(sys.argv) == 2 and sys.argv[1] == "runserver":
        host = os.getenv("RUNSERVER_HOST")
        if host:
            sys.argv.append(host)

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
