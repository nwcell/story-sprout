# Story Sprout Templates Structure

This README documents the template structure of the Story Sprout project to ensure consistency and clarity.

## Base Templates

The project uses three specialized base templates for different sections of the application:

1. **`landing/landing_base.html`** - Base template for public-facing marketing pages
   - Used for: homepage, landing pages, public content
   - Previously named: `base.html`, then `marketing_base.html`

2. **`dashboard/dashboard_base.html`** - Base template for the app dashboard
   - Used for: authenticated user dashboard, story management, user settings
   - Previously named: `dashboard/base.html`

3. **`account/auth_base.html`** - Base template for authentication pages
   - Used for: login, signup, password reset, etc.
   - Previously named: `account/base.html`

## Shared Components

Common elements are extracted into shared components to reduce duplication:

- **`components/head.html`** - Common head elements, meta tags, and scripts
- **`components/tailwind_config.html`** - Shared Tailwind configuration
- **`dashboard/partials/`** - Partials specific to the dashboard

## Extending Base Templates

Example usage:

```html
<!-- For landing/marketing pages -->
{% extends "landing/landing_base.html" %}

<!-- For dashboard pages -->
{% extends "dashboard/dashboard_base.html" %}

<!-- For authentication pages -->
{% extends "account/auth_base.html" %}
```

## Template Block Structure

Each base template provides the following blocks:

1. **Marketing Base:**
   - `title` - Page title
   - `extra_head` - Additional head content
   - `header` - Page header content
   - `content` - Main content
   - `footer` - Footer content
   - `extra_js` - Additional JavaScript

2. **Dashboard Base:**
   - `title` - Page title
   - `extra_head` - Additional head content
   - `dashboard_content` - Main dashboard content
   - `extra_js` - Additional JavaScript

3. **Auth Base:**
   - `title` - Page title
   - `extra_head` - Additional head content
   - `content` - Main content
   - `extra_js` - Additional JavaScript

## HTMX Integration

All base templates include proper HTMX setup:
- Include the script via `{% htmx_script %}`
- Set CSRF token headers via `hx-headers='{"x-csrftoken": "{{ csrf_token }}"}'`
