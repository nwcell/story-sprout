"""Test environment overrides for speed and isolation."""

# Security: Use test-only secret key (unsafe but fine for tests)
# SECRET_KEY = "django-insecure-test-key-only-for-testing-do-not-use-in-production"

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
