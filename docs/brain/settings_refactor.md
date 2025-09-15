# Django Settings Refactor (Zero-Behavior-Change Plan)

**Goal:** Convert a single `settings.py` into a layered settings package without changing any effective runtime values across dev, test, or prod.

## Hard Invariants (Must Stay True)

- ✅ **No effective value changes** (DB/caches/email/apps/middleware/logging/etc.)
- ✅ **Same import path for Django:** `DJANGO_SETTINGS_MODULE` remains `<project_pkg>.settings`
- ✅ **No secrets/hosts/paths edited:** only code moved
- ✅ **Idempotent:** running the refactor twice should not duplicate or alter behavior

**Current reality:** single `settings.py`. We will move it to `settings/base.py` and add thin overlays that are empty (no values set) so nothing changes.

## Target Layout

```
<repo>/
  <project_pkg>/
    settings/
      __init__.py   # re-exports base, then optional overlay via DJANGO_ENV
      base.py       # verbatim copy of existing settings.py
      dev.py        # (empty overlay; comments only)
      test.py       # (empty overlay; comments only)
      prod.py       # (empty overlay; comments only)
```

**Note:** Replace `<project_pkg>` with your actual Django project package name (in this case: `core`).

**For Story Sprout specifically:** Replace all instances of `<project_pkg>` with `core` in the commands above.

## Pre-Flight Checklist

- [ ] **Confirm current settings module** (usually `<project_pkg>.settings`)
- [ ] **Record current Python version** and dependencies used in CI and locally
- [ ] **Ensure the repo is clean** (`git status` shows no local changes)
- [ ] **Verify working test suite** command (e.g., `uv run -m pytest`)
- [ ] **Verify working management** command (e.g., `python manage.py check`)
- [ ] **Document baseline metrics:**
  - [ ] Current settings hash (see verification script below)
  - [ ] Test count and duration
  - [ ] Any existing warnings from `manage.py check`

## Step-By-Step Refactor (Mechanical, No Edits)

**Use these exact steps. Do not change values inside your current settings.**

### Phase 1: Create Settings Package Structure

- [ ] **Create the settings package directory:**
  ```bash
  mkdir -p <project_pkg>/settings
  ```

- [ ] **Move existing file verbatim:**
  ```bash
  git mv <project_pkg>/settings.py <project_pkg>/settings/base.py
  ```

### Phase 2: Create Overlay Loader

- [ ] **Create `<project_pkg>/settings/__init__.py`:**
  ```python
  import os as _os
  from .base import *  # noqa: F401,F403  (re-export everything from legacy settings)
  
  _env = _os.getenv("DJANGO_ENV", "dev")
  _mod = f"{__name__}.{_env}"
  
  try:
      _m = __import__(_mod, fromlist=["*"])
  except ModuleNotFoundError:
      _m = None
  
  if _m:
      for _k in dir(_m):
          if _k.isupper():
              globals()[_k] = getattr(_m, _k)
  ```

### Phase 3: Create Empty Environment Overlays

- [ ] **Create `<project_pkg>/settings/dev.py`:**
  ```python
  """Development-only overrides. Intentionally empty to preserve behavior."""
  # Example (future): DEBUG = True
  ```

- [ ] **Create `<project_pkg>/settings/test.py`:**
  ```python
  """Pytest-only overrides. Intentionally empty to preserve behavior."""
  # Example (future): PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
  ```

- [ ] **Create `<project_pkg>/settings/prod.py`:**
  ```python
  """Production-only hardening. Intentionally empty to preserve behavior."""
  # Example (future): SECURE_SSL_REDIRECT = True
  ```

### Phase 4: Verify No Changes Made

- [ ] **Do NOT change any of the following:**
  - [ ] `manage.py`, `wsgi.py`, `asgi.py`
  - [ ] `DJANGO_SETTINGS_MODULE` in env/CI
  - [ ] Any effective setting values in `base.py`
  - [ ] Import paths or module references

## Verification Checklist (Before & After Must Match)

### Pre-Refactor Baseline Capture

- [ ] **Hash the effective settings** (run this script and save output):
  ```bash
  python - <<'PY'
  import os, json, django
  os.environ.setdefault("DJANGO_SETTINGS_MODULE","<project_pkg>.settings")
  django.setup()
  from django.conf import settings
  items = []
  for k in dir(settings):
      if k.isupper():
          try:
              v = getattr(settings, k)
              items.append((k, repr(v)))
          except Exception as e:
              items.append((k, f"<ERR:{e.__class__.__name__}>"))
  print(hash(tuple(sorted(items))))
  PY
  ```
  **Baseline Hash:** `_____________` (record this number)

