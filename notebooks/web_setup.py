"""
Django environment setup for Jupyter notebooks.

Import this module at the start of your notebooks to load Django:
    import _setup
"""

import os
import sys
from pathlib import Path


def setup():
    # Add the web service root to Python path (where Django config is located)
    web_service_root = Path(__file__).parent.parent.parent / "web"
    sys.path.insert(0, str(web_service_root))

    # Set Django Environment Settings
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

    # Setup Django
    import django

    django.setup()

    # Import settings to make them available
    from django.conf import settings

    print("✅ Django environment loaded successfully!")
    print(f"📁 Web service root: {web_service_root}")
    print(f"🔧 Settings module: {settings.SETTINGS_MODULE}")
    print("🚀 Ready to use Django models and services")

    return settings


if __name__ == "__main__":
    setup()
