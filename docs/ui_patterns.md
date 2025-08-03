# Story Sprout UI Patterns

This document outlines the standardized UI patterns and component system for the Story Sprout application. It serves as a comprehensive guide for implementing consistent, maintainable, and accessible UI components across the application.

## 1. Architecture Overview

The UI system consists of several integrated layers:

1. **Template Components**: Reusable HTML fragments in `templates/components/`
2. **Django Template Tags**: Python-backed template helpers in `templatetags/ui_components.py`
3. **Base HTMX Views**: Core view classes that handle editable fields
4. **Tailwind CSS Components**: Standardized styling with `@apply` directives
5. **Django Forms with Crispy-Tailwind**: Form rendering and validation

## 2. Component Directory Structure

```
templates/
├── components/               # Shared components across apps
│   ├── editable_field.html   # Main editable field wrapper
│   ├── form_buttons/         # Button components
│   │   ├── save_button.html
│   │   ├── cancel_button.html
│   │   └── button_group.html
│   └── form_inputs/          # Input components
│       ├── text_input.html
│       └── textarea.html
└── stories/                  # App-specific templates
    ├── components/           # App-specific components
    │   ├── story_title_display.html
    │   ├── story_title_form.html
    │   ├── story_description_display.html
    │   └── story_description_form.html
    └── story_detail_new.html # Page using componentized approach
```

## 3. Editable Field Component

The core pattern for in-place editing throughout the application.

### 3.1 Template Tag Usage

```html
{% load ui_components %}

{% editable_field 
    instance 
    'field_name' 
    'edit_url_name' 
    'display_url_name' 
    editing=False 
    field_type='text'
    show_label=False 
%}
```

### 3.2 Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| instance | Object | (required) | Model instance to edit |
| field_name | String | (required) | Name of the model field |
| edit_url_name | String | (required) | URL name for edit view |
| display_url_name | String | (required) | URL name for display view |
| editing | Boolean | False | Whether to render in edit mode |
| field_type | String | 'text' | Input type ('text', 'textarea') |
| show_label | Boolean | False | Whether to show field label |
| placeholder | String | '' | Placeholder text for input |
| button_layout | String | 'row' | Button arrangement ('row', 'column') |
| has_magic | Boolean | False | Whether to show magic generate button |
| magic_url | String | None | URL for magic content generation |

### 3.3 Display Mode

- Rendered as clickable content with subtle hover effect
- HTMX attributes for switching to edit mode on click
- Optional label and styling based on field type

### 3.4 Edit Mode

- Renders appropriate input based on field_type
- HTMX-powered form for inline submission
- Consistent button layout with save/cancel actions
- Keyboard shortcuts for common actions

## 4. HTMX View Pattern

### 4.1 Base Classes

- `HtmxEditableFieldView`: Core class for editable fields
- `HtmxToggleView`: For boolean toggle fields

### 4.2 Specialized Views

```python
class StoryTitleEditView(HtmxEditableFieldView):
    model = Story
    form_class = StoryTitleForm
    display_template = 'stories/components/story_title_display.html'
    form_template = 'stories/components/story_title_form.html'
    field_name = 'title'
```

### 4.3 URL Configuration

```python
path('<uuid:story_uuid>/title/', StoryTitleDisplayView.as_view(), name='get_story_title'),
path('<uuid:story_uuid>/edit/title/', StoryTitleEditView.as_view(), name='edit_story_title'),
```

## 5. Form Handling

### 5.1 Django Forms

```python
class StoryTitleForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'text-2xl font-medium text-black uppercase tracking-wide w-full p-2',
                'placeholder': 'Enter story title...'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('title', css_class='form-input-base')
        )
```

### 5.2 Form Templates

```html
<form hx-post="{% url update_url %}" 
      hx-swap="outerHTML" 
      hx-trigger="submit, blur from:input, keydown[key=='Enter'] from:body"
      x-data
      x-init="$nextTick(() => $el.querySelector('input').focus())">
      
    <!-- Input field -->
    
    <!-- Button group -->
    {% form_button_group cancel_url=cancel_url %}
</form>
```

## 6. Styling System

### 6.1 Component Classes

Using `@apply` directives in `static/css/components.css`:

```css
/* Base Input Styles */
.form-input-base {
  @apply w-full px-4 py-2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-200 focus:ring-opacity-50;
}

/* Button Styles */
.btn {
  @apply inline-flex items-center justify-center px-4 py-2 rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors;
}

.btn-primary {
  @apply btn bg-black text-white hover:bg-gray-800 focus:ring-black;
}
```

### 6.2 Custom Tailwind Config

Extending the theme in `tailwind.config.js`:

```js
theme: {
  extend: {
    colors: {
      'gray': '#6B7280',
      'light-gray': '#E5E7EB',
      'dark-gray': '#4B5563',
      'black': '#1F2937',
      'white': '#FFFFFF',
    },
    animation: {
      'fade-in': 'fadeIn 0.3s ease-in',
      'slide-down': 'slideDown 0.3s ease-out',
    },
  }
}
```

## 7. Implementation Workflow

### 7.1 Creating a New Editable Field

1. Create Django form class for the field
2. Create specialized HTMX view classes
3. Add URL patterns for the views
4. Create display and form templates
5. Include the component in the page template

### 7.2 Example: Title Field

```python
# 1. Form
class StoryTitleForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['title']
        
# 2. View
class StoryTitleEditView(HtmxEditableFieldView):
    model = Story
    form_class = StoryTitleForm
    display_template = 'stories/components/story_title_display.html'
    form_template = 'stories/components/story_title_form.html'
    field_name = 'title'
    
# 3. URLs
path('<uuid:story_uuid>/title/', StoryTitleDisplayView.as_view(), name='get_story_title'),
path('<uuid:story_uuid>/edit/title/', StoryTitleEditView.as_view(), name='edit_story_title'),

# 4. Templates
# display_template.html
{% editable_field story 'title' 'stories:edit_story_title' 'stories:get_story_title' %}

# 5. Page inclusion
{% include 'stories/components/story_title_display.html' with story=story %}
```

## 8. Keyboard Shortcuts & Accessibility

### 8.1 Standard Keyboard Controls

- **Enter**: Submit form (input fields)
- **Cmd/Ctrl + Enter**: Submit form (textarea fields)
- **Escape**: Cancel editing
- **Tab**: Navigate between form elements

### 8.2 Accessibility Features

- Proper focus management
- ARIA attributes
- Visible focus states
- Keyboard navigation
- Screen reader friendly markup

## 9. Best Practices

1. **Consistent Structure**: Follow the established pattern for all editable fields
2. **Reuse Components**: Leverage existing components rather than creating new ones
3. **Template Tags**: Use template tags to encapsulate complex rendering logic
4. **Styling**: Use component classes from `components.css` rather than inline styles
5. **Validation**: Include proper form validation with clear error messages
6. **Documentation**: Document any new components or patterns in this guide

## 10. Example Implementation

The story detail view demonstrates the complete implementation of the componentized approach:

- Title field uses `editable_field` with text input
- Description field uses `editable_field` with textarea
- Both leverage Django forms, HTMX views, and template components
- Consistent styling through Tailwind component classes

This standardized approach ensures consistency, reduces code duplication, and improves maintainability across the application.
