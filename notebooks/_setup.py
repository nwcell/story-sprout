"""
Django environment setup for Jupyter notebooks.

Import this module at the start of your notebooks to load Django:
    import _setup
"""

import os
import sys
from pathlib import Path


def setup():
    # Add the project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    # Set Django Environment Settings
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

    # Setup Django
    import django

    django.setup()

    print("✅ Django environment loaded successfully!")
    print(f"📁 Project root: {project_root}")
    print("🚀 Ready to use Django models and services")


if __name__ == "__main__":
    setup()
