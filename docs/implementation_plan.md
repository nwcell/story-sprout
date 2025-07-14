# Implementation plan

## Phase 1: Environment Setup

1.  Prevalidation: Check if **manage.py** exists in the current directory; if yes, abort initialization to avoid redundancy. [Project Overview]
2.  Install Python 3.11.4. [Tech Stack & Ops: Backend]
3.  **Validation:** Run `python3 --version` and confirm it prints **Python 3.11.4**. [Tech Stack & Ops: Backend]
4.  Install Node.js v20.2.1. [Tech Stack & Ops: Frontend]
5.  **Validation:** Run `node -v` and confirm it prints **v20.2.1**. [Tech Stack & Ops: Frontend]
6.  Install Docker Engine. [Tech Stack & Ops: Backend]
7.  **Validation:** Run `docker --version` and confirm Docker is available. [Tech Stack & Ops: Backend]
8.  Install Docker Compose. [Tech Stack & Ops: Backend]
9.  **Validation:** Run `docker-compose --version`. [Tech Stack & Ops: Backend]
10. Clone Pegasus scaffold into **storysprout** folder:

`git clone https://github.com/your-org/pegasus-scaffold.git storysprout cd storysprout`

[Tech Stack & Ops: Backend] 11. Copy environment template:

`cp .env.example .env`

Then update **.env** with DigitalOcean credentials. [Tech Stack & Ops: Deployment] 12. Create **cursor_metrics.md** in the project root and reference **cursor_project_rules.mdc** for metric guidelines. [Development Tools: Cursor] 13. If using **Cursor**:\
a. Create `.cursor/` directory in project root.\
b. Create an empty `.cursor/mcp.json` file.\
c. Add `.cursor/mcp.json` to `.gitignore`.\
[Development Tools: Cursor] 14. If using **Windsurf**:\
a. Open Cascade assistant.\
b. Tap hammer (MCP) icon → **Configure** → add `.cursor/mcp.json` settings if needed.\
[Development Tools: Windsurf]

## Phase 2: Frontend Development

1.  Install Tailwind CSS and Alpine.js:

`npm install tailwindcss@^3.3 autoprefixer alpinejs`

