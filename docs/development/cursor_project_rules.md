## Project Overview

*   **Type:** cursor_project_rules
*   **Description:** I want to build a web-based platform for **parents and children** to **co-create fully-illustrated storybooks**. Families define characters and a rough plot; the system uses AI to craft a consistent narrative plus matching images, shows pages appear in real-time, then offers a print-ready PDF. MVP must launch ≤ 14 days, run cheaply on DigitalOcean, and avoid vendor lock-in.
*   **Primary Goal:** Build and launch an MVP of StorySprout in 14 days on a DigitalOcean droplet, maintain infra costs ≤ $50/mo (excl. AI usage), 99.5% uptime, and preserve vendor portability.

## Project Structure

### Framework-Specific Routing

*   **Directory Rules:**

    *   `django_5/`: Standard Django 5 project layout with `project_name/urls.py` as root router; each app has its own `app_name/urls.py` included via `path('app_name/', include('app_name.urls'))`.

*   Example 1: Accounts → `accounts/urls.py` mapping `path('signup/', SignupView.as_view())`.

*   Example 2: Books → `books/urls.py` mapping REST API endpoints under `/api/books/`.

*   Example 3: WebSocket → In `project_name/asgi.py`, route `ws/progress/<book_id>/` to `ProgressConsumer`.

### Core Directories

*   **Versioned Structure:**

    *   `apps/`: Django apps (accounts, books, characters, prompts, notifications, moderation).
    *   `templates/`: Django template overrides; namespaced per app at `templates/<app_name>/*.html`.
    *   `static/`: Tailwind-generated CSS and JS asset bundles.
    *   `prompts/`: `story.md`, `image.txt`, `lora_tune.yaml` for AI prompt templates.
    *   `ai_providers/`: Abstraction layer wrapping OpenAI, Anthropic, self-hosted SD-XL.
    *   `docker/`: Dockerfiles and compose definitions (Compose v2 format).

### Key Files

*   **Stack-Versioned Patterns:**

    *   `project_name/settings.py`: Django 5 settings with `INSTALLED_APPS`, Channels, Celery broker settings, DigitalOcean Spaces storage backend.
    *   `project_name/asgi.py`: Configure Channels v4 with Redis layer for WebSocket routing at `ws/progress/<book_id>/`.
    *   `docker-compose.yml`: Docker Compose v2; services: web (Gunicorn), worker (Celery), redis, postgres.
    *   `.github/workflows/ci.yml`: GitHub Actions using Docker build → SSH deploy; blue-green deployment via Docker Compose.
    *   `templates/base.html`: Django template inheritance with Tailwind CSS JIT.

## Tech Stack Rules

*   **Version Enforcement:**

    *   `django@5`: Use path-based routing, class-based views, no legacy `url()`.
    *   `htmx@1.*`: Favor `hx-get`, `hx-post`, and OOB swaps (`hx-swap-oob`) for real-time updates.
    *   `tailwindcss@3`: Enable JIT mode; purge unused classes from `templates/` and `static/js/`.
    *   `django_channels@4`: Use ASGI and channel layers with Redis; no polling fallbacks.
    *   `celery@5`: Organize tasks in `tasks/` modules; enforce idempotency.
    *   `docker-compose@2`: All services defined in `docker-compose.yml`; no legacy `docker-compose.yml` v1 syntax.

## PRD Compliance

*   "Launch an MVP in 14 days on DigitalOcean": Enforce rapid scaffolding with Pegasus starter; restrict scope to MVP features.
*   "Monthly cloud bill target ≤ $50 excluding AI usage": Use Managed Postgres and Redis on smallest plans; DigitalOcean Spaces with lifecycle rules.
*   "Avoid vendor lock-in": All third-party calls through `ai_providers/` service layer; configurable via environment variables.

## App Flow Integration

