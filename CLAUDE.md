# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Story Sprout is a Django-based AI-powered storytelling platform that helps users create illustrated children's stories. It uses HTMX for interactive UI, Celery for async task processing, and integrates with AI services for content generation.

## Project Structure

```
story-sprout/
├── services/
│   ├── web/                 # Main Django application
│   │   ├── apps/            # Django apps
│   │   │   ├── accounts/    # User authentication
│   │   │   ├── ai/          # AI integration and task management
│   │   │   ├── common/      # Shared utilities and commands
│   │   │   ├── dashboard/   # User dashboard
│   │   │   ├── landing/     # Landing page
│   │   │   ├── stories/     # Story creation and management
│   │   │   └── subscriptions/ # Subscription management
│   │   ├── core/            # Django project settings and configuration
│   │   │   └── settings/    # Environment-specific settings (base, dev, prod, test)
│   │   ├── static/          # Static assets (CSS, JS, images)
│   │   ├── templates/       # HTML templates with HTMX and Alpine.js
│   │   └── manage.py        # Django management script
├── docs/                    # Project documentation
│   ├── architecture/        # System architecture docs
│   ├── brain/              # Development notes and TODOs
│   ├── development/        # Development guidelines
│   └── llms/               # LLM integration docs
└── scripts/                # Utility scripts
```

Note: The `pydantic-ai-stash` and `celery-typed` packages are referenced from `../_libs/` (outside this repository) as editable installs.

## Key Technologies

- **Backend:** Django 5.2+ with Django Ninja API framework
- **Frontend:** HTMX, Alpine.js, Tailwind CSS, Django Cotton components
- **Async:** Celery with Redis broker, Django EventStream for SSE
- **AI:** Pydantic AI, Google GenAI, LiteLLM
- **Database:** PostgreSQL (prod), SQLite (dev)
- **Package Manager:** uv (replaces pip/poetry)

## Development Commands

### Running the Application

```bash
# Start Django development server
make web
# or
uv run --project services/web python services/web/manage.py runserver

# Start Celery worker (required for AI tasks)
make tasks
# or
uv run --project services/web python services/web/manage.py runworker

# Start documentation server
make docs-server

# Start Jupyter Lab environment
make notebooks

```

### Database Management

```bash
# Create and apply migrations
make db-sync
# or individually:
make makemigrations
make migrate

# Run Django management commands
make manage <command>
# Example: make manage createsuperuser
```

### Testing and Code Quality

```bash
# Run tests
uv run -m pytest

# Run linting and formatting
uv run ruff check --fix
uv run ruff format

# Type checking (if configured)
uv run mypy services/web
```

### Environment Setup

```bash
# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install
```

## Architecture Patterns

### Django Apps Structure

Each app in `services/web/apps/` follows this pattern:
- `models.py` - Database models
- `views.py` - Django views (function or class-based)
- `api.py` - Django Ninja API endpoints
- `tasks.py` - Celery background tasks
- `services.py` - Business logic layer
- `signals.py` - Django signals
- `urls.py` - URL routing

### AI Integration Pattern

The AI app (`services/web/apps/ai/`) manages all AI interactions:
- Jobs are created as `Job` model instances
- Tasks are executed asynchronously via Celery
- Progress updates stream via SSE using Django EventStream
- Pydantic models ensure type safety across the pipeline

### Frontend Patterns

- **HTMX:** Used for dynamic content updates without full page reloads
- **Alpine.js:** Handles client-side interactivity
- **Django Cotton:** Component-based templating system
- **Tailwind CSS:** Utility-first styling

### Settings Management

Settings are split by environment:
- `core/settings/base.py` - Common settings
- `core/settings/dev.py` - Development overrides
- `core/settings/prod.py` - Production settings
- `core/settings/test.py` - Test configuration

Environment is selected via `DJANGO_ENV` variable (defaults to "dev").

## Important Conventions

