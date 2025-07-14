# Frontend Development Guide

**Project:** Story Sprout - Batteries-Included Frontend Stack  
**Philosophy:** Leverage proven tools with minimal custom JavaScript for maintainable, secure, and interactive UIs.

---

## 1. Frontend Stack Overview

### Core Technologies
- **Tailwind CSS** - Utility-first CSS framework with UI component patterns
- **Alpine.js** - Lightweight reactive JavaScript framework for UI behavior
- **HTMX** - Declarative AJAX and partial page updates via HTML attributes
- **django-htmx** - Django integration for HTMX with middleware and template tags
- **django-crispy-forms + crispy-tailwind** - Form rendering with consistent Tailwind styling

### Design Principles
1. **Declarative over Imperative** - Use HTML attributes and directives instead of custom JavaScript
2. **Progressive Enhancement** - Start with working HTML, enhance with interactivity
3. **Component Reuse** - Leverage Tailwind UI patterns and crispy-forms layouts
4. **Security First** - CSRF protection, proper escaping, trusted routes only
5. **Accessibility** - Use semantic HTML and proper ARIA attributes

---

## 2. Project Setup & Configuration

### Django Settings
```python
# In settings.py
INSTALLED_APPS = [
    # ... other apps
    'django_htmx',
    'crispy_forms',
    'crispy_tailwind',
]

MIDDLEWARE = [
    # ... other middleware
    'django_htmx.middleware.HtmxMiddleware',
]

# Crispy Forms Configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"
```

### Base Template Setup
```html
<!-- templates/dashboard/base.html -->
{% load django_htmx %}
<!doctype html>
<html>
<head>
    <!-- Tailwind CSS (via CDN or build process) -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Alpine.js -->
    <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
    
    <!-- HTMX + django-htmx -->
    {% htmx_script %}
</head>
<body hx-headers='{"x-csrftoken": "{{ csrf_token }}"}'>
    <!-- Your content -->
</body>
</html>
```

---

## 3. Interactive Patterns

### 3.1 Robust In-Place Editing (Best Practice)

This pattern combines HTMX and Alpine.js to create a feature-rich, declarative in-place editing experience. It supports keyboard shortcuts, save-on-blur, and handles common UI race conditions without custom JavaScript functions.

**Key Features:**
- **Display Mode**: Shows the current value. Click to enter edit mode.
- **Edit Mode**: Shows a form with the value in an input/textarea.
- **Save**: `Enter` (for inputs), `Ctrl/Cmd+Enter` (for textareas), clicking the Save button, or blurring the field.
- **Cancel**: `Escape` key or clicking the Cancel button.

--- 

#### **Pattern 1: Single-Line Input (e.g., Story Title)**

**Display Partial (`story_title.html`):**
```html
<div hx-get="{% url 'stories:get_story_title_form' story.uuid %}"
     hx-trigger="click"
     hx-target="this"
     hx-swap="outerHTML"
     class="w-full">
    <h1 class="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl cursor-pointer hover:bg-gray-100 rounded-lg p-2">
        {{ story.title }}
    </h1>
</div>
```

**Form Partial (`story_title_form.html`):**
```html
{% load crispy_forms_tags %}
<form hx-post="{% url 'stories:edit_story_title' story.uuid %}"
      hx-target="this"
      hx-swap="outerHTML"
      hx-trigger="submit, keydown[key=='Enter'] from:body, blur from:input"
      class="w-full">
    {% csrf_token %}
    <div class="flex items-center space-x-2" x-data x-init="$nextTick(() => $el.querySelector('input').focus())">
        {{ form|crispy }}

        <!-- Button Group -->
        <span class="isolate inline-flex rounded-md shadow-sm">
            <!-- Cancel Button -->
            <button type="button"
                    @mousedown.prevent
                    class="... hover:bg-red-50 hover:text-red-600 ..."
                    title="Cancel (Esc)"
                    hx-get="{% url 'stories:get_story_title' story.uuid %}"
                    hx-target="closest form"
                    hx-swap="outerHTML">
                <svg><!-- X Icon --></svg>
            </button>
            <!-- Save Button -->
            <button type="submit"
                    @mousedown.prevent
                    class="... hover:bg-green-50 hover:text-green-600 ..."
                    title="Save (Enter)">
                <svg><!-- Checkmark Icon --></svg>
            </button>
        </span>
    </div>
</form>
```

--- 

#### **Pattern 2: Multi-Line Textarea (e.g., Description)**

This pattern is nearly identical, but adjusts for textareas.

**Key Differences:**
- **Save Trigger**: Use `keydown[metaKey&&key=='Enter']` and `keydown[ctrlKey&&key=='Enter']` for an explicit save action, as `Enter` alone should create a new line.
- **Layout**: A `flex-col` button group is often more suitable for taller textareas.

