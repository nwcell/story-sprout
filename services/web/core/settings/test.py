"""Test environment overrides for speed and isolation."""

# Security: Unsafe but fast password hashing for tests
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Email: In-memory backend for tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Cache: In-memory cache for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Celery: Synchronous execution for tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Allauth: No email verification for tests
ACCOUNT_EMAIL_VERIFICATION = "none"

# Database: Use in-memory SQLite for tests (faster)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
