# Story Sprout UI Simplification Project

**Date:** 2025-08-02  
**Updated:** 2025-08-02  
**Goal:** Simplify UI and form management to avoid "spaghetti code"

## Table of Contents
1. [Problem Statement](#problem-statement)
2. [Solution Overview](#solution-overview)
3. [Implementation Strategy](#implementation-strategy)
4. [Component Templates](#component-templates)
5. [Abstracted Tailwind Classes](#abstracted-tailwind-classes)
6. [HTMX State Variants](#htmx-state-variants)
7. [Django Form Integration](#django-form-integration)
8. [Backend View Patterns](#backend-view-patterns)
9. [Implementation Timeline](#implementation-timeline)
10. [Reference Examples](#reference-examples)

## Problem Statement

The current UI and form management approach:
- Has a lot of duplication across multiple partial templates
- Complex HTMX and Alpine.js logic is repeated in several places
- Tailwind classes lead to very long HTML attributes
- Growing complexity as more features are added

## Solution Overview

A comprehensive approach to simplify UI management through:
1. Extracting reusable template fragments (buttons, textareas, etc.)
2. Using unified component templates for both display and edit modes
3. Using Django forms and crispy-tailwind for consistent rendering and validation
4. Implementing a component system for editable fields
5. Standardizing backend HTMX view patterns
6. Using abstracted Tailwind classes and HTMX state variants
7. Organizing and documenting all UI patterns

## Implementation Strategy

### Directory Structure

```
templates/
├── base.html
├── components/
│   ├── form_buttons/
│   │   ├── save_button.html
│   │   ├── cancel_button.html
│   │   └── button_group.html
│   └── form_inputs/
│       ├── textarea.html
│       └── text_input.html
├── stories/
│   ├── components/  # Unified templates (display+edit modes)
│   │   ├── story_title.html
│   │   ├── story_description.html
│   │   └── page_content.html
│   └── partials/    # Other partial templates
static/
└── css/
    └── components.css  # Tailwind component classes
apps/
├── core/
│   └── views.py     # Base HTMX view classes
└── stories/
    ├── forms.py     # Django forms
    ├── views.py     # View implementations
    ├── htmx_views.py # HTMX-specific view implementations
    └── urls.py      # URL patterns
```

## Component Templates

### Unified Editable Field Pattern

The core of our UI approach is the unified editable field pattern. This component handles both display and edit modes in a single template, controlled by a `mode` parameter:

```html
{% if mode == 'edit' %}
    {# Edit Mode with form #}
    <form hx-post="{{ url }}"
          hx-target="this"
          hx-swap="outerHTML"
          hx-trigger="submit, keydown[metaKey&&key=='Enter'] from:body, keydown[ctrlKey&&key=='Enter'] from:body, blur from:textarea"
          class="hover:bg-gray-50 p-2 rounded transition-colors">
        <!-- Form content -->        
    </form>
{% else %}
    {# Display Mode with click-to-edit #}
    <div id="{{ field_name }}" 
         hx-get="{{ url }}?mode=edit" 
         hx-trigger="click"
         hx-target="this"
         hx-swap="outerHTML"
         class="cursor-pointer hover:bg-gray-50 p-2 rounded transition-colors group">
        <!-- Display content -->
    </div>
{% endif %}
```

### Implementation Methods

There are two ways to use this pattern in our application:

#### 1. Generic Editable Field Component

For simple editable fields (like descriptions, titles), use the reusable component:

```html
{% url 'stories:edit_story_description' story.uuid as desc_url %}
{% include "components/editable_field.html" with 
    field_name="description" 
    value=story.description 
    label="Description" 
    placeholder="Click to add a description" 
    url=desc_url 
    mode=mode %}
```

#### 2. Custom Complex Components

For components with specialized behavior (like page content with AI generation), create custom component templates that follow the same pattern but with added functionality:

```html
{# page_content.html #}
{% if mode == 'edit' %}
    {# Custom edit mode with AI buttons #}
{% else %}
    {# Custom display mode with specialized styling #}
{% endif %}
```

### Example: Components With Abstracted Classes

Using abstracted Tailwind classes from `components.css` simplifies templates and makes them more maintainable:

```html
<!-- Save button with abstracted classes -->
<button type="submit"
        @mousedown.prevent
        class="btn-success btn-sm"
        title="Save (Ctrl+Enter)">
    <svg class="icon-sm" viewBox="0 0 20 20">
        <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
    </svg>
</button>

<!-- Textarea with abstracted classes -->
<textarea name="content"
          rows="4"
          class="form-textarea"
          placeholder="Enter content..."
          x-init="$el.focus()">{{ content }}</textarea>
```

## Abstracted Tailwind Classes

Tailwind classes are abstracted in `components.css` to promote consistency and reduce duplication:

```css
/* Form Controls */
.form-textarea {
  @apply w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray resize-none flex-grow;
}

.form-input {
  @apply w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray;
}

/* Buttons */
.btn-primary {
  @apply inline-flex items-center px-4 py-2 bg-blue-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-blue-700 focus:bg-blue-700 active:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition ease-in-out duration-150;
}

.btn-success {
  @apply inline-flex items-center justify-center rounded-t-md bg-white p-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-green-50 hover:text-green-600 focus:z-10;
}

.btn-secondary {
  @apply relative -mt-px inline-flex items-center justify-center rounded-b-md bg-white p-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-red-50 hover:text-red-600 focus:z-10;
}

/* Button Sizes */
.btn-sm {
  @apply p-2;
}

.btn-md {
  @apply px-4 py-2;
}

/* Icons */
.icon-sm {
  @apply h-5 w-5;
}
```

## HTMX State Variants

We use HTMX state variants to provide visual feedback during AJAX requests. These are configured in the Tailwind CDN setup in `base.html`:

```html
<script>
  tailwind.config = {
    theme: {
      extend: {
        opacity: {
          '15': '0.15',
        },
        backgroundColor: {
          'loading': '#f9fafb',
        },
      },
      variants: {
        extend: {
          // HTMX state variants
          opacity: ['htmx-request', 'htmx-settling', 'htmx-indicator'],
          backgroundColor: ['htmx-request', 'htmx-settling'],
          cursor: ['htmx-request'],
          display: ['htmx-indicator'],
          scale: ['htmx-request'],
        }
      },
    }
  }
</script>
```

Usage examples:

```html
<!-- Element dims during HTMX request -->  
<div class="htmx-request:opacity-50">
    Content that dims during loading
</div>

<!-- Loading indicator that only shows during request -->
<div class="htmx-indicator opacity-0 htmx-request:opacity-100 transition-opacity">
    <div class="spinner"></div>
</div>
```
            
            <textarea name="description" 
                      rows="4"
                      class="form-textarea"
                      placeholder="Enter story description..."
                      x-init="$el.focus()">{{ form.description.value|default:story.description }}</textarea>
            
            <!-- Button Group -->
            <div class="btn-group-col">
                <button type="submit" @mousedown.prevent class="btn-success btn-sm" title="Save (Ctrl+Enter)">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>
                </button>
                <button type="button" @mousedown.prevent class="btn-secondary btn-sm" title="Cancel (Esc)"
                        hx-get="{% url 'stories:get_story_description' story.uuid %}"
                        hx-target="closest form"
                        hx-swap="outerHTML">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                </button>
            </div>
        </div>
        <div class="text-xs text-gray-500 mt-1">Ctrl+Enter to save, Escape to cancel, or use the buttons.</div>
    </form>
{% else %}
    {# Display Mode #}
    <div id="story-description" 
         hx-get="{% url 'stories:editable_story_description' story.uuid %}?mode=edit" 
         hx-trigger="click"
         hx-target="this"
         hx-swap="outerHTML"
         class="editable-field group">
        <h3 class="card-title">
            Description
            <i class="fa-solid fa-pen-to-square text-sm text-gray-400 ml-2 edit-icon"></i>
        </h3>
        <div class="prose max-w-none">
            {% if value|default:story.description %}
                {{ value|default:story.description|linebreaks }}
            {% else %}
                <p class="text-gray-400 italic">Click to add a description</p>
            {% endif %}
        </div>
    </div>
{% endif %}
```

## Unified Template Pattern

The unified template pattern combines display and edit modes in a single template file, controlled by a `mode` parameter. This approach eliminates duplication and creates a clear relationship between display and edit views.

### Core Principles

1. **Single Responsibility**: Each template handles both display and edit modes for one specific element
2. **Mode Switching**: HTMX handles transitions between modes via `hx-get` and `hx-post`
3. **Self-Contained**: Templates include all necessary markup, styles, and behaviors
4. **Consistent Structure**: All unified templates follow the same conditional pattern

### Standard Structure

```html
{% if mode == 'edit' %}
    {# Edit Mode #}
    <form hx-post="{% url 'endpoint' object.id %}"  
          hx-target="this"
          hx-swap="outerHTML"
          hx-trigger="submit, keydown[metaKey&&key=='Enter'] from:body, blur from:textarea">
        <!-- Form fields go here -->
        <!-- Button group for actions -->
    </form>
{% else %}
    {# Display Mode #}
    <div hx-get="{% url 'endpoint' object.id %}?mode=edit" 
         hx-trigger="click"
         hx-target="this"
         hx-swap="outerHTML">
        <!-- Display content here -->
    </div>
{% endif %}
```

### Common HTMX Patterns

1. **Click-to-Edit**: Display mode elements trigger edit mode on click
2. **Submit Handling**: Forms handle standard submit, keyboard shortcuts, and blur events
3. **Cancel Action**: Cancel buttons restore display mode via HTMX GET request
4. **Validation**: Server-side validation with error display
5. **Form Focus**: Alpine.js handles auto-focus when entering edit mode

## Tailwind CSS Implementation

### Current Setup: CDN with Inline Configuration

The project currently uses Tailwind CSS via CDN with inline configuration in `base.html`. This approach offers simplicity and quick iteration without requiring a build step.

```html
<script src="https://cdn.tailwindcss.com"></script>
<script>
  tailwind.config = {
    theme: {
      extend: {
        /* Custom theme extensions */
      },
      variants: {
        extend: {
          /* HTMX state variants */
        }
      },
    }
  }
</script>
```

### Benefits of Current Approach

1. **Simple Development**: No build step required
2. **Easy Prototyping**: Changes take effect instantly
3. **Minimal Configuration**: No separate config files to manage
4. **Reduced Dependencies**: No Node.js or npm dependencies

### Limitations of Current Approach

1. **Performance**: The full Tailwind library is loaded by the browser
2. **Limited Plugin Support**: Some plugins may not be available via CDN
3. **No Tree-Shaking**: Unused CSS isn't removed
4. **Limited Custom Configuration**: Some advanced features require a build process

### Future Considerations: Build Process

If needed, the project could migrate to a build process setup with the following steps:

1. **Setup Node.js and npm**
2. **Install Tailwind CSS and dependencies**
3. **Create a proper `tailwind.config.js` file**
4. **Set up a build pipeline (postcss, webpack, etc.)**
5. **Replace CDN link with compiled CSS file**

However, the current CDN approach is sufficient for the project's needs at this stage, providing the right balance of simplicity and functionality.

## Tailwind Components

### Create `static/css/components.css`

```css
/* Form Components */
@layer components {
  /* Text Inputs */
  .form-input-base {
    @apply border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200;
  }
  
  .form-textarea {
    @apply form-input-base w-full p-3 bg-white text-gray resize-none flex-grow;
  }
  
  .form-text-input {
    @apply form-input-base w-full p-2;
  }
  
  /* Button System */
  .btn {
    @apply relative inline-flex items-center justify-center p-2 text-gray-400 ring-1 ring-inset ring-gray-300 focus:z-10 transition-all duration-200;
  }
  
  .btn-save {
    @apply btn rounded-t-md hover:bg-green-50 hover:text-green-600;
  }
  
  .btn-cancel {
    @apply btn -mt-px hover:bg-red-50 hover:text-red-600;
  }
  
  .btn-action {
    @apply btn -mt-px rounded-b-md hover:bg-blue-50 hover:text-blue-600;
  }
  
  /* Status and State Classes */
  .disabled-blur {
    @apply opacity-50 cursor-not-allowed;
  }
  
  /* Card and Container Styles */
  .story-card {
    @apply bg-white shadow rounded-lg p-4 border border-gray-200;
  }
  
  .section-container {
    @apply my-4 p-4 bg-white rounded-lg shadow;
  }
}
```

### Update `tailwind.config.js`

```javascript
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        'story-primary': '#3b82f6',
        'story-accent': '#10b981',
        'story-warning': '#f59e0b',
        'story-error': '#ef4444',
      },
      animation: {
        'twinkle': 'twinkle 1.5s ease-in-out infinite',
        'spin-slow': 'spin 3s linear infinite',
      },
      keyframes: {
        twinkle: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
      },
      borderRadius: {
        'input': '0.375rem',
      }
    },
  },
  plugins: [
    function({ addVariant }) {
      // HTMX specific variants
      addVariant('htmx-requesting', '.htmx-request &');
      addVariant('htmx-settling', '.htmx-settling &');
      
      //## HTMX State Variants

HTMX automatically adds classes to elements during AJAX operations that we can target with Tailwind variants to provide visual feedback to users.

### Key HTMX States

1. **htmx-request**: Applied during an ongoing request
2. **htmx-settling**: Applied when content is being swapped in
3. **htmx-indicator**: Used with custom loading indicators

### Tailwind Configuration

In `tailwind.config.js`, add custom variants to target these states:

```javascript
module.exports = {
  // ... other config
  plugins: [
    function({ addVariant }) {
      // HTMX specific variants
      addVariant('htmx-requesting', '.htmx-request &');
      addVariant('htmx-settling', '.htmx-settling &');
      addVariant('htmx-indicator', '.htmx-request.htmx-indicator &, .htmx-request .htmx-indicator &');
      
      // Parent state variants for group hover effects
      addVariant('parent-hover', '.parent:hover &');
      addVariant('parent-focus', '.parent:focus &');
    },
  ],
}
```

### Usage in Templates

With these variants configured, we can add visual feedback to our components:

```html
<!-- Loading indicator that appears during HTMX requests -->
<div class="htmx-indicator opacity-0 htmx-requesting:opacity-100 transition-opacity">
  <svg class="animate-spin h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
  </svg>
</div>

<!-- Form that dims during submission -->
<form hx-post="/endpoint"
      class="transition-opacity duration-200 htmx-requesting:opacity-50">
  <!-- Form contents -->
</form>

<!-- Button with loading state -->
<button hx-post="/endpoint"
        class="btn-primary relative">
  <span class="htmx-requesting:invisible">Save Changes</span>
  <span class="htmx-indicator absolute inset-0 flex items-center justify-center">
    <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
  </span>
</button>
```
      addVariant('form-disabled', '&.disabled, &[disabled]');
      addVariant('form-invalid', '&.is-invalid');
      
      // Parent state variants
      addVariant('parent-hover', '.parent:hover &');
      addVariant('parent-focus', '.parent:focus &');
    },
  ],
}
```

## Django Form Integration

### Create or extend in `apps/stories/forms.py`:

```python
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from .models import Page

class PageContentForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'rows': 6,
                    'placeholder': 'Enter page content...',
                    'class': 'form-textarea',
                }
            )
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('content', wrapper_class='w-full'),
        )

class PageImageTextForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['image_text']
        widgets = {
            'image_text': forms.Textarea(
                attrs={
                    'rows': 6,
                    'placeholder': 'Enter image text...',
                    'class': 'form-textarea',
                }
            )
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
```

### Global CSRF Protection

For CSRF protection with HTMX, we use a global approach instead of including the CSRF token in each form:

```html
{% load django_htmx %}
<html>
<head>
    <!-- Load HTMX script via template tag -->
    {% htmx_script %}
</head>
<body hx-headers='{"x-csrftoken": "{{ csrf_token }}"}'>  <!-- Global CSRF token -->
    <!-- Page content -->
</body>
</html>
```

With this global approach, NEVER include `{% csrf_token %}` directly in forms when using HTMX.

### Unified View Pattern

The backend view handles both display and edit modes in a single class:

## Backend View Patterns

### Create in `apps/core/views.py`:

```python
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
    
    def post(self, request, pk):
        """Toggle the boolean field value"""
        obj = get_object_or_404(self.model, pk=pk)
        current_value = getattr(obj, self.field_name)
        setattr(obj, self.field_name, not current_value)
        obj.save()
        
        return render(request, self.template_name, {'object': obj})
```

### Implement in `apps/stories/views.py`:

```python
from apps.core.views import HtmxEditableFieldView, HtmxToggleView
from .models import Page
from .forms import PageContentForm, PageImageTextForm

class PageContentEditView(HtmxEditableFieldView):
    model = Page
    form_class = PageContentForm
    display_template = 'stories/partials/page_content.html'
    form_template = 'stories/partials/page_content_form.html'
    field_name = 'content'

class PageImageTextEditView(HtmxEditableFieldView):
    model = Page
    form_class = PageImageTextForm
    display_template = 'stories/partials/page_image_text.html'
    form_template = 'stories/partials/page_image_text_form.html'
    field_name = 'image_text'

class PageContentDisplayView(View):
    def get(self, request, pk):
        page = get_object_or_404(Page, pk=pk)
        return render(request, 'stories/partials/page_content.html', {'page': page})

class PageImageTextDisplayView(View):
    def get(self, request, pk):
        page = get_object_or_404(Page, pk=pk)
        return render(request, 'stories/partials/page_image_text.html', {'page': page})

class ToggleContentGeneratingView(HtmxToggleView):
    model = Page
    field_name = 'content_generating'
    template_name = 'stories/partials/page_content_form.html'
```

## URL Configuration

### Update `apps/stories/urls.py`:

```python
from django.urls import path
from . import views

app_name = 'stories'

urlpatterns = [
    # Existing URLs...
    
    # HTMX editable field URLs
    path('pages/<int:pk>/content/', views.PageContentEditView.as_view(), name='edit_page_content'),
    path('pages/<int:pk>/content/display/', views.PageContentDisplayView.as_view(), name='get_page_content'),
    path('pages/<int:pk>/image-text/', views.PageImageTextEditView.as_view(), name='edit_page_image_text'),
    path('pages/<int:pk>/image-text/display/', views.PageImageTextDisplayView.as_view(), name='get_page_image_text'),
    
    # HTMX toggle URLs
    path('pages/<int:pk>/toggle-generating/', views.ToggleContentGeneratingView.as_view(), name='toggle_content_generating'),
    path('pages/<int:pk>/check-generating/', views.CheckContentGeneratingStatusView.as_view(), name='check_content_generating_status'),
]
```

## Refactoring Templates

### Simplified `templates/stories/partials/page_image_text_form.html`:

```html
{% load ui_components %}

<!-- Page image text edit form -->
{% editable_field page 'image_text' 'stories:edit_page_image_text' 'stories:get_page_image_text' %}
```

### Simplified `templates/stories/partials/page_content_form.html`:

```html
{% load ui_components %}

<!-- Editable content form -->
{% editable_field page 'content' 'stories:edit_page_content' 'stories:get_page_content' disabled=page.content_generating show_magic=True is_generating=page.content_generating %}
```

### Using the Unified Pattern

#### 1. Create a unified template with conditional rendering

Create a template (e.g., `story_title.html`) that handles both display and edit modes:

```html
{% if mode == 'edit' %}
    <!-- Edit form -->  
{% else %}
    <!-- Display content -->
{% endif %}
```

#### 2. Create a view class that inherits from HtmxEditableFieldView

```python
class EditableStoryTitleView(HtmxEditableFieldView):
    model = Story
    form_class = StoryTitleForm
    template_name = 'stories/components/story_title.html'
    field_name = 'title'
```

#### 3. Configure URL pattern for the unified endpoint

```python
path('<uuid:story_uuid>/title/editable/', 
     htmx_views.EditableStoryTitleView.as_view(), 
     name='editable_story_title'),
```

#### 4. Include the template in your page

```html
{% include 'stories/components/story_title.html' with story=story %}
```

## Implementation Timeline

1. **Phase 1 (Days 1-2)**: Extract common components into templates
   - Create component directory structure
   - Create button and input component templates

2. **Phase 2 (Days 3-4)**: Create Django template tags and component templates
   - Implement ui_components template tags
   - Create editable_field master template

3. **Phase 3 (Days 5-6)**: Implement Tailwind styling and configuration
   - Create components.css with @apply directives
   - Update tailwind.config.js with theme extensions

4. **Phase 4 (Days 7-8)**: Integrate Django forms with crispy-tailwind
   - Create model forms for each editable field
   - Configure crispy-tailwind to style forms consistently

5. **Phase 5 (Days 9-10)**: Create backend view patterns
   - Implement base HTMX view classes
   - Create views for each editable field

6. **Phase 6 (Day 11)**: Update URLs
   - Configure URL patterns for new views

7. **Phase 7 (Days 12-13)**: Refactor existing templates
   - Update all partial templates to use new components

8. **Phase 8 (Day 14)**: Document all patterns
   - Create comprehensive documentation of UI patterns

## Reference Examples

### Example: In-Place Editing

Before simplification:
```html
<div hx-get="/edit/1/" hx-trigger="click" hx-swap="outerHTML">
    Some content
</div>

<!-- When clicked becomes: -->
<form hx-post="/save/1/" hx-swap="outerHTML" class="flex items-center space-x-2">
    <input name="value" value="Some content" class="form-input">
    <button>✓</button>
</form>
```

After simplification:
```html
{% load ui_components %}
{% editable_field obj 'content' 'edit_view' 'display_view' %}
```

### Example: Button Group

Before simplification:
```html
<span class="isolate inline-flex flex-col rounded-md shadow-sm">
    <!-- Save Button -->
    <button type="submit" @mousedown.prevent class="relative inline-flex items-center justify-center rounded-t-md bg-white p-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-green-50 hover:text-green-600 focus:z-10">
        <svg>...</svg>
    </button>
    <!-- Cancel Button -->
    <button type="button" @mousedown.prevent class="relative -mt-px inline-flex items-center justify-center bg-white p-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-red-50 hover:text-red-600 focus:z-10" hx-get="...">
        <svg>...</svg>
    </button>
</span>
```

After simplification:
```html
{% include "components/form_buttons/button_group.html" with get_url=url %}
```
