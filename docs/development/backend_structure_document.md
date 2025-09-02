# Backend Structure Document

## Backend Architecture

Our backend is built using Django (version 5) following the Model-View-Controller (MVC) pattern. Key design elements:

*   **Django Framework**: Provides a clear separation between data models, business logic, and presentation. This makes it easy to update one part without breaking others.
*   **Service Layer**: All calls to external services (AI providers, payment gateways) go through a dedicated folder (`ai_providers/`). This abstraction means we can swap out OpenAI, DALL·E, Stripe, or any other service just by changing configuration—no deep code changes needed.
*   **Asynchronous Tasks**: We use Celery to handle heavy-duty work in the background (story generation, image creation, moderation). Tasks are queued in Redis and run by worker processes, so our web server stays fast.
*   **Real-Time Updates**: Django Channels powers WebSocket connections, streaming progress updates back to the browser as each illustration or text segment completes.

How this supports our goals:

*   **Scalability**: Background workers can be scaled up independently of web servers. Redis and PostgreSQL are managed by DigitalOcean, so we can upgrade plans as traffic grows.
*   **Maintainability**: Clear folder structure (models, views, services) and a dedicated service layer mean new developers can jump in quickly.
*   **Performance**: Asynchronous tasks keep user requests snappy, and WebSockets provide live feedback instead of making customers wait on a spinning wheel.

## Database Management

We use DigitalOcean Managed PostgreSQL for structured data and Redis for fast caching and task brokering.

*   **Relational Data (PostgreSQL)**

    *   Users, teams, books, pages, characters, subscriptions, moderation settings, and version history.
    *   Enforces data integrity with foreign keys (e.g., a Page always belongs to one Book).
    *   Managed backups and high-availability provided by DigitalOcean.

*   **Caching & Task Queue (Redis)**

    *   Stores Celery task queues (job payloads, status).
    *   Caches AI prompt templates and style references for quick reuse (reducing repeated AI calls and cost).
    *   Manages WebSocket session state for real-time updates.

*   **Object Storage (DigitalOcean Spaces)**

    *   Houses original images, style references, and generated PDFs.
    *   Lifecycle rule archives any files older than 90 days to keep costs low.

Data Access Patterns:

*   Synchronous reads/writes (user profiles, book drafts) go directly to PostgreSQL.
*   Heavy jobs (story generation, image creation) are handed off to Celery, which writes results back to PostgreSQL and Spaces.
*   Real-time progress streamed from Redis through Channels to the frontend.

## Database Schema

Below is an overview of our main tables. All tables use standard integer primary keys and timestamps for created/updated fields.

1.  **users**

    *   id, email, password_hash, full_name, role (parent or child), date_joined

2.  **teams**

    *   id, name, owner_user_id
    *   owner_user_id → users.id (1 parent-admin per team)

3.  **team_members**

    *   id, team_id, user_id, role_in_team (parent-admin or child-creator)
    *   team_id → teams.id, user_id → users.id

4.  **books**

    *   id, team_id, title, status (draft, generating, complete), created_at, updated_at, soft_deleted_until
    *   team_id → teams.id

5.  **pages**

    *   id, book_id, order_index, text_content, image_url, generate_status, seed_value
    *   book_id → books.id

6.  **characters**

    *   id, name, traits_json, style_ref_id, embedding_vector

7.  **book_characters** (many-to-many)

    *   book_id → books.id, character_id → characters.id

8.  **subscriptions**

    *   id, team_id, stripe_subscription_id, plan_name, status, next_billing_date

9.  **moderation_settings**

    *   id, team_id, thresholds_json

10. **tokens** (for social auth)

    *   id, user_id, provider, access_token, refresh_token, expires_at

Example SQL snippet for `books` and `pages` tables:

`CREATE TABLE books ( id SERIAL PRIMARY KEY, team_id INTEGER REFERENCES teams(id), title VARCHAR(255) NOT NULL, status VARCHAR(20) NOT NULL DEFAULT 'draft', created_at TIMESTAMP NOT NULL DEFAULT NOW(), updated_at TIMESTAMP NOT NULL DEFAULT NOW(), soft_deleted_until TIMESTAMP NULL ); CREATE TABLE pages ( id SERIAL PRIMARY KEY, book_id INTEGER REFERENCES books(id) ON DELETE CASCADE, order_index SMALLINT NOT NULL, text_content TEXT, image_url VARCHAR(512), generate_status VARCHAR(20) NOT NULL DEFAULT 'pending', seed_value BIGINT );`

## API Design and Endpoints

We follow a RESTful pattern for core resources, plus WebSockets for live updates.

### REST Endpoints

