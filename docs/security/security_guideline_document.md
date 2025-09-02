# StorySprout MVP: 14-Day Implementation Plan

This plan outlines feature development, infrastructure setup, security controls, timelines, and cost estimates to deliver the StorySprout MVP in 14 days.

## 1. High-Level Architecture

• **Frontend**: Django templates + HTMX, Tailwind, Alpine.js, StPageFlip JS\
• **Backend**: Django 5 (Pegasus scaffold), Django Channels, Celery (Docker service)\
• **Data Stores**: DigitalOcean Managed PostgreSQL; Redis (broker + channels)\
• **Object Storage**: DigitalOcean Spaces (S3 compatible)\
• **AI Services**: OpenAI GPT-4o / Anthropic Claude fallback; DALL·E 3 / self-hosted SD-XL+LoRA\
• **Auth & Billing**: django-allauth (Email + Google/Apple), Stripe subscriptions\
• **CI/CD**: GitHub Actions → Docker build → SSH deploy (blue-green)\
• **Observability**: Sentry (errors), Grafana Cloud (metrics), Healthcheck.io (Celery)

Diagram (textual):

`[Browser] ↔ HTTPS ↔ [Django + HTMX] ↔ {Postgres, Redis, Spaces} ↕ [Celery] ↕ [AI Providers Service Layer] / \ OpenAI GPT / DALL·E SD-XL + LoRA (self-hosted)`

## 2. Security & Compliance Checklist

1.  **Authentication & RBAC**

    *   Parent-admin vs Child-creator roles enforced server-side
    *   django-allauth with strong password policy (Argon2 + unique salts)
    *   Session cookies: `HttpOnly`, `Secure`, `SameSite=Strict`

2.  **Input Validation & Output Encoding**

    *   DRF or Django forms with built-in validators
    *   HTMX responses context-aware escaped
    *   File uploads: whitelist MIME & extensions, max size, virus scan

3.  **API & Service Security**

    *   Enforce HTTPS + HSTS
    *   Rate limiting via Django Ratelimit (Celery tasks throttled)
    *   CORS restricted to app domains

4.  **Data Protection**

    *   TLS v1.2+ in transit; AES-256 at rest (Spaces + Postgres)
    *   No secrets in code: use DO App Platform env vars or Vault
    *   GDPR: soft-delete retention (90 days), PII minimization

5.  **Web Security Hygiene**

    *   CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy
    *   CSRF tokens on all state-changing requests
    *   Avoid storing PII in localStorage

6.  **Infrastructure Hardening**

    *   Hardened DO Droplet (only SSH, firewall)
    *   Disable debug in production, rotate logs securely

## 3. Cost Estimate (Monthly)

|                        |                        |           |                    |
| ---------------------- | ---------------------- | --------- | ------------------ |
| Service                | Plan/Size              | Est. Cost | Notes              |
| DigitalOcean Droplet   | 2 vCPU / 4 GB RAM      | $18       | App + Celery       |
| DO Managed PostgreSQL  | Standard 1 vCPU / 1 GB | $15       | HA off for cost    |
| Redis (Managed)        | 1 GB                   | $7        | Broker + channels  |
| Spaces (50 GB storage) | Pay-as-you-go          | $5        | < 50 GB/month      |
| Bandwidth & Misc.      | —                      | ~$5       | Egress, backups    |
| **Total**              |                        | **≈ $50** | Excluding AI usage |

## 4. Timeline & Deliverables

### Days 0–1: Foundations & CI/CD

*   [ ] Provision DO Droplet, Managed Postgres, Redis, Spaces
*   [ ] Initialize GitHub Actions: Docker build & SSH deploy (blue-green)
*   [ ] Configure env vars, secrets management
*   [ ] Baseline security headers, HTTPS, HSTS, CSP

### Days 2–3: Authentication & Billing

*   [ ] Integrate django-allauth (email + Google/Apple)
*   [ ] Implement Parent-admin / Child-creator RBAC
*   [ ] Stripe freemium/subscription (3 free pages + metered plan)
*   [ ] Secure session configs, password policies

### Days 4–5: Character Builder

*   [ ] Model & migration for Character (name, style, traits)
*   [ ] File upload to Spaces (validate & scan)
*   [ ] Style-reference extraction pipeline (Celery task stub)
*   [ ] UI: HTMX stepper for character creation

### Days 6–7: Plot Composer & AI Text

*   [ ] Wizard UI (5 steps) via HTMX + Alpine.js
*   [ ] Service layer: `ai_providers/text.py` → GPT-4o / Claude
*   [ ] Celery tasks for text generation + streaming via Channels
*   [ ] Prompt template in `/prompts/story.md`

### Days 8–9: Image Generation & Caching

*   [ ] Service layer: `ai_providers/image.py` → DALL·E 3 or SD-XL+LoRA toggle in admin
*   [ ] Cache images (Spaces + local thumbnail)
*   [ ] Celery tasks + streaming progress events
*   [ ] UI placeholders: spinner → progressive reveal

### Days 10: Flipbook Reader & PDF Export

*   [ ] Integrate StPageFlip JS with ARIA + keyboard support
*   [ ] WeasyPrint PDF export (300 dpi CMYK; US-Letter & 8×10)
*   [ ] Auto title page + margins

### Day 11: Safety & Moderation

*   [ ] OpenAI Moderation API integration for text & images
*   [ ] JSON config for threshold levels (violence, profanity, self-harm)
*   [ ] Parent override / auto-block / flag workflows

### Day 12: Notifications & Library CRUD

*   [ ] Email (SendGrid) + SMS (Twilio) alerts on job success/failure
*   [ ] Auto-retry logic (2×), then skip + flag
*   [ ] Library: list, duplicate, edit, soft-delete (soft-deleted > 90 days auto-purge)

### Day 13: Testing & Compliance

*   [ ] Unit & integration tests (CI)
*   [ ] Security audit: SAST, vulnerability scan, dependency SCA
*   [ ] Performance test: 12-page book ≤ 30 s perceived (streaming)
*   [ ] WCAG AA contrast & ARIA checks

### Day 14: Production Rollout & Buffer

*   [ ] Blue-green deploy to production
*   [ ] Smoke tests, live data run
*   [ ] Final bug-fixes, documentation handover
*   [ ] Monitoring alerts & runbooks

## 5. Risk & Mitigation

• **AI Cost Overrun**: Monitor DALL·E spend; auto-switch to SD-XL+LoRA when > $100/mo\
• **Performance Bottlenecks**: Early load testing; optimize Celery concurrency\
• **Security Gaps**: Daily security review; automated scans in CI\
• **Lock-In**: All third-party calls behind `ai_providers/` service layer

This plan ensures on-time delivery, cost control, and built-in security by design. Please review and flag any gaps or adjustments needed before kick-off.
