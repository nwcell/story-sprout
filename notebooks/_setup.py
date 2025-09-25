"""
Django environment setup for Jupyter notebooks.

Import this module at the start of your notebooks to load Django:
    import _setup
"""

import logging
import os
import sys
from pathlib import Path

from dotenv import find_dotenv, load_dotenv


def setup():
    logger = logging.getLogger(__name__)

    # Add the web service root to Python path (where Django config is located)
    web_service_root = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(web_service_root))

    # Load .env file first (following manage.py pattern)
    load_dotenv(find_dotenv(usecwd=True), override=False)

    # Set Django Environment Settings (following established pattern)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

    # Setup Django
    import django

    django.setup()

    logger.info("Django environment loaded successfully")


if __name__ == "__main__":
    setup()
