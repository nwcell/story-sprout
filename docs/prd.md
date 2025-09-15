# Project Requirements Document (PRD)

**Project Name:** Story Sprout\
**Objective:** Build a web-based platform for creating AI-assisted illustrated stories with real-time collaboration features. Focus on clean architecture using Django, HTMX, and modern AI integration patterns.

## 1. Project Overview

Story Sprout is a Django-based storytelling platform that helps users create illustrated stories with AI assistance. The platform focuses on providing a clean, modern interface using HTMX for dynamic interactions and Cotton components for reusable UI elements.

The current implementation centers around individual Story and Page models, with an AI job system for asynchronous content generation. Real-time updates are delivered via Server-Sent Events, and the entire application is built with modern Django patterns and comprehensive tooling.

## 2. In-Scope vs. Out-of-Scope

**In-Scope (Current Implementation):**

*   User authentication with django-allauth
*   Story and Page models with ordered pages
*   AI integration via Pydantic AI framework
*   Job-based async processing with Celery
*   Real-time updates via Server-Sent Events (SSE) + HTMX
*   Cotton component-based UI system
*   Django Ninja API framework
*   Subscription system foundation
*   Development tooling (uv, ruff, pytest, pre-commit hooks)
*   Multi-environment settings management

**Future Considerations:**

*   PDF export functionality
*   Character and team models
*   Advanced AI content moderation
*   Mobile app development
*   Print-on-demand integration
*   Multi-user collaboration features

## 3. Current User Flow

A **user** lands on the signup page and registers via email authentication. After email verification, they access the dashboard where they can view their existing stories or create new ones.

When creating a **new story**, users start with a simple form to enter a title and description. The interface uses Cotton components with HTMX for smooth interactions—clicking to edit fields inline without page reloads.

Users can add **pages** to their story, with each page containing text content and image descriptions. The AI integration system processes content requests asynchronously, with real-time updates delivered via Server-Sent Events as jobs complete.

The **story detail view** shows all pages in order, with the ability to navigate between them, edit content inline, and track AI processing status. All interactions use the Cotton + HTMX pattern for a responsive user experience.

## 4. Core Features

*   **User Authentication**\
    • Django-allauth for email-based registration\
    • Social login support (Google, Apple)\
    • Email verification system
*   **Story Management**\
    • Create and manage individual stories\
    • Story title and description editing\
    • UUID-based story identification for clean URLs
*   **Page System**\
    • Ordered pages within stories using django-ordered-model\
    • Page content and image text fields\
    • Navigation between pages with proper ordering
*   **AI Integration Pipeline**\
    • Pydantic AI framework for type-safe AI interactions\
    • Job-based async processing via Celery\
    • Support for Google GenAI and LiteLLM\
    • **Real-time progress updates via Server-Sent Events (SSE)**
*   **Modern UI Architecture**\
    • Cotton component system for reusable UI elements\
    • HTMX for dynamic interactions without page reloads\
    • Tailwind CSS for consistent styling\
    • Alpine.js for client-side interactivity
*   **Development Infrastructure**\
    • Django Ninja API framework\
    • Multi-environment settings (dev/test/prod)\
    • Comprehensive testing with pytest\
    • Code quality tools (ruff, pre-commit hooks)\
    • uv for fast Python package management
*   **Subscription Foundation**\
    • Stripe integration scaffolding\
    • Subscription plan models\
    • Customer management system

## 5. Tech Stack & Tools

**Frontend**
*   Django templates with Cotton components
*   HTMX for dynamic updates
*   Tailwind CSS for styling
*   Alpine.js for client-side interactivity

**Backend**
*   Django 5.2+ with modern patterns
*   PostgreSQL (production) / SQLite (development)
*   Redis for Celery broker and SSE
*   Django EventStream for Server-Sent Events
*   Celery for async task processing

**Development Tools**
*   uv for Python package management
*   ruff for linting and formatting
*   pytest for testing
*   pre-commit hooks for code quality
*   Django Ninja for API development

**AI Integration**
*   Pydantic AI framework
*   Google GenAI
*   LiteLLM for model access
*   Custom job workflow system

**Authentication & Payments**
*   django-allauth (email, social logins)
*   Stripe integration foundation

**Infrastructure**
*   Multi-environment settings management
*   Django-environ for configuration
*   Loguru for advanced logging
*   MCP (Model Context Protocol) support

## 6. Non-Functional Requirements

*   **Performance:**\
    • ≤ 30 s perceived wait for a 12-page book (streaming ok)\
    • Support 1,000 paying users on 2 vCPU + managed Postgres/Redis
*   **Reliability & Uptime:**\
    • 99.5% uptime SLA\
    • 98% success rate on book generation jobs
*   **Cost:**\
    • $50/month max for infra (excl. AI credits)\
    • Auto-switch to SD-XL if DALL·E spend > $100/mo
*   **Security & Compliance:**\
    • TLS everywhere\
    • Stripe PCI-compliant checkout\
    • GDPR-friendly data retention
*   **Usability & Accessibility:**\
    • WCAG AA contrast\
    • Keyboard & screen-reader support (VoiceOver, NVDA)\
    • ARIA labels & alt text

## 7. Constraints & Assumptions

*   MVP launch ≤ 14 days on DigitalOcean droplet with Docker Compose
*   GPT-4o and DALL·E 3 availability; fallback to Claude 3.7 / SD-XL
*   Single style-ref per character; no custom backgrounds/fonts
*   Teachers use same parent-admin role
*   Soft-delete retention fixed at 90 days
*   No bleed/crop marks or cover pages in MVP
*   Vendor lock-in mitigated by service layer wrapping all third-party calls

## 8. Known Issues & Potential Pitfalls

*   **AI Cost Spikes:**\
    • Mitigation: switch to self-hosted SD-XL, enforce page quotas, cache images aggressively
*   **Model/API Outages:**\
    • DALL·E failure → fallback to SD-XL\
    • GPT outage → Anthropic Claude fallback
*   **Prompt Drift (style inconsistency):**\
    • Mitigation: short prompts + embed style-ref image early
*   **Rate Limiting:**\
    • Limit 5 active generations per team\
    • Queueing & back-off logic in Celery
*   **Streaming Performance:**\
    • HTMX OOB swaps for updates (faster than full refresh)\
    • Monitor Redis connection usage
*   **Moderation False Positives:**\
    • Parent override UI + two-retry logic to reduce manual intervention

This PRD covers all essential details for an AI-driven implementation, ensuring subsequent technical and design documents can be generated without ambiguity.
