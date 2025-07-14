---
trigger: always_on
---

# Frontend Development Guide

**Philosophy:** Leverage a declarative stack (Tailwind, Alpine.js, HTMX) for maintainable and interactive UIs with minimal custom JavaScript.

---

## 1. Core Stack & Setup

- **Tech:** Tailwind CSS, Alpine.js, HTMX, django-htmx, crispy-tailwind.
- **`settings.py`**: Ensure `django_htmx`, `crispy_forms`, `crispy_tailwind` are in `INSTALLED_APPS` and `HtmxMiddleware` is in `MIDDLEWARE`.
- **`base.html`**: Must include scripts for Tailwind and Alpine, `{% htmx_script %}`, and the CSRF header on the `<body>` tag.

```html
<!-- base.html essentials -->
{% load django_htmx %}
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
    {% htmx_script %}
</head>
<body hx-headers='{"x-csrftoken": "{{ csrf_token }}"}'>
    ...
</body>
</html>
```

---

## 2. Key Patterns & Best Practices

### In-Place Editing (Canonical Pattern)

This is the standard for all click-to-edit functionality.

**1. Display Element (Loads the form on click):**
```html
<div hx-get="{% url 'get_form' object.id %}" hx-trigger="click" hx-swap="outerHTML">
    {{ object.value }}
</div>
```

**2. Edit Form (Returned by the view):**
```html
<form hx-post="{% url 'save_form' object.id %}"
      hx-swap="outerHTML"
      hx-trigger="submit, blur from:input, keydown[key=='Enter'] from:body"
      class="flex items-center space-x-2"
      x-data x-init="$nextTick(() => $el.querySelector('input').focus())">

    <input name="value" value="{{ object.value }}" class="...">

    <button type="button" @mousedown.prevent hx-get="..." title="Cancel (Esc)">X</button>
    <button type="submit" @mousedown.prevent title="Save (Enter)">✓</button>
</form>
```

**Core Techniques:**
- **Triggers (`hx-trigger`):**
    - **Save:** `submit, blur from:input, keydown[key=='Enter'] from:body`
    - **Textarea Save:** Use `keydown[metaKey&&key=='Enter']` to allow newlines.
    - **Cancel:** A separate button `hx-get`s the display partial. For global cancel, add `keydown[key=='Escape']` to the form's `hx-trigger` and have the view return the display partial.
- **Blur/Click Fix (`@mousedown.prevent`):** **CRITICAL**. Add to all form buttons to prevent the input's `blur` event from firing before the button click is registered.
- **Auto-Focus (`x-init`):** Use `$nextTick(() => ... .focus())` to focus the input after HTMX swaps it into the DOM.

### Other Core Patterns

- **Dynamic Content:** To add items to a list, use `hx-post` on a button with `hx-swap="beforeend"` targeting the list container.
- **Loading States:** Use the `htmx-indicator` class on a spinner. The `htmx-request` class is automatically applied to elements during a request, allowing for CSS transitions (e.g., `form.htmx-request { opacity: 0.5; }`).
- **Security:**
    - The global `hx-headers` handles CSRF.
    - Always validate and sanitize data on the backend.
    - Never use `x-html` or `|safe` with user-provided content.

### 6.3 Search with Live Results
```html
<div x-data="{ query: '' }">
    <input x-model="query"
           hx-get="{% url 'search_stories' %}"
           hx-trigger="input changed delay:300ms"
           hx-target="#search-results"
           hx-vals="js:{q: query}"
           placeholder="Search stories..."
           class="w-full px-4 py-2 border rounded-lg">
    
    <div id="search-results" class="mt-4">
        <!-- Results populated by HTMX -->
    </div>
</div>
```

---

## 7. Performance & Best Practices

### 7.1 Minimize JavaScript
- Use Alpine.js only for client-side interactivity that can't be handled by HTMX
- Prefer HTMX for server interactions and DOM updates
- Use CSS for animations when possible

### 7.2 Efficient HTMX Patterns
```html
<!-- Good: Specific targeting -->
<button hx-post="/toggle" hx-target="#status" hx-swap="outerHTML">
    Toggle
</button>

<!-- Good: Debounced input -->
<input hx-get="/search" 
       hx-trigger="input changed delay:300ms" 
       hx-target="#results">

<!-- Good: Use hx-push-url for navigation -->
<a hx-get="/page/2" hx-target="#content" hx-push-url="true">
    Next Page
</a>
```

### 7.3 Template Organization
```
templates/
├── dashboard/
│   └── base.html              # Base template with all scripts
├── stories/
│   ├── stories.html           # Full page templates
│   ├── story_detail.html
│   └── partials/              # HTMX partial templates
│       ├── story_title.html
│       ├── story_title_form.html
│       └── page_item.html
```

---

## 8. Testing Considerations

### 8.1 Test HTMX Responses
```python
def test_htmx_story_update(self):
    response = self.client.post(
        '/stories/1/update/',
        {'title': 'New Title'},
        HTTP_HX_REQUEST='true'
    )
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'New Title')
```

### 8.2 Alpine.js Testing
- Use semantic HTML that works without JavaScript
- Test progressive enhancement
- Verify keyboard accessibility

---

## 9. Troubleshooting

### 9.1 Common HTMX Issues
- **CSRF errors**: Ensure `hx-headers` includes CSRF token
- **Response not updating**: Check target selectors and swap modes
- **Events not firing**: Verify trigger syntax and element selection

### 9.2 Alpine.js Debugging
- Use `Alpine.store()` for global state
- Add `x-data` to parent elements for nested components
- Check browser console for initialization errors

---

**Remember:** This stack prioritizes maintainability and security over custom solutions. When in doubt, leverage the existing patterns and avoid writing custom JavaScript unless absolutely necessary.
