# AGENTS.md

This file provides guidance to AI coding agents for working with the Story Sprout repository.

## 1. Project Overview

Story Sprout is a Django-based AI-powered storytelling platform that helps users create illustrated children's stories. It uses HTMX for a dynamic UI, Celery for asynchronous task processing, and `pydantic-ai` for integrating generative AI services.

### 1.1. Key Technologies

- **Backend**: Django 5.2+, Django Ninja, Celery
- **Frontend**: Django Templates, `django-cotton` components, HTMX, Alpine.js, Tailwind CSS
- **Database**: PostgreSQL (production), SQLite (development)
- **Async**: Redis (Celery broker), `django-eventstream` (SSE)
- **AI**: `pydantic-ai`, Google GenAI, LiteLLM
- **Package Management**: `uv`

### 1.2. Project Structure

```
story-sprout/
├── src/
│   ├── apps/            # Django apps (stories, ai, accounts, etc.)
│   ├── config/          # Django project settings and configuration
│   ├── static/          # Static assets (CSS, JS, images)
│   └── templates/       # HTML templates with HTMX and Alpine.js
├── docs/                # Project documentation
├── scripts/             # Utility scripts
├── Makefile             # Helper commands for common tasks
├── manage.py            # Django management script
├── pyproject.toml       # Python dependency definitions
└── uv.lock              # Pinned Python dependency versions
```
*Note: Some local library packages like `pydantic-ai-stash` are referenced from outside this repository as editable installs.*

## 2. Environment Setup

1.  **Install `uv`**: If not already installed, run:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
2.  **Create a virtual environment**:
    ```bash
    uv venv
    ```
3.  **Install dependencies**:
    ```bash
    uv sync
    ```
4.  **Setup pre-commit hooks**:
    ```bash
    uv run pre-commit install
    ```
5.  **Setup local environment file**:
    ```bash
    cp .env.example .env
    ```
    *You must fill in the required API keys in `.env` for AI features to work.*

6.  **Apply database migrations**:
    ```bash
    uv run manage.py migrate
    ```

## 3. Development Workflow

### 3.1. Running the Application

This project uses a `Makefile` for convenience.

- **Start the web server**:
  ```bash
  make web
  ```
  *The server will be available at http://localhost:8000.*

- **Start the Celery worker** (required for all AI tasks):
  ```bash
  make tasks
  ```

### 3.2. Common Commands

**CRITICAL**: All Python and Django commands **must** be run using `uv`. Do not use `python` or `pip` directly.

- **Run management commands**:
  ```bash
  # General syntax
  uv run manage.py <command>
  # Example
  uv run manage.py createsuperuser
  ```
- **Run tests**:
  ```bash
  uv run -m pytest
  ```
- **Linting and Formatting**:
  ```bash
  # Check for issues and auto-fix where possible
  uv run ruff check --fix

  # Format code
  uv run ruff format
  ```
- **Database Migrations**:
  ```bash
  # Create new migration files after changing models
  uv run manage.py makemigrations

  # Apply migrations to the database
  uv run manage.py migrate
  ```

### 3.3. Core Architectural Patterns

- **Backend**: Logic is organized into Django apps. Complex business logic should be in `services.py` files. API endpoints are built with Django Ninja in `api.py`.
- **Frontend**: The UI is built with Django templates and `django-cotton` components. Interactivity is added via HTMX for server communication and Alpine.js for client-side behaviors. Follow the patterns in `docs/development/htmx_patterns.md`.
- **AI Agents**: Agent execution is handled asynchronously by Celery. Agents interact with the application via a secure API layer, not by accessing the database directly. Refer to `docs/architecture/ai_workflow_design.md` for the "Signal, Stream, Swap" pattern.

## 4. Task Management

When working on complex features, use a structured task list with status indicators to track progress.

- ✅ **Completed**: `- [x] Task description`
- ⏳ **In Progress**: `- [ ] Task description _**(⏳ In Progress)**_`
- 📋 **Pending**: `- [ ] Task description`
- 🔍 **Review Needed**: `- [ ] Task description _**(🔍 Review)**_`
- ⚠️ **Blocked**: `- [ ] Task description _**(⚠️ Blocked: reason)**_`
- 🧪 **Testing**: `- [ ] Task description _**(🧪 Testing)**_`

Work on a small number of tasks at a time (3-5) and complete them fully before moving on.

## 5. Troubleshooting

- **Redis Connection Issues**: Ensure the Redis server is running. You can start it with `redis-server`.
- **Celery Tasks Not Executing**:
  1.  Confirm the worker is running (`make tasks`).
  2.  Check the worker logs for errors.
  3.  You can clear stale tasks from the queue with `redis-cli DEL celery`.
- **Migration Conflicts**: If you encounter migration conflicts, you may need to resolve them manually or use `uv run manage.py migrate --merge`.