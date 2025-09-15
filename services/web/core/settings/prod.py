"""Production-only security hardening and optimizations."""

from pathlib import Path

import environ

# Initialize django-environ
env = environ.Env()

# Load .env from project root
_project_root = Path(__file__).resolve().parent.parent.parent.parent
_env_path = _project_root / ".env"
if _env_path.exists():
    env.read_env(_env_path)

# Security: Enforce HTTPS and security headers
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 2592000  # 30 days
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# Cache: Redis cache for production (environment-driven)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_CACHE_URL", default="redis://127.0.0.1:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Logging: Production-optimized logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "loguru": {"()": "core.logging.InterceptHandler"},
    },
    "root": {"handlers": ["loguru"], "level": "WARNING"},  # Less verbose in prod
    "loggers": {
        "django": {"level": "WARNING", "propagate": True},
        "django.server": {"level": "ERROR", "propagate": True},
        "django.request": {"level": "WARNING", "propagate": True},
    },
}

# Session: More secure session settings
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
