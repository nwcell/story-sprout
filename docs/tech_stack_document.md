# Tech Stack Document for StorySprout

This document explains, in everyday language, the technology choices behind StorySprout—a web platform where families co-create illustrated storybooks. You don’t need a technical background to understand why each tool was selected and how it helps deliver a safe, fast, and delightful experience.

## Frontend Technologies

These are the tools that run in your browser and shape what you see and interact with:

*   **Django Templates**\
    Provides server-generated HTML pages, keeping the interface simple and fast to develop.
*   **HTMX**\
    Lets the page update small parts (like new story text or images) without a full reload—this makes the real-time storytelling feel smooth.
*   **Tailwind CSS**\
    A utility-first styling toolkit that powers our pastel-themed look (rounded cards, drop shadows) with minimal custom CSS.
*   **Alpine.js**\
    Handles tiny bits of interactivity (menus, toggles) without pulling in a large JavaScript framework.
*   **StPageFlip JS**\
    Creates the mobile-first, 60 fps page-turning flipbook animation, complete with keyboard and touch controls, plus accessibility support (ARIA labels).

How these improve your experience:

*   Fast, incremental updates keep you engaged as story pages appear in real time.
*   Consistent styling ensures a friendly, pastel-colored interface that’s easy on the eyes.
*   Lightweight libraries mean quicker load times on both desktop and mobile.

## Backend Technologies

These power the behind-the-scenes work: storing your data, running AI, and generating images.

*   **Django 5 (Pegasus scaffold)**\
    A mature web framework that organizes code clearly, with built-in admin pages for quick setup.
*   **Django Channels**\
    Enables live WebSocket connections so we can stream text and images to your browser as soon as they’re ready.
*   **Celery (in Docker containers)**\
    Manages background jobs—like calling AI models to write text or make images—so the web server stays responsive.
*   **PostgreSQL (DigitalOcean Managed)**\
    A reliable database for storing users, books, character traits, and settings.
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

*   **AI Text & Image Providers**

    *   OpenAI GPT-4o (primary) and Anthropic Claude 3.7 Sonnet (fallback) for story text.
    *   DALL·E 3 (primary) and self-hosted Stable Diffusion XL + LoRA (fallback) for illustrations.
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
    Text appears immediately; images load as soon as they’re ready through WebSockets and HTMX swaps.
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

*   We use **Django, HTMX, Tailwind, and Alpine.js** for a lightweight, fast frontend.
*   **Django Channels, Celery, and Redis** power real-time AI generation and background jobs.
*   **DigitalOcean** hosts everything under budget, with managed databases and object storage.
*   **OpenAI, Anthropic, DALL·E, and Stable Diffusion** deliver the storytelling magic, wrapped in a service layer for easy swapping.
*   **Stripe, SendGrid, Twilio** handle payments and notifications securely.
*   **Sentry, Grafana Cloud, Healthcheck.io** keep an eye on errors and performance.

This combination ensures parents and children get a seamless, safe, and enchanting co-creation experience today—and lays a solid foundation for future growth and features.
