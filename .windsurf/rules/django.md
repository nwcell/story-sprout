---
trigger: always_on
---

# Django Rules for Story Sprout Project

**Project:** Story Sprout - A Django-based storytelling platform  
**Location:** `/Users/travis/Projects/story-sprout`  
**Python Management:** All commands must use `uv` (never direct python/pip/django-admin)

---

## 1. Project Structure

### App Organization
- **Core:** Main project configuration in `core/`
- **Apps:** Individual Django apps in `apps/` directory
- **Templates:** Shared templates in `templates/` with app-specific subdirectories
- **Static Files:** CSS, JS, images managed via Django's static files system

### Key Files
- **Settings:** `core/settings.py`
- **Main URLs:** `core/urls.py`
- **Requirements:** Dependencies managed via `pyproject.toml` (uv)
- **Database:** SQLite for development (configurable for production)

---

## 2. Development Server Management

### Check if Server is Running
```bash
# Use the healthcheck endpoint to verify server status
curl -s http://localhost:8000/healthcheck/ | grep -q "healthy" && echo "Server is running" || echo "Server is not running"

# Alternative: Check if port 8000 is in use
lsof -i :8000
```

### Start Development Server
```bash
# Always start on default port 8000
uv run manage.py runserver

# Only use alternative port if explicitly needed
# uv run manage.py runserver 8001
```

### Stop Development Server
- Use `CTRL+C` in the terminal where server is running
- Or kill the process: `kill -9 $(lsof -t -i:8000)`

### Healthcheck Endpoint
- **URL:** `http://localhost:8000/healthcheck/`
- **Response:** `{"status": "healthy", "message": "Django server is running"}`
- **Use:** Programmatically check if server is running before starting new instances

---

## 3. Database & Migrations

### Migration Workflow
```bash
# 1. Create migrations after model changes
uv run manage.py makemigrations

# 2. Check migration plan (optional)
uv run manage.py showmigrations

# 3. Apply migrations
uv run manage.py migrate

# 4. Create specific app migration
uv run manage.py makemigrations stories
```

### Database Management
```bash
# Create superuser
uv run manage.py createsuperuser

# Access Django shell
uv run manage.py shell

# Database shell
uv run manage.py dbshell
```

---

## 4. Model Development

### Model Best Practices
- Use meaningful field names and help_text
- Add `__str__` methods to all models
- Use proper field types (CharField, TextField, etc.)
- Set appropriate `null` and `blank` options
- Use foreign keys for relationships

### Common Model Patterns
- **Timestamps:** `created_at`, `updated_at` with `auto_now_add` and `auto_now`
- **UUIDs:** For public-facing identifiers
- **User Relations:** Foreign keys to User model
- **Ordering:** Use Meta class `ordering` attribute

---

## 5. Admin Configuration

### Admin Best Practices
- Register all models in respective `admin.py` files
- Use `list_display` for better model overview
- Add `search_fields` and `list_filter` for large datasets
- Use inlines for related models
- Customize admin with `fieldsets` when needed

### Access Admin
```bash
# URL: http://localhost:8000/admin/
# Requires superuser account
# Create with: uv run manage.py createsuperuser
```

---

## 6. Dependencies & Package Management

### Package Management with UV
- All dependencies managed via `pyproject.toml`
- Lock file: `uv.lock` (committed to version control)
- Virtual environment: `.venv/` (auto-created by uv)

### Package Commands
```bash
# Add new package
uv add package-name

# Remove package
uv remove package-name

# Update lockfile
uv lock

# Sync environment
uv sync
```

---

## 7. Template Structure

### Template Organization
- **Base Templates:** In `templates/` root directory
- **App Templates:** In `templates/{app_name}/` subdirectories
- **Shared Components:** Reusable template fragments

### Template Best Practices
- Extend base templates consistently
- Use template inheritance effectively
- Keep template logic minimal
- Use proper template tags and filters
- Organize static files logically

---

## 8. URL Patterns

### URL Organization
- **Main URLs:** `core/urls.py` includes app URLs
- **App URLs:** Each app has its own `urls.py`
- **Healthcheck:** `/healthcheck/` for server status
- **Admin:** `/admin/` for Django admin
- **Static/Media:** Configured in settings for development

---

## 9. Common Development Tasks

### Model Changes
1. Edit model in `apps/{app}/models.py`
2. Run `uv run manage.py makemigrations`
3. Run `uv run manage.py migrate`
4. Update admin.py if needed
5. Test in Django admin

### View Development
1. Create/edit view in `apps/{app}/views.py`
2. Add URL pattern in `apps/{app}/urls.py`
3. Create template in `templates/{app}/`
4. Test functionality

### Static Files
```bash
# Collect static files (production)
uv run manage.py collectstatic

# Tailwind compilation (if needed)
uv run manage.py tailwind build
```

---

## 10. Testing & Debugging

### Run Tests
```bash
# All tests
uv run manage.py test

# Specific app
uv run manage.py test stories

# Specific test
uv run manage.py test stories.tests.TestStoryModel
```

### Debug Tools
- **Django Debug Toolbar** (if installed)
- **Print statements** in views/models
- **Django shell** for model testing
- **Admin interface** for data inspection

---

## 11. Known Issues & Warnings

### Django Allauth Deprecations
- Settings like `ACCOUNT_EMAIL_REQUIRED` are deprecated
- These don't break functionality but should be updated eventually
- Use new `ACCOUNT_SIGNUP_FIELDS` format when updating

### Port Management
- Always use default port 8000 unless explicitly needed otherwise
- Use healthcheck endpoint to verify server status before starting
- Only use alternative ports when necessary for specific testing scenarios

---

## 12. Best Practices for This Project

### Code Organization
- Keep models in respective app directories
- Use meaningful model field names
- Add `__str__` methods to all models
- Use proper foreign key relationships

### Database
- Always create migrations for model changes
- Use descriptive migration names when needed
- Test migrations on development data

### Templates
- Extend base templates consistently
- Use Tailwind classes for styling
- Keep template logic minimal
- Use proper template tags and filters

### Security
- Keep DEBUG=False in production
- Use environment variables for secrets
- Validate user input in forms
- Use Django's built-in authentication

---

## 13. Quick Reference Commands

```bash
# Start development
uv run manage.py runserver

# Database operations
uv run manage.py makemigrations
uv run manage.py migrate

# User management
uv run manage.py createsuperuser

# Testing
uv run manage.py test

# Shell access
uv run manage.py shell

# Package management
uv add package-name
uv remove package-name
uv sync
```

---

**Remember:** Always use `uv` for Python/Django commands in this project. Never use direct `python`, `pip`, or `django-admin` commands.