**Form Partial (`story_description_form.html`):**
```html
{% load crispy_forms_tags %}
<form hx-post="{% url 'stories:edit_story_description' story.uuid %}"
      hx-target="this"
      hx-swap="outerHTML"
      hx-trigger="submit, keydown[metaKey&&key=='Enter'] from:body, keydown[ctrlKey&&key=='Enter'] from:body, blur from:textarea"
      class="w-full">
    {% csrf_token %}
    <div class="flex items-start space-x-2" x-data x-init="$nextTick(() => $el.querySelector('textarea').focus())">
        {{ form|crispy }}

        <!-- Vertical Button Group -->
        <span class="isolate inline-flex flex-col rounded-md shadow-sm">
            <!-- Cancel/Save Buttons (same as above) -->
        </span>
    </div>
</form>
```

--- 

#### **Explanation of Key Techniques**

1.  **Declarative Triggers (`hx-trigger`)**
    - **Multiple Triggers**: A comma-separated list allows the form to be submitted by multiple events.
    - **Keyboard Shortcuts**: `keydown[key=='Escape'] from:body` listens for the Escape key globally. This is crucial so the user doesn't have to have the input focused to cancel.
    - **Save on Blur**: `blur from:input` or `blur from:textarea` triggers a save when the user clicks away from the field.

2.  **Fixing the Blur/Click Race Condition (`@mousedown.prevent`)**
    - **Problem**: When a user clicks a save/cancel button, the `blur` event on the input fires *first*, submitting and swapping the form. The button, no longer existing in the DOM, never receives the `click` event.
    - **Solution**: Add Alpine's `@mousedown.prevent` to the buttons. This directive prevents the `blur` event from being triggered on the input when the button is clicked, allowing the button's `hx-get` or `submit` action to proceed correctly.

3.  **Auto-Focus (`x-init`)**
    - `x-data x-init="$nextTick(() => $el.querySelector('input').focus())"` ensures that as soon as the form is rendered, the input field is focused for immediate typing. `$nextTick` is used to wait for the DOM to be fully updated by HTMX before attempting to focus.

4.  **Tailwind UI Button Groups**
    - The `isolate inline-flex rounded-md shadow-sm` classes create a professional, grouped button appearance.
    - Using SVG icons for actions (X, checkmark) with distinct `hover:` styles (`hover:bg-red-50`, `hover:bg-green-50`) provides clear visual feedback.

### 3.2 Dynamic Content Addition

**Adding New Pages to Story:**
```html
<!-- Add page button -->
<button hx-post="{% url 'add_page' story.id %}"
        hx-target="#pages-container"
        hx-swap="beforeend"
        class="btn btn-primary">
    Add New Page
</button>

<!-- Pages container -->
<div id="pages-container">
    {% for page in story.pages.all %}
        {% include 'stories/partials/page_item.html' %}
    {% endfor %}
</div>
```

**Backend:**
```python
def add_page(request, story_id):
    if request.htmx and request.method == 'POST':
        story = get_object_or_404(Story, id=story_id, user=request.user)
        page = Page.objects.create(
            story=story,
            title=f"Page {story.pages.count() + 1}",
            content="Click to edit content..."
        )
        return render(request, 'stories/partials/page_item.html', {
            'page': page
        })
    return HttpResponseBadRequest()
```

### 3.3 Form Handling with Crispy Forms

**Simple Form (|crispy filter):**
```html
<!-- For basic forms -->
{% load crispy_forms_tags %}
<form method="post">
    {% csrf_token %}
    {{ form|crispy }}
    <button type="submit" class="btn btn-primary">Save</button>
</form>
```

**Advanced Form ({% crispy %} tag):**
```python
# forms.py
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit

class StoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('title', css_class='text-lg font-semibold'),
            Field('description', rows=4),
            Submit('submit', 'Save Story', css_class='btn btn-primary')
        )
```

```html
<!-- Template -->
{% load crispy_forms_tags %}
{% crispy form %}
```

### 3.4 Loading States and Feedback

**HTMX Request Indicators:**
```html
<!-- Loading spinner -->
<button hx-post="/api/save" 
        hx-indicator="#spinner"
        class="btn btn-primary">
    Save
    <div id="spinner" class="htmx-indicator">
        <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24">
            <!-- spinner icon -->
        </svg>
    </div>
</button>

<!-- Global loading indicator -->
<div id="global-spinner" 
     class="htmx-indicator fixed top-4 right-4 bg-blue-500 text-white p-2 rounded">
    Loading...
</div>
<div hx-ext="loading-states" hx-indicator="#global-spinner">
    <!-- Your content -->
</div>
```