- [ ] **Django system check baseline:**
  ```bash
  python manage.py check
  ```
  **Output:** Record any warnings/errors

- [ ] **Test suite baseline:**
  ```bash
  uv run -m pytest -q
  ```
  **Results:** Record test count, passes/failures, duration

### Post-Refactor Verification

- [ ] **Settings hash verification:**
  - [ ] Run the same settings hash script
  - [ ] **Hash matches baseline:** ✅ / ❌
  - [ ] If different, **STOP** and rollback immediately

- [ ] **Django system check verification:**
  - [ ] Run `python manage.py check`
  - [ ] **Output identical to baseline:** ✅ / ❌
  - [ ] No new warnings or errors introduced

- [ ] **Test suite verification:**
  - [ ] Run `uv run -m pytest -q`
  - [ ] **Same test count:** ✅ / ❌
  - [ ] **Same pass/fail results:** ✅ / ❌
  - [ ] **Duration within reasonable variance:** ✅ / ❌

- [ ] **Smoke test (optional):**
  ```bash
  python manage.py runserver
  ```
  - [ ] **Server starts without new warnings/errors:** ✅ / ❌


## Git & PR Flow

### Commit Strategy (Two-Stage Approach)

#### Stage 1: File Move Only

- [ ] **Commit the file move:**
  ```bash
  git add -A
  git commit -m "refactor(settings): move single settings.py to settings/base.py"
  ```

#### Stage 2: Add Overlay Infrastructure

- [ ] **Commit the new overlay files:**
  ```bash
  git add <project_pkg>/settings/__init__.py <project_pkg>/settings/dev.py <project_pkg>/settings/test.py <project_pkg>/settings/prod.py
  git commit -m "refactor(settings): add overlay loader (__init__) and empty env stubs"
  ```

### Pull Request Template

```markdown
## Django Settings Refactor: Zero-Behavior-Change

**Objective:** Layer settings with zero behavior change

**Invariants Maintained:**
- ✅ No value changes
- ✅ Same DJANGO_SETTINGS_MODULE
- ✅ No new dependencies

**Verification Evidence:**
- **Settings hash:** Before: `_______` | After: `_______` ✅ MATCH
- **manage.py check:** ✅ UNCHANGED
- **pytest results:** ✅ UNCHANGED
- **runserver:** ✅ NO NEW WARNINGS

**Risk Level:** LOW (file moves + no-op overlays)

**Rollback Plan:** `git revert` the two commits
```

## Rollback Plan (If Anything Differs)

**IMPORTANT: If any verification fails, stop immediately and rollback**

### Immediate Rollback Steps

- [ ] **Stop and do not tweak values**
- [ ] **Choose rollback method:**
  
  **Option A - Revert commits:**
  ```bash
  git revert HEAD~1  # revert overlay commit
  git revert HEAD~1  # revert move commit
  ```
  
  **Option B - Hard reset:**
  ```bash
  git reset --hard HEAD~2  # if both commits need revert
  ```

### Post-Rollback Verification

- [ ] **Re-run tests:** `uv run -m pytest -q`
- [ ] **Re-run system check:** `python manage.py check`
- [ ] **Verify original state restored**

### Re-attempt Protocol

- [ ] **Re-attempt the refactor following steps exactly**
- [ ] **Do not edit values inside `base.py`**
- [ ] **Double-check each file creation step**

## Post-Merge Future Work (Do Not Change Now)

**These are commented examples for later, once you want intentional, explicit diffs.**

### Future Test Environment Optimizations (`test.py`)

```python
# PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
# EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
# CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
```

### Future Development Conveniences (`dev.py`)

```python
# DEBUG = True
# ALLOWED_HOSTS = ["*"]
# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE
```

### Future Production Hardening (`prod.py`)

```python
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 2592000
```

### Future Work Rules

- ✅ **Any future changes must be isolated to the correct overlay**
- ✅ **All changes must come with tests**
- ✅ **Each change should be a separate PR with clear justification**
- ✅ **Maintain environment variable configuration where possible**

## Common Pitfalls (Avoid These)

