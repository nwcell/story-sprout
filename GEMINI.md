# GEMINI.md

This file provides instructional context about the Story Sprout project for Gemini.

## Project Overview

Story Sprout is a modern, AI-powered storytelling platform built with Django. It enables users to create illustrated stories with the help of generative AI. The architecture is designed to be scalable and maintainable, featuring a decoupled frontend and backend, asynchronous task processing, and real-time UI updates.

**Core Technologies:**

- **Backend**: Django 5.2+, Django Ninja, Celery
- **Frontend**: Django Templates with `django-cotton` for components, HTMX for dynamic server interactions, and Alpine.js for client-side interactivity.
- **Styling**: Tailwind CSS
- **Database**: PostgreSQL (production), SQLite (development)
- **Async & Real-time**: Redis (as a Celery broker) and `django-eventstream` (for Server-Sent Events).
- **AI Integration**: `pydantic-ai` for type-safe AI workflows, with LiteLLM for flexible model access.
- **Package Management**: `uv` is used for all Python dependency and environment management.

## Building and Running

This project uses a `Makefile` to simplify common development tasks.

### 1. Initial Setup

First-time setup requires syncing dependencies and preparing the database.

```bash
# Install all dependencies from uv.lock
uv sync

# Copy the example environment file (and fill in secrets)
cp .env.example .env

# Create and apply database migrations
make db

# Create a superuser for the admin panel
make manage createsuperuser
```

### 2. Running the Development Environment

The application requires two processes to run concurrently for full functionality.

- **Start the Django web server:**
  ```bash
  # Runs on http://localhost:8000
  make web
  ```

- **Start the Celery worker** (for AI tasks and other background jobs):
  ```bash
  # In a separate terminal
  make tasks
  ```

### 3. Running Tests

Execute the entire test suite using the Makefile target.

```bash
make test
```

## Development Conventions

- **Package Management**: All Python-related commands (`pip`, `python`, `django-admin`) **must** be run through `uv` (e.g., `uv run manage.py ...`). This is a strict project requirement.
- **Code Style**: Code is linted and formatted with `ruff`. Adherence to PEP 8, Google-style docstrings, and a line length of 119 characters is enforced. Run `uv run ruff check --fix && uv run ruff format` before committing.
- **Architecture**: The backend follows a service-oriented pattern, with business logic separated from views. The frontend is built with reusable `django-cotton` components, enhanced with HTMX for dynamic updates, avoiding large JavaScript frameworks.
- **Asynchronous Tasks**: Long-running or heavy tasks (especially AI generation) are handled by Celery workers. The UI is updated in real-time using Server-Sent Events (SSE) via the "Signal, Stream, Swap" pattern documented in `docs/architecture/ai_workflow_design.md`.
- **API**: The project uses `django-ninja` for its API, which provides automatic validation and documentation.
