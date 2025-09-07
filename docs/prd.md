# Project Requirements Document (PRD)

**Project Name:** StorySprout\
**Objective:** Build a web-based platform where parents and children co-create fully illustrated storybooks in real time, then download a print-ready PDF. Launch an MVP in 14 days on DigitalOcean, keep monthly infra costs under $50 (excluding AI usage), and avoid vendor lock-in.

## 1. Project Overview

StorySprout lets families define characters and a rough plot, then uses AI to generate a consistent narrative and matching illustrations page by page. As kids watch text and images appear in real time, they stay engaged—and parents stay in control of tone, safety, and spend. When the story is done, families download a PDF ready for home printing or gift-giving.

We’re building this to spark creativity, simplify personalized bookmaking, and convert curiosity into paid subscriptions. Success means delivering an alpha demo at day 7 and a public beta by day 14, supporting at least 1,000 paying users on a single 2 vCPU droplet, and maintaining > 99.5% uptime at ≤ $50/month infrastructure cost.

## 2. In-Scope vs. Out-of-Scope

**In-Scope (MVP):**

*   Family/Team accounts (parent-admin & child-creator roles)
*   Freemium model (first 3 pages free; Premium: 60 pages/mo + add-ons + unlimited tier)
*   Character Builder with single photo upload → style-ref image
*   5-step Plot Composer Wizard (manual edits + AI autofill)
*   AI pipeline: GPT-4o (fallback Claude 3.7), DALL·E 3 or self-hosted SD-XL+LoRA
*   **Real-time streaming via Server-Sent Events (SSE) + HTMX (text first, then images)**
*   Flipbook reader (mobile-first, 60 fps, keyboard & screen-reader support)
*   Print-ready PDF export (WeasyPrint, 0.5″ margins, auto-title page; US-Letter & 8×10)
*   Safety layer: text/image moderation (violence, profanity, sexual content, self-harm)
*   Notifications: email (SendGrid) + optional SMS (Twilio)
*   Library & versioning + soft-delete (90 days retention)

**Out-of-Scope (Post-MVP):**

*   Hardcover print-on-demand (e.g., Blurb API)
*   Multilingual story support
*   Live multi-user co-editing (Yjs)
*   Custom backgrounds, clip art, or fonts beyond Inter family

## 3. User Flow

A **new parent** lands on the signup page, registers via email or social login, and confirms their address. They create a “family team,” invite children by email, and immediately see how many free pages remain in their account. Guided by a simple dashboard, they pick the freemium plan, then click “Start New Book.”

In the **Character Builder**, the parent or child names a hero, selects a visual style, and uploads a photo. StorySprout shows a generated style-ref image instantly, and they enter simple personality traits. Next, the **Plot Composer Wizard** walks them through setting, conflict, resolution, moral, and length—in each step they type or hit “AI suggest.” When the outline is ready, they press “Generate Story.”

Pages start streaming: text types in line by line, then placeholders swap into illustrations as they finish. Parents can pause to edit flagged content (violence, profanity, etc.) or adjust moderation thresholds. Once the book is complete, they switch to the **Flipbook Reader** to flip through at 60 fps, with ARIA labels for VoiceOver/NVDA. Finally, they click **Export PDF**, receive an email link, and see the finished book in their library—ready to duplicate, continue editing, or soft-delete (90-day trash).

## 4. Core Features

*   **Family & Team Accounts**\
    • Parent-admin & child-creator roles\
    • Freemium + Stripe subscriptions (“Sprout Free”, “Sprout Premium”, unlimited tier)\
    • Metered pages (60 pages/mo) + add-on purchases
*   **Character Builder**\
    • Single image upload → consistent style-ref generation\
    • Store embedding & style_ref_id for visual continuity\
    • Traits captured as simple JSON
*   **Plot Composer Wizard**\
    • 5 guided steps: setting, conflict, climax, resolution, moral\
    • Manual text entry or AI autofill\
    • Live editable outline
*   **AI Generation Pipeline**\
    • Text: OpenAI GPT-4o (Anthropic Claude 3.7 fallback) via Celery tasks\
    • Images: DALL·E 3 (fixed seed & style-ref) or SD-XL+LoRA self-hosted\
    • AI prompt templates are stored in dedicated files for easy tuning.\
    • **Streaming updates via Server-Sent Events (SSE) + HTMX swaps**
*   **Flipbook Reader**\
    • A mobile-first flipbook component with 60 fps animations\
    • Keyboard navigation + ARIA labels + alt text for screen readers\
    • Hidden “read aloud” menu
*   **PDF Export**\
    • WeasyPrint → same HTML at 300 dpi, CMYK\
    • 0.5″ margins, auto title page, US-Letter & 8×10 presets
*   **Safety Layer**\
    • OpenAI moderation APIs for violence, profanity, sexual content, self-harm\
    • Configurable thresholds per team (JSON)\
    • Auto-block, parent-override, or flag
*   **Notifications**\
    • SendGrid email alerts\
    • Optional Twilio SMS\
    • Automatic retry logic (2 retries per page) then skip + flag
*   **Library & Versioning**\
    • List, search, duplicate, continue, soft-delete books\
    • Soft-deleted items purged after 90 days

## 5. Tech Stack & Tools

Frontend

*   Django templates + HTMX (partial page updates)
*   Tailwind CSS
*   Alpine.js for micro-interactions

Backend & Ops

*   Django 5
*   PostgreSQL (DigitalOcean Managed)
*   Redis (broker + pub/sub for websockets)
*   Celery workers in Docker
*   DigitalOcean Spaces (S3-compatible) for media & PDFs
*   GitHub Actions → Docker → SSH deploy (blue-green)

Authentication & Billing

*   django-allauth (email, Google, Apple)
*   Stripe (subscriptions + metered billing)

AI & Images

*   OpenAI GPT-4o + Anthropic Claude 3.7 Sonnet
*   DALL·E 3 (2048×2048) or self-hosted Stable Diffusion XL + LoRA

Notifications & Moderation

*   SendGrid (email)
*   Twilio (SMS)
*   Service layer abstraction for AI and moderation calls

Observability

*   Sentry (error tracking)
*   Grafana Cloud + Prometheus metrics
*   Healthcheck.io (Celery beat)

IDE & AI Coding Tools

*   Windsurf, Cursor, Cline
*   GPT-o3, Grok 3, Gemini 2.5 Pro

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
