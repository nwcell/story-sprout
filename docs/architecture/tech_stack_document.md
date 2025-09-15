# Tech Stack Document for StorySprout

This document explains, in everyday language, the technology choices behind StorySprout—a web platform where families co-create illustrated storybooks. You don’t need a technical background to understand why each tool was selected and how it helps deliver a safe, fast, and delightful experience.

## Frontend Technologies

These are the tools that run in your browser and shape what you see and interact with:

*   **Django Templates with Cotton Components**\
    Provides server-generated HTML pages with reusable component system for clean, maintainable templates.
*   **HTMX**\
    Lets the page update small parts (like new story text or images) without a full reload—this makes the real-time storytelling feel smooth.
*   **Tailwind CSS**\
    A utility-first styling toolkit that powers our clean, modern interface with minimal custom CSS.
*   **Alpine.js**\
    Handles client-side interactivity (menus, toggles, form handling) without pulling in a large JavaScript framework.
*   **Django Cotton**\
    Component-based templating system that allows building reusable UI components with slots and props, making templates more maintainable.

How these improve your experience:

*   Fast, incremental updates keep you engaged as story pages appear in real time.
*   Consistent styling ensures a friendly, pastel-colored interface that’s easy on the eyes.
*   Lightweight libraries mean quicker load times on both desktop and mobile.

## Backend Technologies

These power the behind-the-scenes work: storing your data, running AI, and generating images.

*   **Django 5.2**\
    A mature web framework that organizes code clearly, with built-in admin pages for quick setup.
*   **Django EventStream**\
    Enables Server-Sent Events (SSE) for real-time updates, streaming progress to your browser as AI generates content.
*   **Celery (in Docker containers)**\
    Manages background jobs—like calling AI models to write text or make images—so the web server stays responsive.
*   **PostgreSQL (Production) / SQLite (Development)**\
    A reliable database for storing users, stories, pages, and AI job tracking.
*   **Redis**\
    Acts as both a message broker for Celery and a real-time data store to power live progress updates.
*   **DigitalOcean Spaces**\
    S3-compatible storage for your generated images and PDFs, with automatic archiving of older files.
*   **WeasyPrint**\
    Turns the same HTML you saw in the browser into a high-quality, print-ready PDF at 300 dpi.

Together, these components:

*   Keep your data safe and consistent.
*   Let AI tasks run in the background while you continue planning or editing.
*   Store large image and PDF files efficiently.

## Infrastructure and Deployment

Here’s how everything is hosted, updated, and monitored:

*   **DigitalOcean Droplet**\
    A virtual server where all services run—chosen for its simplicity and low cost.
*   **Docker**\
    Containers wrap each service (web server, worker, database client) so they behave the same in development and production.
*   **GitHub Actions**\
    Automatically builds Docker images whenever code changes, then deploys them via SSH to DigitalOcean.
*   **Blue-Green Deployment**\
    Means new code is rolled out alongside existing code, then traffic switches over instantly—avoiding downtime.
*   **Managed Databases & Redis**\
    Handled by DigitalOcean so we don’t worry about backups or scaling up when you add more users.

Benefits:

*   Reliable 99.5% uptime with fast recovery.
*   Easy rollbacks if something goes wrong.
*   Clear version control and automated builds accelerate updates.

## Third-Party Integrations

We rely on specialized services to power AI, payments, and notifications:

*   **AI Integration**

    *   Pydantic AI framework for type-safe AI interactions
    *   Google GenAI and LiteLLM for model access
    *   Job-based workflow system for async AI processing
    *   All AI calls are wrapped in our own service layer, so we can switch providers easily.

*   **Stripe**\
    Manages subscription billing (free pages, 60-page premium plan, add-on pages, or unlimited option).

*   **Django-allauth**\
    Handles user signup, login, and social logins (Google/Apple) in a secure, standard way.

*   **SendGrid & Twilio**\
    Send email and optional SMS alerts when your book is finished or if a page needs your review.

*   **Sentry, Grafana Cloud & Healthcheck.io**\
    Monitor errors, track performance metrics, and ensure background jobs run on schedule.

These integrations give us mature, maintained services that scale with demand and keep costs predictable.

## Security and Performance Considerations

To protect families and keep the app snappy, we’ve built in multiple layers of safety and speed:

Security Measures:

*   **Authentication & Roles**\
    Parent-admins vs. child-creators, all managed by Django-allauth.
*   **Content Moderation**\
    OpenAI’s moderation APIs screen text and images for violence, profanity, sexual content, and self-harm.\
    Thresholds are stored per team in a simple JSON file, letting parents adjust safety levels.
*   **Retry & Fail-Safe**\
    Each page generation retries twice on failure; if it still fails, we skip that page, flag it for review, and continue so you’re never stuck.

Performance Optimizations:

*   **Streaming Updates**\
    Text appears immediately; images load as soon as they're ready through Server-Sent Events and HTMX swaps.
*   **Aggressive Caching**\
    Recently-generated images are cached; if costs rise on DALL·E, we switch to our local Stable Diffusion model automatically.
*   **Lightweight Frontend**\
    Minimal JavaScript and CSS frameworks keep page downloads small.

These steps ensure StorySprout stays responsive, safe, and cost-efficient even as usage grows.

## Development Tools & Environment

To build StorySprout quickly and maintain high code quality, developers use:

*   **Windsurf**\
    Modern IDE with AI coding assistance.
*   **Cursor**\
    Real-time AI suggestions while coding.
*   **Cline**\
    Open-source collaborative AI partner for team coding.
*   **GPT-3o, Grok 3 & Gemini 2.5 Pro**\
    Advanced language models for complex problem solving, prompt tuning, and documentation assistance.

These tools accelerate feature development, help catch issues early, and keep our codebase consistent.

## Conclusion and Overall Tech Stack Summary

StorySprout’s tech stack was chosen to meet a tight 14-day MVP launch, run cheaply on DigitalOcean, and avoid vendor lock-in, while delivering a magical experience for families:

*   We use **Django, Cotton components, HTMX, Tailwind, and Alpine.js** for a lightweight, fast frontend.
*   **Django EventStream, Celery, and Redis** power real-time AI generation and background jobs.
*   **DigitalOcean** hosts everything under budget, with managed databases and object storage.
*   **Pydantic AI, Google GenAI, and LiteLLM** deliver the storytelling magic, wrapped in a service layer for easy swapping.
*   **Stripe, SendGrid, Twilio** handle payments and notifications securely.
*   **Sentry, Grafana Cloud, Healthcheck.io** keep an eye on errors and performance.

This combination ensures parents and children get a seamless, safe, and enchanting co-creation experience today—and lays a solid foundation for future growth and features.