### 3.5 Alpine.js State Management

**Component State:**
```html
<div x-data="{ 
    isOpen: false, 
    items: @json($items),
    selectedItem: null 
}">
    <!-- Toggle button -->
    <button @click="isOpen = !isOpen" 
            class="btn btn-secondary">
        <span x-text="isOpen ? 'Close' : 'Open'"></span>
    </button>
    
    <!-- Conditional content -->
    <div x-show="isOpen" 
         x-transition
         class="mt-4 p-4 border rounded">
        <!-- List with selection -->
        <div x-for="item in items" :key="item.id">
            <button @click="selectedItem = item"
                    :class="selectedItem?.id === item.id ? 'bg-blue-100' : 'bg-white'"
                    class="block w-full text-left p-2 border rounded mb-2"
                    x-text="item.name">
            </button>
        </div>
        
        <!-- Selected item display -->
        <div x-show="selectedItem" x-transition>
            <h3 x-text="selectedItem?.name"></h3>
            <p x-text="selectedItem?.description"></p>
        </div>
    </div>
</div>
```

---

## 4. Security Best Practices

### 4.1 CSRF Protection
- **Always** include CSRF token in base template: `hx-headers='{"x-csrftoken": "{{ csrf_token }}"}'`
- Use `{% csrf_token %}` in all forms
- Validate HTMX requests with `request.htmx` check

### 4.2 Content Escaping
```html
<!-- Safe: Auto-escaped by Django -->
<p>{{ user_content }}</p>

<!-- Safe: Alpine.js auto-escapes -->
<p x-text="userContent"></p>

<!-- DANGEROUS: Never do this with user content -->
<p x-html="userContent"></p>
```

### 4.3 Input Validation
```python
# Always validate in views
def update_content(request):
    if request.htmx and request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if len(content) > 10000:  # Validate length
            return HttpResponseBadRequest("Content too long")
        # ... save content
```

---

## 5. Styling Guidelines

### 5.1 Tailwind Component Patterns
```html
<!-- Button styles -->
<button class="btn btn-primary">Primary Action</button>
<button class="btn btn-secondary">Secondary Action</button>

<!-- Card pattern -->
<div class="bg-white shadow-sm rounded-lg border p-6">
    <h3 class="text-lg font-semibold mb-4">Card Title</h3>
    <p class="text-gray-600">Card content</p>
</div>

<!-- Form field pattern -->
<div class="mb-4">
    <label class="block text-sm font-medium text-gray-700 mb-2">
        Field Label
    </label>
    <input type="text" 
           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
</div>
```

### 5.2 Responsive Design
```html
<!-- Mobile-first responsive -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <!-- Cards -->
</div>

<!-- Show/hide on different screens -->
<button class="md:hidden">Mobile Menu</button>
<nav class="hidden md:block">Desktop Nav</nav>
```

### 5.3 State-Based Styling
```html
<!-- Using Alpine.js for dynamic classes -->
<button :class="isActive ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'"
        @click="isActive = !isActive">
    Toggle
</button>

<!-- HTMX loading states -->
<form hx-post="/save" class="htmx-request:opacity-50">
    <!-- Form becomes semi-transparent during request -->
</form>
```

---

## 6. Common Patterns & Examples

### 6.1 Modal/Dialog
```html
<div x-data="{ open: false }">
    <button @click="open = true" class="btn btn-primary">
        Open Modal
    </button>
    
    <div x-show="open" 
         x-transition.opacity
         class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
         @click.self="open = false">
        <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 class="text-xl font-bold mb-4">Modal Title</h2>
            <p class="mb-4">Modal content</p>
            <div class="flex justify-end space-x-2">
                <button @click="open = false" class="btn btn-secondary">
                    Cancel
                </button>
                <button class="btn btn-primary">
                    Confirm
                </button>
            </div>
        </div>
    </div>
</div>
```

### 6.2 Auto-Save with Debouncing
```html
<div x-data="{ 
    content: '{{ page.content }}',
    saving: false,
    saveTimeout: null 
}">
    <textarea x-model="content"
              @input="
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(() => {
                    saving = true;
                    $refs.saveForm.requestSubmit();
                }, 1000)
              "
              class="w-full h-32 p-3 border rounded">
    </textarea>
    
    <form x-ref="saveForm" 
          hx-post="{% url 'update_page' page.id %}"
          hx-vals="js:{content: content}"
          @htmx:after-request="saving = false"
          style="display: none;">
    </form>
    
    <div x-show="saving" class="text-sm text-gray-500 mt-1">
        Saving...
    </div>
</div>
```

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
