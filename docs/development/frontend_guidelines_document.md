# StorySprout Frontend Guideline Document

This document lays out how the StorySprout frontend is built, styled, and organized. It’s written in everyday language so anyone on the team can understand how our web interface works—even if you’re not a hardcore developer.

## 1. Frontend Architecture

### 1.1 Overview

*   We use **Django templates** as our base. Pages are rendered server-side, and we sprinkle in bits of dynamic behavior with **HTMX** and **Alpine.js**.
*   **Tailwind CSS** is loaded via a CDN and configured directly in the main template. This allows for rapid prototyping with utility-first classes without a local build step.

### 1.2 Scalability & Maintainability

*   **Template Includes**: Common page components (headers, footers, form fields) live in reusable template files. If you need the same widget in two places, you just `{% include %}` it.
*   **Utility-First Styles**: Tailwind’s purge feature strips out unused classes, keeping the CSS bundle small as the project grows.
*   **HTMX + Alpine.js**: We avoid large frontend frameworks. HTMX fetches snippets from the server and swaps them into the page. Alpine.js manages tiny bits of interactive state (toggles, dropdowns) right in the HTML.

### 1.3 Performance

*   Pages load fast because the server sends ready-to-go HTML, and only small fragments update on user actions.
*   Tailwind’s purging and minified builds ensure lean CSS bundles.
*   Static assets (images, PDFs) live on DigitalOcean Spaces (S3) and are served via CDN rules.

## 2. Design Principles

### 2.1 Usability

*   Clear form flows (e.g., Character Builder, Plot Composer) guide parents and kids step by step.
*   Button labels and field hints use everyday language: “Add your hero’s name,” “Choose a mood.”

### 2.2 Accessibility

*   We meet **WCAG AA** contrast levels for text and background.
*   Interactive elements have proper `aria-label`s. The flipbook supports VoiceOver (iOS/macOS) and NVDA (Windows).
*   Keyboard navigation: all buttons and links are reachable with Tab, and HTMX swaps preserve focus.

### 2.3 Responsiveness

*   Mobile-first design. Layouts adapt from phone (single-column) to tablet and desktop (multi-column) using Tailwind breakpoints (`sm`, `md`, `lg`).
*   The flipbook reader works on touch devices and desktop browsers alike.

## 3. Styling and Theming

### 3.1 Styling Approach

*   **Utility-first** with Tailwind CSS—no heavy custom CSS files or BEM conventions. Variants (`hover:`, `focus:`) live right in the class list.
*   The Tailwind configuration is defined within a `<script>` tag in the main layout. This setup is simple for development but does not include purging of unused classes.

### 3.2 Theming

*   One consistent look across the app—soft pastel colors, rounded containers, subtle shadows.

### 3.3 Visual Style

*   Style: Modern flat design with soft drop shadows (glass-like feel on cards).
*   Cards and panels use `rounded-2xl` and `shadow-lg/10` for gentle depth.

### 3.4 Color Palette

*   Primary pink: `#FFD2E0`
*   Secondary blue: `#CFF6FF`
*   Background off-white: `#F9FAFB`
*   Text dark: `#1F2937` (Tailwind’s `gray-800`)
*   Accent green (success): `#10B981` (Tailwind’s `emerald-500`)
*   Warning yellow: `#F59E0B`

### 3.5 Typography

*   **Headings (H1)**: Inter Display, weight 700, 48px (Tailwind: `text-4xl font-bold`).
*   **Body text**: Inter, weight 500, 18px (Tailwind: `text-lg font-medium`).
*   Line-height and letter spacing follow Inter’s defaults for readability.

## 4. Component Structure

### 4.1 Organization

*   Templates are organized by feature within the `templates` directory. Reusable components, such as those for `django-cotton`, are located in a shared `cotton` subdirectory.

### 4.2 Reuse & Consistency

*   Each component accepts parameters (via Django context) to render different labels, icons, or modes.
*   HTMX attributes (`hx-get`, `hx-post`, `hx-swap`) are added in these includes so developers don’t have to reinvent the wheel.

### 4.3 Benefits of Component-Based Frontend

*   Changes to a single include file ripple across the app. Update your modal style once, and every modal updates.
*   Encourages consistency and cuts down on copy-pasted code.

## 5. State Management

### 5.1 Alpine.js for Local State

*   Use Alpine.js (`x-data`, `x-show`, `x-on:click`) for small UI interactions: dropdowns, collapsible panels, tooltip toggles.
*   No global store; each component manages its own tiny bit of state.

### 5.2 HTMX for Server-Driven Updates

*   Form submissions and list filters hit Django endpoints and return a chunk of HTML.
*   Shared data (user profile, subscription status) is available in the initial page context.

### 5.3 Smooth User Experience

*   Partial page swaps mean no full reloads. The character builder updates right on the form; the plot composer shows live previews.

## 6. Routing and Navigation

### 6.1 Server-Side Routing

*   All URLs are defined in Django’s `urls.py` files. The main `core/urls.py` file includes the URL configurations from each app, which are the source of truth for the application's routing.

### 6.2 HTMX-Enhanced Navigation

*   Clicking “Continue to Step 3” in the plot composer sends an `hx-post` to the wizard view, which swaps in the next step’s form.
*   Browser history is managed with `hx-push-url`, so the back button still works.

### 6.3 Flipbook Reader

*   The flipbook component initializes on a container with all pages preloaded or streamed in.
*   Next/previous controls and keyboard arrows trigger page turns at 60fps.

## 7. Performance Optimization

### 7.1 Asset Optimization

*   Tailwind CSS is loaded from a CDN. For production, switching to a compiled and purged CSS file would be a key optimization.
*   JavaScript libraries like Alpine.js and HTMX are served locally from the `static/vendor/` directory.

### 7.2 Lazy Loading & Streaming

*   Flipbook images lazy-load as pages come into view.
*   During book generation, the text appears immediately; images stream in via Django Channels and HTMX swaps.

### 7.3 Caching

*   Template fragment caching for sidebar lists and navigation.
*   HTTP caching headers on static assets (images, CSS, JS).

## 8. Testing and Quality Assurance

### 8.1 Unit & Integration Tests

*   Frontend logic covered by Django’s live server tests (via pytest). We check HTMX endpoints return the correct HTML fragment.
*   Component includes are tested by rendering them with test contexts and verifying key elements exist.

### 8.2 End-to-End (E2E)

*   **Cypress** scripts simulate a parent creating an account, building a character, generating a book, and hitting the payment wall.
*   We assert visible text, button states, and that HTMX swaps occur correctly.

### 8.3 Accessibility & Performance Audits

*   Run **axe-core** in CI to catch missing ARIA attributes or color-contrast issues.
*   Use **Lighthouse** in CI for performance scoring—keep first-contentful-paint under 2s on slow 3G emulation.

## 9. Conclusion and Overall Frontend Summary

Our frontend is built to be simple, accessible, and fast. By combining Django templates, HTMX, Alpine.js, and Tailwind CSS, we:

*   Keep complexity low, so we can iterate quickly for our 14-day MVP goal.
*   Ensure a consistent look and feel with a pastel theme, Inter fonts, and reusable components.
*   Deliver a responsive, keyboard-friendly experience that meets WCAG AA standards.
*   Optimize performance with server-side rendering, CSS purging, lazy loading, and real-time streaming.

With these guidelines in hand, any new feature or UI tweak will fit right into the StorySprout frontend without confusion. Welcome aboard—and happy coding!