*   **POST /api/books/**

    *   Create a new book draft. Returns the book ID and initial page stubs.

*   **POST /api/books/{id}/generate/**

    *   Kick off the story + image pipeline for a specific book.
    *   Enforces rate limit: max 5 active generations per team.

*   **GET /api/books/{id}/**

    *   Fetch book details, page texts, image URLs, and status of each page.

*   **PATCH /api/books/{id}/**

    *   Update editable fields (title, page text edits, moderation thresholds).

*   **POST /api/teams/{id}/subscriptions/**

    *   Create or update Stripe subscription for team billing.

*   **POST /api/characters/**

    *   Define a new character (name, traits, uploaded style image). Returns style_ref_id.

*   **GET /api/characters/**

    *   List saved characters for a team.

### WebSocket Endpoint

*   **/ws/progress/{book_id}/**

    *   Streams JSON messages as each page completes:

    `{ "page": 3, "status": "done" }`

    *   Frontend uses HTMX to swap in images/text immediately.

## Hosting Solutions

We host everything on DigitalOcean to keep costs under $50/month (excluding AI API fees) and avoid vendor lock-in.

*   **Droplet (2 vCPU, 4GB RAM)**

    *   Runs Docker Compose with web, worker, and Channels services.
    *   Blue-green deployment via GitHub Actions and SSH, ensuring zero downtime.

*   **Managed PostgreSQL**

    *   Automatic backups, daily maintenance, and easy resizing.

*   **Managed Redis**

    *   High availability for Celery queues and channel layers.

*   **Spaces (S3-compatible)**

    *   Stores all images and PDFs. Lifecycle policy archives older files automatically.

Benefits:

*   **Reliability**: Managed databases and caches handle failover.
*   **Scalability**: Easy to upgrade droplet size or add load balancers.
*   **Cost-Effectiveness**: Clear monthly billing under $50 for infrastructure.

## Infrastructure Components

*   **Load Balancer**

    *   Routes HTTP/HTTPS traffic across web containers in a blue-green setup.

*   **Docker & Docker Compose**

    *   Defines web, worker (Celery), and Channels services in isolated containers.

*   **Redis**

    *   Handles Celery job brokering and real-time channel layers for WebSockets.

*   **DigitalOcean Spaces CDN**

    *   Serves images and PDFs via a global CDN for fast load times.

*   **Stripe Webhooks**

    *   Securely notifies our backend about subscription events (renewals, cancellations).

*   **CI/CD Pipeline (GitHub Actions)**

    *   On push to main: run tests, build Docker images, and deploy to droplet.

## Security Measures

*   **Authentication & Authorization**

    *   Django-allauth manages email/password and social login (Google, Apple).
    *   Session-based auth with secure cookies (HTTP-only, same-site).
    *   Role checks ensure only parent-admins can change billing or moderation settings.

*   **Encryption**

    *   TLS everywhere: HTTPS for web traffic and secure connections to PostgreSQL/Redis.
    *   Spaces buckets use server-side encryption at rest.

*   **Rate Limiting**

    *   IP- and user-based throttling on generation endpoints to prevent abuse.

*   **Environment Variables**

    *   Secrets (API keys, DB credentials) never live in code—managed via `.env` and Docker secrets.

*   **Content Moderation**

    *   Text and images go through OpenAI moderation. Teams can adjust thresholds via a JSON config.

*   **Vendor-Lock Mitigation**

    *   All external services abstracted behind a service layer. Swap DALL·E for self-hosted SD-XL by flipping an env var.

## Monitoring and Maintenance

*   **Error Tracking (Sentry)**

    *   Captures exceptions with context (user, environment) and alerts on new issues.

*   **Metrics & Dashboards (Grafana Cloud + Prometheus)**

    *   Tracks request latency, Celery queue length, WebSocket connections, and resource usage.

*   **Health Checks (Healthcheck.io)**

    *   Pings Celery Beat and critical cron-like tasks to ensure job scheduling is happening.

*   **Automated Testing**

    *   Pytest (unit tests, 90%+ coverage on generation pipeline).
    *   Cypress for end-to-end flows: account setup, book generation, payments.
    *   Locust for load testing concurrent generations.

*   **Maintenance Windows**

    *   Scheduled during off-peak (night hours) with advance notice; CI/CD pipeline ensures rollback capability.

## Conclusion and Overall Backend Summary

StorySprout’s backend is a modern, maintainable Django application designed for fast growth and low cost. By using managed services on DigitalOcean, containerized deployment, and a clear service layer, we achieve:

*   Real-time user feedback during book creation
*   Cost-efficient AI integration with fallback options
*   Easy scaling to 1,000+ paying customers
*   High reliability (99.5% uptime) and strong security

This setup aligns with our 14-day MVP goal, tight budget, and the need to avoid vendor lock-in, while providing a robust foundation for future features.
