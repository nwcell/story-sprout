# Backend Structure Document

## Backend Architecture

Our backend is built using Django (version 5) following the Model-View-Controller (MVC) pattern. Key design elements:

*   **Django Framework**: Provides a clear separation between data models, business logic, and presentation. This makes it easy to update one part without breaking others.
*   **Service Layer**: All calls to external services (AI providers, payment gateways) are handled within their respective Django apps. This modular approach allows us to swap out providers like OpenAI, DALL·E, or Stripe by changing configuration within the relevant app, minimizing deep code changes.
*   **Asynchronous Tasks**

We use Celery to handle heavy-duty work in the background (story generation, image creation, moderation). Tasks are queued in Redis and run by worker processes, so our web server stays fast.

### Pydantic Preserializer for Celery

To ensure type safety and a seamless developer experience when working with Celery, we use a Pydantic preserializer from the `celery-typed` library, which is included as a local package. This allows us to pass Pydantic models directly to Celery tasks without manual serialization and deserialization.

**Key benefits:**

- **Type Safety:** Pydantic models are validated at runtime, reducing errors.
- **Developer Experience:** No need for boilerplate serialization code in our tasks.
- **Maintainability:** Keeps our task definitions clean and easy to read.

The preserializer is registered in the main Celery application file, making it available globally for all tasks.

*   **Real-Time Updates**: We use `django-eventstream` to provide Server-Sent Events (SSE), streaming progress updates back to the browser as each illustration or text segment completes.

How this supports our goals:

*   **Scalability**: Background workers can be scaled up independently of web servers. Redis and PostgreSQL are managed by DigitalOcean, so we can upgrade plans as traffic grows.
*   **Maintainability**: Clear folder structure (models, views, services) and a dedicated service layer mean new developers can jump in quickly.
*   **Performance**: Asynchronous tasks keep user requests snappy, and Server-Sent Events (SSE) provide live feedback instead of making customers wait on a spinning wheel.

## Database Management

For our database, we use SQLite for local development to ensure a simple setup, and DigitalOcean Managed PostgreSQL in production for robust, structured data storage. Redis is used for fast caching and as a task broker for Celery.

*   **Relational Data (PostgreSQL)**

    *   Users, teams, books, pages, characters, subscriptions, moderation settings, and version history.
    *   Enforces data integrity with foreign keys (e.g., a Page always belongs to one Book).
    *   Managed backups and high-availability provided by DigitalOcean.

*   **Caching & Task Queue (Redis)**

    *   Stores Celery task queues (job payloads, status).
    *   Caches AI prompt templates and style references for quick reuse (reducing repeated AI calls and cost).
    *   Manages SSE channel state for real-time updates.

*   **Object Storage (DigitalOcean Spaces)**

    *   Houses original images, style references, and generated PDFs.
    *   Lifecycle rule archives any files older than 90 days to keep costs low.

Data Access Patterns:

*   Synchronous reads/writes (user profiles, book drafts) go directly to PostgreSQL.
*   Heavy jobs (story generation, image creation) are handed off to Celery, which writes results back to PostgreSQL and Spaces.
*   Real-time progress is streamed via SSE to the frontend.

## Database Schema

The single source of truth for our database schema is the Django models defined within each app (e.g., `apps/stories/models.py`, `apps/accounts/models.py`). To understand the current data structure, relationships, and fields, developers should inspect these model files directly. This ensures that the understanding of the schema is always based on the live codebase, rather than potentially outdated documentation.

## API Design and Endpoints

We follow a RESTful pattern for core resources, plus Server-Sent Events (SSE) for live updates.

### API Endpoints and Live Documentation

Our API is built using **Django Ninja**, which automatically generates interactive documentation for all available endpoints. This ensures that the API documentation is always up-to-date with the codebase.

To explore the API, run the development server and navigate to:

- **`/api/docs`**

This will open a Swagger UI interface where you can see all the endpoints, their parameters, and even send test requests directly from your browser. The API is organized into logical groups (or "tags") such as `stories` and `ai` to make it easy to navigate.

### Server-Sent Events (SSE)

Our real-time updates are powered by `django-eventstream`, which uses Server-Sent Events (SSE) to push data from the server to the client. This is a lightweight and efficient alternative to WebSockets for one-way communication.

#### Implementation Details

- **Endpoint:** The primary SSE endpoint is `/events/`, managed by `django-eventstream`.
- **Channel Management:** A custom `ChannelManager` controls access to event channels. This ensures that users can only subscribe to channels they are authorized to view, such as:
    - `user-<id>`: For user-specific notifications.
    - `story-<story_uuid>`: For real-time updates related to a specific story.
- **Publishing Pattern:** The primary pattern for SSE is to use events as **triggers**, not as data transport. When a resource is updated on the server, a service function calls `send_event` with a specific event name and an empty payload. The frontend listens for this named event and then issues an HTMX `GET` request to the relevant API endpoint to fetch the updated content. This keeps the SSE traffic minimal and leverages HTMX for the actual UI updates.

This setup allows us to easily send real-time updates to the frontend, for everything from AI generation progress to notifications.


    
## Hosting Solutions

We host everything on DigitalOcean to keep costs under $50/month (excluding AI API fees) and avoid vendor lock-in.

*   **Droplet (2 vCPU, 4GB RAM)**

    *   Runs Docker Compose with containerized web and worker services.
    
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

    *   Routes HTTP/HTTPS traffic to the web container.

*   **Docker & Docker Compose**

    *   Defines web and worker (Celery) services in isolated containers. The web service runs Daphne to support SSE.

*   **Redis**

    *   Handles Celery job brokering and can be used by `django-eventstream` for multi-server setups.

*   **DigitalOcean Spaces CDN**

    *   Serves images and PDFs via a global CDN for fast load times.

*   **Stripe Webhooks**

    *   Securely notifies our backend about subscription events (renewals, cancellations).

*   **CI/CD Pipeline (GitHub Actions)**

    *   A CI/CD pipeline can be set up to run tests, build Docker images, and deploy to the droplet on push to the main branch.

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

    *   Tracks request latency, Celery queue length, active SSE connections, and resource usage.

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