*   **Onboarding Flow:** `accounts/urls.py` → `SignupView` → team creation → redirect to `characters:create`.
*   **Story Generation Flow:** `POST /api/books/<id>/generate/` enqueues Celery `generate_story` then `generate_images`; progress streamed via Channels on `ws/progress/<id>/`.
*   **Flipbook Reader:** Static route `flipbook/<book_id>/` served by `books.views.FlipbookView` using StPageFlip JS.
*   **PDF Export:** `GET /api/books/<id>/export_pdf/` triggers WeasyPrint task; file saved to Spaces and emailed via SendGrid.

## Best Practices

*   django_5

    *   Split code into reusable apps.
    *   Use class-based views and Django REST framework where appropriate.
    *   Keep `settings.py` modular with environment overrides.

*   django_templates

    *   Employ template inheritance; avoid inline CSS/JS.
    *   Escape user content by default; use `|safe` sparingly.

*   htmx

    *   Use `hx-trigger` and `hx-swap-oob` for clean partial updates.
    *   Return fragments of HTML only; avoid full-page renders in HTMX endpoints.

*   tailwind_css

    *   Configure `tailwind.config.js` to purge `templates/` and `static/`.
    *   Use utility-first classes; avoid custom CSS unless necessary.

*   django_channels

    *   Name channel groups by `book_{id}`; clean up on disconnect.

*   celery

    *   Use retries with exponential backoff; limit to two retries.
    *   Keep tasks small and idempotent.

*   docker

    *   Base images on official Python 3.11-slim; multi-stage builds.
    *   Pin versions of dependencies in `requirements.txt`.

*   postgres

    *   Enable `pgcrypto` extension for UUIDs.
    *   Enforce connection pooling and SSL.

*   redis

    *   Set `maxmemory-policy` to `allkeys-lru` in production.

*   digitalocean_spaces

    *   Use versioned buckets; apply lifecycle rule to archive >90 days.

*   django_allauth

    *   Configure strict email verification and social login scopes to minimal data.

*   stripe

    *   Use webhooks for subscription events; verify signatures.

*   github_actions

    *   Run `pytest` and `cypress` in CI; fail early on lint errors.

*   sentry

    *   Initialize in `settings.py`; filter out known warnings.

*   grafana_cloud

    *   Expose Prometheus metrics at `/metrics`; instrument Celery and Django.

*   healthcheck_io

    *   Register Celery beat, web, and worker endpoints; alert on missed heartbeats.

*   openai_gpt_4o

    *   Wrap API calls with timeouts and retries; log request/response for debugging.

*   anthropic_claude_3_7_sonnet

    *   Use as fallback only; maintain separate prompt templates.

*   dalle_3

    *   Fix seed per page for reproducibility; store seed in Page model.

*   stable_diffusion_xl + lora_fine_tune

    *   Host on GPU instance; expose local endpoint; toggle via admin setting.

*   stpageflip_js

    *   Lazy-load on reader entry; prefetch first two pages.

*   weasyprint

    *   Render same HTML as flipbook; reuse templates to avoid drift.

*   sendgrid

    *   Use transactional templates; verify webhook events.

*   twilio

    *   Throttle SMS to avoid overage.

*   windsurf, cursor, cline, gpt_o3, grok_3, gemini_2_5

    *   Use as IDE embellishments only; never commit AI-generated code without review.

## Rules

*   Derive folder/file patterns **directly** from `techStackDoc` versions.
*   If Django 5: enforce MVT structure with `apps/`, `templates/`, `static/`.
*   If HTMX present: all dynamic updates use `hx-` attributes; no full-page reloads for streaming.
*   If Channels v4: WebSocket consumers must live in `apps/` with explicit routing in `asgi.py`.
*   Never mix legacy routing patterns (e.g., no `urls.py` in project root only).

## Rules Metrics

Before starting the project development, create a metrics file in the root of the project called

`cursor_metrics.md`

### Instructions:

*   Each time a cursor rule is used as context, update `cursor_metrics.md`.
*   Use the following format for `cursor_metrics.md`:

`# Rules Metrics ## Usage The number of times rules is used as context * rule-name.mdc: 5 * another-rule.mdc: 2 * ...other rules`
