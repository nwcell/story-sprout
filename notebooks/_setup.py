"""
Django environment setup for Jupyter notebooks.

Import this module at the start of your notebooks to load Django:
    import _setup
"""

import os
import sys
from pathlib import Path


def setup():
    # Add the web service root to Python path (where Django core is located)
    web_service_root = Path(__file__).parent.parent / "services" / "web"
    print(f"🔍 Calculated web service root: {web_service_root}")
    print(f"🔍 Path exists: {web_service_root.exists()}")
    print(f"🔍 Core directory exists: {(web_service_root / 'core').exists()}")

    sys.path.insert(0, str(web_service_root))
    print(f"🔍 Python path now includes: {str(web_service_root)}")

    # Set Django Environment Settings
    os.environ.setdefault("DJANGO_ENV", "dev")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

    # Setup Django
    import django

    django.setup()

    print("✅ Django environment loaded successfully!")
    print(f"📁 Web service root: {web_service_root}")
    print("🚀 Ready to use Django models and services")


if __name__ == "__main__":
    setup()