[Tech Stack & Ops: Frontend] 16. Initialize Tailwind:\
`bash npx tailwindcss init`\
Modify `tailwind.config.js` to set `content: ['./templates/**/*.html']`. [Tech Stack & Ops: Frontend] 17. Configure Django static files in **settings.py**: add to `STATICFILES_DIRS` → `os.path.join(BASE_DIR, 'static')`. [Tech Stack & Ops: Frontend] 18. Create `/templates/base.html` with Tailwind CDN link and Alpine.js script, reflecting pastel palette (#FFD2E0, #CFF6FF, #F9FAFB) and Inter fonts. [UX / Design Guidelines] 19. Create `/templates/character_builder.html` with form fields: name, look, personality, style dropdown, file upload. [Core Features: Character Builder] 20. **Validation:** Start Django server (`python manage.py runserver`) and open `http://localhost:8000/character-builder/`, verify form appears. [Core Features: Character Builder] 21. Create Plot Composer Wizard templates: `/templates/plot_wizard_step1.html` through `/templates/plot_wizard_step5.html`. [Core Features: Plot Composer Wizard] 22. Add HTMX attributes (`hx-post`, `hx-target`, `hx-swap`) to wizard navigation buttons, pointing to `/plot-wizard/step/{{step}}/`. [Core Features: Plot Composer Wizard] 23. **Validation:** Use the browser to navigate all 5 steps at `http://localhost:8000/plot-wizard/`, ensure HTMX swaps pages correctly. [Core Features: Plot Composer Wizard]

## Phase 3: Backend Development

1.  Install Python dependencies:

`pip install django==5.0 djangorestframework django-allauth celery[redis] channels psycopg2-binary weasyprint stripe sendgrid twilio django-redis`

[Tech Stack & Ops: Backend] 25. **Validation:** Run `pip freeze` and confirm installed versions match above. [Tech Stack & Ops: Backend] 26. In **settings.py**, add `channels` to `INSTALLED_APPS`; set `ASGI_APPLICATION='storysprout.asgi.application'`; configure `CHANNEL_LAYERS` to use Redis at `redis://localhost:6379/1`. [Tech Stack & Ops: Backend] 27. Provision DigitalOcean Managed Postgres 15.3 in `nyc1`; copy connection string into `.env` as `DATABASE_URL`. [Tech Stack & Ops: Database] 28. **Validation:** Run `python manage.py migrate` and ensure migrations complete without errors. [Tech Stack & Ops: Database] 29. Create `celery.py` in project root: configure broker as `redis://localhost:6379/0` and backend as same. [Tech Stack & Ops: Backend] 30. In `ai_providers/`, add modules:\

*   `openai.py` (for GPT-4o & moderation)\
*   `anthropic.py` (for Claude fallback)\
*   `sd_xl.py` (for self-hosted SD-XL + LoRA)\
    [Lock-In Mitigation] 31. Implement DRF endpoints in `/books/views.py`:\
*   `POST /api/books/` → create draft book\
*   `POST /api/books/<id>/generate/` → trigger Celery pipeline\
    Add throttle class limiting 5 active generations per team. [Core Features: API Endpoints] 32. **Validation:** Run\
    `bash curl -X POST http://localhost:8000/api/books/ -d '{}'`\
    Expect 201 with draft book JSON. [Core Features: API Endpoints] 33. Add WebSocket consumer in `/books/consumers.py` at route `/ws/progress/<book_id>/`; produce JSON `{page, status}` events. [Core Features: API Endpoints] 34. **Validation:** Use `wscat` or browser console to connect to `ws://localhost:8000/ws/progress/1/` and verify streaming events. [Core Features: API Endpoints] 35. Define Django models for `Team`, `User`, `Book`, `Page`, `Character`, `Embedding`, `ModerationLog` with appropriate fields and relations. [Tech Stack & Ops: Database] 36. **Validation:** Run `python manage.py makemigrations` and `migrate`. [Tech Stack & Ops: Database] 37. In `/books/tasks.py`, implement Celery tasks:\
*   `generate_story(task_id)` invoking GPT-4o via `ai_providers/openai.py`\
*   `generate_images(page_id)` invoking DALL·E 3 or `sd_xl.py`\
*   `moderate_text` & `moderate_images`\
    Add `@app.task(bind=True, max_retries=2, default_retry_delay=2)` for auto-retries. [Non-Functional Requirements] 38. **Validation:** Start Celery worker (`celery -A storysprout worker --loglevel=info`), trigger `generate_story.delay(1)`, verify retries and logging. [Non-Functional Requirements] 39. Integrate Stripe in **settings.py** with API keys; create subscription plans (3 free pages, metered overage). [Core Features: Family/Team Accounts] 40. Configure Django-allauth for email, Google, Apple in **settings.py** and add URLs in `/urls.py`. [Core Features: Family/Team Accounts] 41. Configure SendGrid email backend and Twilio SMS in **settings.py**; test with sample email and SMS send. [Core Features: Notifications]

## Phase 4: Integration

1.  Wire HTMX character-builder form to Django view at `/character-builder/submit/` returning JSON or HTML partial. [App Flow]
2.  Wire HTMX plot-wizard forms to corresponding Django views, persisting wizard state in session or draft Book model. [App Flow]
3.  In `/books/views.py`, on `POST /api/books/<id>/generate/` call `generate_story.delay()` then `generate_images.delay()` for each page. [App Flow]
4.  In `/templates/generation_progress.html`, use HTMX `hx-sse` to subscribe to `/ws/progress/{{book.id}}/` and swap progress indicators. [App Flow]
5.  **Validation:** Perform end-to-end in browser: sign up → create character → compose plot → trigger generation → watch flipbook reader at `/books/{{id}}/reader/`. [Testing & QA]

## Phase 5: Deployment

1.  Create GitHub Actions workflow at `.github/workflows/deploy.yml` that:

    1.  Checks out code
    2.  Builds Docker image tagged `registry.digitalocean.com/your-registry/storysprout:$GITHUB_SHA`
    3.  Pushes image
    4.  SSH into DO droplet and performs blue-green swap\
        [CI/CD]

2.  Provision DigitalOcean resources in `nyc1`:

    *   Managed Postgres 15.3
    *   Redis Droplet (vapor stack)
    *   Spaces bucket `storysprout-assets`
    *   App Droplet (2 vCPU, 4GB RAM)\
        [Tech Stack & Ops: Deployment]

3.  Add `/healthz` endpoint in Django; configure Healthcheck.io to call every 5 minutes. [Observability]

4.  **Validation:** Run Locust with 25 concurrent users against `/api/books/…/generate/` and verify full 12-page book completes under 30 seconds while success rate ≥ 98%. [Testing & QA]
