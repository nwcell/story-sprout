"""Development-only overrides and conveniences."""

# Security: Development conveniences (never use in production)
DEBUG = True
ALLOWED_HOSTS = ["*"]  # Allow all hosts for development
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://travis.local:8000",
]

# Email: Console backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Celery: Local Redis for development
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

# Cache: In-memory cache for development
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Allauth: Relaxed email verification for development
ACCOUNT_EMAIL_VERIFICATION = "none"
