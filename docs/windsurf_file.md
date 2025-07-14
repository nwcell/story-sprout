# .windsurfrules

## Project Overview

*   **Type:** Web Application (Django-based SaaS)
*   **Description:** StorySprout is a web-based platform for families to co-create fully illustrated storybooks using AI.
*   **Primary Goal:** Enable collaborative narrative and image generation with real-time page updates and exportable print-ready PDFs.

## Project Structure

### Framework-Specific Routing

*   **Directory Rules:**

    *   Django 5: Use `project/urls.py` for global routes and each app’s `apps/<app_name>/urls.py` for app-specific paths.
    *   HTMX Endpoints: Prefix AJAX routes under each app, e.g., `character_builder/hx/create/` serving partials.
    *   WebSocket Routing: Define ASGI routes in `project/asgi.py` for Channels at `ws/generation/<job_id>/`.

### Core Directories

*   **Versioned Structure:**

    *   `apps/character_builder`: Django app for character creation and reference image handling.
    *   `apps/plot_composer`: Django app implementing the 5-step plot wizard.
    *   `apps/story_generation`: Django app for Celery tasks driving text/image AI pipelines.
    *   `apps/flipbook`: Django app integrating the StPageFlip JS reader.
    *   `apps/pdf_export`: Django app for WeasyPrint PDF rendering utilities.
    *   `ai_providers/`: Service layer for swapping AI providers via environment variables.
    *   `prompts/`: Markdown templates for AI prompts (e.g., `story.md`).
    *   `static/`: Tailwind CSS and Alpine.js assets via Pegasus starter.
    *   `templates/`: Django templates with HTMX snippets and ARIA-compliant markup.

### Key Files

*   **Stack-Versioned Patterns:**

    *   `manage.py`: Django 5 CLI entrypoint.
    *   `project/settings.py`: Pegasus starter settings, allauth, Celery, Redis, Spaces config.
    *   `project/urls.py`: Root URL config including each app’s namespace.
    *   `apps/story_generation/tasks.py`: Celery tasks with auto-retry and error-handling logic.
    *   `prompts/story.md`: GPT-4o prompt template for narrative generation.
    *   `apps/pdf_export/utils.py`: WeasyPrint helpers for CMYK, 300 dpi PDF output.
    *   `docker-compose.yml`: Defines services: web (Django), celery, Redis, db, and DO Spaces proxy.

## Tech Stack Rules

*   **Version Enforcement:**

    *   django@5: Enforce ASGI with Channels; no legacy full-page reloads for async flows.
    *   celery@5: All tasks scoped under `apps/*/tasks.py`; global retry policy applied.
    *   redis@latest: Only used as broker and channel layer; avoid direct caching uses.
    *   tailwindcss@latest: All styles compiled via `static/css/tailwind.css`; no inline styles.
    *   htmx@1.9: All dynamic interactions must use HTMX attributes; no custom AJAX.

## PRD Compliance

*   **Non-Negotiable:**

    *   "≤ 30 s perceived wait for full 12-page book (background ok; real-time stream preferred)": Stream progress via Django Channels and HTMX swaps.
    *   "WCAG AA contrast minimum; flipbook navigable by keyboard & screen reader": Ensure ARIA labels, alt text, and keyboard handlers.
    *   "Soft-deleted books retained 90 days, then auto-purged": Implement `deleted_at` timestamp and daily Celery purge job.
    *   "All third-party calls wrapped in service layer (`ai_providers/`)": Disallow direct API calls outside this module.

## App Flow Integration

*   **Stack-Aligned Flow:**

    *   Character Builder → `apps/character_builder/views.py` with HTMX partials in `templates/character_builder/partials/`.
    *   Plot Composer Wizard → `apps/plot_composer/views.py` multi-step endpoints at `plot_composer/step/<int:step>/`.
    *   Story Generation Pipeline → Celery tasks in `apps/story_generation/tasks.py` and WS at `ws/generation/<job_id>/`.
    *   Flipbook Reader → Template `templates/flipbook/index.html` served at `flipbook/<book_id>/`.
    *   PDF Export → View `export/pdf/<book_id>/` in `apps/pdf_export/views.py` invoking WeasyPrint.

### Input Context (Priority Order):

1.  techStackDoc (exact versions + routing patterns)
2.  prd (version-dependent requirements)
3.  appFlow (route-to-component mapping)
4.  answers (e.g., "We chose App Router for RSCs")

### Rules:

*   Derive folder/file patterns directly from techStackDoc versions.
*   If Next.js 14 App Router: Enforce `app/` directory with nested route folders.
*   If Pages Router: Use `pages/*.tsx` flat structure.
*   Mirror this logic for React Router, SvelteKit, etc.
*   Never mix version patterns (e.g., no `pages/` in App Router projects).
