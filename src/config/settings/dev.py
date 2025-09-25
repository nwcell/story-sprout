"""Development-only overrides and conveniences."""

from pathlib import Path

import environ

# Initialize django-environ
env = environ.Env()

# Load .env from project root
_project_root = Path(__file__).resolve().parent.parent.parent.parent
_env_path = _project_root / ".env"
if _env_path.exists():
    env.read_env(_env_path)

# Security: Development conveniences (never use in production)
DEBUG = True
ALLOWED_HOSTS = ["*"]  # Allow all hosts for development

# CSRF: Allow common development hosts + any custom ones from environment
_default_origins = ["http://localhost:8000", "http://127.0.0.1:8000"]
_custom_origins = env.list("DEV_CSRF_TRUSTED_ORIGINS", default=[])
CSRF_TRUSTED_ORIGINS = _default_origins + _custom_origins

# Email: Console backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Celery: Environment-driven with sensible defaults
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/0")

# Cache: Environment-driven with in-memory fallback
# _cache_backend = env("CACHE_BACKEND", default="locmem")
# if _cache_backend == "redis":
#     CACHES = {
#         "default": {
#             "BACKEND": "django.core.cache.backends.redis.RedisCache",
#             "LOCATION": env("REDIS_CACHE_URL", default="redis://127.0.0.1:6379/1"),
#         }
#     }
# else:
#     CACHES = {
#         "default": {
#             "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
#         }
#     }

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Allauth: Relaxed email verification for development
ACCOUNT_EMAIL_VERIFICATION = "none"
