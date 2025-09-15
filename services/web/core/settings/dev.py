"""Development-only overrides and conveniences."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
_project_root = Path(__file__).resolve().parent.parent.parent.parent
_env_path = _project_root / ".env"
if _env_path.exists():
    load_dotenv(_env_path, override=False)

# Security: Development conveniences (never use in production)
DEBUG = True
ALLOWED_HOSTS = ["*"]  # Allow all hosts for development

# CSRF: Allow common development hosts + any custom ones from environment
_default_origins = ["http://localhost:8000", "http://127.0.0.1:8000"]
_custom_origins = os.environ.get("DEV_CSRF_TRUSTED_ORIGINS", "").split(",")
CSRF_TRUSTED_ORIGINS = _default_origins + [o.strip() for o in _custom_origins if o.strip()]

# Email: Console backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Celery: Environment-driven with sensible defaults
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Cache: Environment-driven with in-memory fallback
_cache_backend = os.environ.get("CACHE_BACKEND", "locmem")
if _cache_backend == "redis":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": os.environ.get("REDIS_CACHE_URL", "redis://127.0.0.1:6379/1"),
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }

# Allauth: Relaxed email verification for development
ACCOUNT_EMAIL_VERIFICATION = "none"