### Code Style
- Python: Ruff for linting/formatting (line length: 119)
- Follow Google docstring convention
- Use type hints for function signatures
- Pydantic models for data validation

### Testing
- Tests located alongside app code in `tests.py` or `test_*.py`
- Use pytest with Django plugin
- Database is reused between test runs for speed (`--reuse-db`)

### Git Workflow
- Main branch: `main`
- Feature branches off main
- Pre-commit hooks run automatically (ruff, uv lock)

### Environment Variables
- Copy `.env.example` to `.env` for local development
- Required variables include API keys for AI services
- Never commit `.env` file

## Common Development Tasks

### Adding a New Django App
```bash
cd services/web
uv run python manage.py startapp <app_name> apps/<app_name>
```

### Creating a New Celery Task
1. Add task to `apps/<app>/tasks.py`
2. Use `@shared_task` decorator
3. Call with `.delay()` for async execution

### Adding API Endpoints
1. Create endpoints in `apps/<app>/api.py`
2. Register router in `core/api.py`
3. Use Pydantic schemas for request/response

### Working with HTMX
- Add `hx-*` attributes to trigger requests
- Return partial templates from views
- Use Cotton components for reusable UI elements

## Troubleshooting

### Redis Connection Issues
Ensure Redis is running: `redis-server`

### Celery Tasks Not Executing
1. Check worker is running: `make tasks`
2. Clear stale tasks: `redis-cli DEL celery`

### Migration Conflicts
```bash
uv run python services/web/manage.py migrate --merge
```

### Static Files Issues
```bash
uv run python services/web/manage.py collectstatic --noinput
```

## Task Management Best Practices

### Working with Task Lists and Checkboxes

When working on complex features or implementations, use the structured task management approach in the `docs/brain/` directory. This ensures organized, trackable progress.

#### Checkbox Status Indicators
- ✅ **Completed**: `- [x] Task description`
- ⏳ **In Progress**: `- [ ] Task description _**(⏳ In Progress)**_`
- 📋 **Pending**: `- [ ] Task description`
- 🔍 **Review Needed**: `- [ ] Task description _**(🔍 Review)**_`
- ⚠️ **Blocked**: `- [ ] Task description _**(⚠️ Blocked: reason)**_`
- 🧪 **Testing**: `- [ ] Task description _**(🧪 Testing)**_`

#### Implementation Guidelines
1. **Focus Limit**: Work on 3-5 tasks maximum at any time to maintain quality
2. **Status Updates**: Mark tasks as `_**(⏳ In Progress)**_` when starting work
3. **Sequential Completion**: Complete tasks fully before moving to next phase
4. **Nested Tasks**: Use indentation for subtasks and dependencies
5. **Review Process**: Add `_**(🔍 Review)**_` tag when task needs verification
6. **Specific References**: Include file paths and line numbers for clarity

#### Example Task Structure
```markdown
## Phase 1: Foundation
- [x] Configure basic setup
- [ ] Implement core functionality _**(⏳ In Progress)**_
  - [x] Add model definitions
  - [ ] Create API endpoints _**(🧪 Testing)**_
  - [ ] Add validation logic
- [ ] Integration testing _**(⚠️ Blocked: waiting for API completion)**_
```

#### Task Management Process
1. **Planning**: Break large features into phases with clear dependencies
2. **Execution**: Work sequentially through phases, completing all tasks before advancing
3. **Testing**: Each phase should include testing tasks
4. **Review**: Mark completed phases for review before proceeding
5. **Documentation**: Update task lists as work progresses

Use this approach for all significant development work to maintain organized, trackable progress and ensure nothing is missed during implementation.

## Context7 Integration

Always use context7 when I need code generation, setup or configuration steps, or library/API documentation. This means you should automatically use the Context7 MCP tools to resolve library id and get library docs without me having to explicitly ask.

Use context7 for:
- Code generation tasks requiring library/framework knowledge
- Setup and configuration steps for new tools or services
- API documentation and usage examples
- Library-specific implementation patterns
- Framework best practices and conventions

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