- ⛔ **Editing values when moving to `base.py`** (even reordering lists can bite)
- ⛔ **Changing `DJANGO_SETTINGS_MODULE`** or touching `manage.py`/`wsgi.py`/`asgi.py`
- ⛔ **Introducing new libraries** (`django-environ`, `pydantic-settings`) in this pass
- ⛔ **Adding defaults where none existed**
- ⛔ **Putting non-uppercase attributes into overlays** (loader only imports `UPPERCASE`)
- ⛔ **Changing import order or adding imports** during the file move
- ⛔ **Modifying comments or whitespace** that could affect behavior
- ⛔ **Testing with different environment variables** during verification

## Operator Runbook (Copy/Paste Commands)

### Before Refactor (Capture Baseline)

```bash
# System check
python manage.py check

# Test suite
uv run -m pytest -q

# Settings hash (save the output number)
python - <<'PY'
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","<project_pkg>.settings")
django.setup()
from django.conf import settings
items = []
for k in dir(settings):
    if k.isupper():
        try:
            v = getattr(settings, k)
            items.append((k, repr(v)))
        except Exception as e:
            items.append((k, f"<ERR:{e.__class__.__name__}>"))
print(hash(tuple(sorted(items))))
PY
```

### Perform Refactor

```bash
# Phase 1: Create settings package and move file
mkdir -p <project_pkg>/settings
git mv <project_pkg>/settings.py <project_pkg>/settings/base.py

# Create __init__.py (overlay loader)
cat > <project_pkg>/settings/__init__.py << 'EOF'
import os as _os
from .base import *  # noqa: F401,F403

_env = _os.getenv("DJANGO_ENV", "dev")
_mod = f"{__name__}.{_env}"

try:
    _m = __import__(_mod, fromlist=["*"])
except ModuleNotFoundError:
    _m = None

if _m:
    for _k in dir(_m):
        if _k.isupper():
            globals()[_k] = getattr(_m, _k)
EOF

# Create empty overlay files
echo '"""Development-only overrides. Intentionally empty to preserve behavior."""\n# Example (future): DEBUG = True' > <project_pkg>/settings/dev.py

echo '"""Pytest-only overrides. Intentionally empty to preserve behavior."""\n# Example (future): PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]' > <project_pkg>/settings/test.py

echo '"""Production-only hardening. Intentionally empty to preserve behavior."""\n# Example (future): SECURE_SSL_REDIRECT = True' > <project_pkg>/settings/prod.py

# Commit in two stages
git add -A && git commit -m "refactor(settings): move base settings"
git add <project_pkg>/settings/__init__.py <project_pkg>/settings/dev.py <project_pkg>/settings/test.py <project_pkg>/settings/prod.py
git commit -m "refactor(settings): add overlay loader and empty env stubs"
```

### After Refactor (Verify)

```bash
# System check (should be identical)
python manage.py check

# Test suite (should be identical)
uv run -m pytest -q

# Settings hash (should match baseline)
python - <<'PY'
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","<project_pkg>.settings")
django.setup()
from django.conf import settings
items = []
for k in dir(settings):
    if k.isupper():
        try:
            v = getattr(settings, k)
            items.append((k, repr(v)))
        except Exception as e:
            items.append((k, f"<ERR:{e.__class__.__name__}>"))
print(hash(tuple(sorted(items))))
PY
```

### If Verification Fails

```bash
# Emergency rollback
git reset --hard HEAD~2  # Remove both commits

# Or revert each commit
git revert HEAD~1  # Revert overlay commit
git revert HEAD~1  # Revert move commit

# Verify rollback worked
python manage.py check
uv run -m pytest -q
```

## Acceptance Criteria (Definition of Done)

### Technical Requirements

- [ ] **Repo builds and runs with no config changes**
- [ ] **Settings hash unchanged** (default env, no `DJANGO_ENV` set)
- [ ] **Tests & system checks unchanged** (same count, results, warnings)
- [ ] **Git diff shows only expected changes:**
  - [ ] File move: `settings.py` → `settings/base.py`
  - [ ] New overlay loader: `settings/__init__.py`
  - [ ] Empty overlay files: `dev.py`, `test.py`, `prod.py`

### Process Requirements

- [ ] **Two-commit strategy followed** (move, then overlays)
- [ ] **All verification steps completed** with documented evidence
- [ ] **PR includes verification hashes** (before/after comparison)
- [ ] **CI pipeline green** with no new failures

### Review Requirements

- [ ] **Code reviewers sign off** on zero-behavior-change evidence
- [ ] **QA team verifies** no functional regressions (if applicable)
- [ ] **Documentation updated** (if deployment guides reference settings.py)

---

**That's it.** This gives you a clean, future-proof settings structure while keeping your app behavior identical today. The layered approach enables future environment-specific customizations without breaking existing functionality.
