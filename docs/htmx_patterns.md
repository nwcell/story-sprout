# HTMX View Patterns for Story Sprout

This document outlines the standardized patterns for HTMX interactions in the Story Sprout application, with a focus on editable field components.

## 1. Base Classes

### 1.1. `HtmxEditableFieldView`

The core class that handles both displaying and editing a single field in a model. All editable field views should inherit from this base class.

```python
class HtmxEditableFieldView(View):
    model = None              # Model class (required)
    form_class = None         # Django form class (optional)
    display_template = None   # Template to render for display mode
    form_template = None      # Template to render for edit mode
    field_name = None         # Model field name to update
```

#### Key Features:

- **Object Lookup**: Supports both primary key (`pk`) and UUID (`story_uuid`) lookup
- **Security**: Automatically checks ownership (user field or related story's user)
- **GET Request**: Shows the edit form
- **POST Request**: Updates the field and returns to display mode
- **HTMX Detection**: Only responds to HTMX requests

### 1.2. `HtmxToggleView`

For handling boolean toggle fields (e.g., checkboxes, switches).

```python
class HtmxToggleView(View):
    model = None              # Model class (required)
    template_name = None      # Template to render after toggle
    field_name = None         # Boolean field to toggle
```

## 2. Implementation Pattern

### 2.1. Create a Specialized View

```python
class StoryTitleEditView(HtmxEditableFieldView):
    model = Story
    form_class = StoryTitleForm
    display_template = 'stories/components/story_title_display.html'
    form_template = 'stories/components/story_title_form.html'
    field_name = 'title'
```

### 2.2. Register URL Patterns

```python
path('<uuid:story_uuid>/title/', StoryTitleDisplayView.as_view(), name='get_story_title'),
path('<uuid:story_uuid>/edit/title/', StoryTitleEditView.as_view(), name='edit_story_title'),
```

### 2.3. Create Templates

Create matching display and form templates:

```html
<!-- Display template -->
{% load ui_components %}

{% editable_field story 'title' 'stories:edit_story_title' 'stories:get_story_title' editing=False %}
```

```html
<!-- Form template -->
{% load ui_components %}

{% editable_field story 'title' 'stories:edit_story_title' 'stories:get_story_title' editing=True %}
```

## 3. Component Template Tag Usage

### 3.1. Basic Usage

```html
{% editable_field instance 'field_name' 'edit_url_name' 'display_url_name' %}
```

### 3.2. Optional Parameters

- `editing`: Boolean, whether to show in edit mode (default: False)
- `field_type`: String, input type to use (default: 'text', options: 'text', 'textarea')
- `show_label`: Boolean, whether to show field label (default: False)
- `placeholder`: String, placeholder text for input
- `button_layout`: String, button arrangement (default: 'row', options: 'row', 'column')
- `has_magic`: Boolean, whether to show magic generate button (default: False)
- `magic_url`: String, URL for magic content generation endpoint

### 3.3. Button Group Tag

```html
{% form_button_group cancel_url='stories:get_story_title' has_magic=True magic_url='...' %}
```

## 4. Styling Conventions

### 4.1. Display Mode

- Clear hover state for clickable fields
- Appropriate padding and typography
- Visual indicator that field is editable (faint outline, icon, etc.)

### 4.2. Form Mode

- Consistent styling for inputs and textareas
- Clear focus state
- Consistent button styling and positioning

## 5. HTMX Attributes

### 5.1. Display Element (to trigger edit)

```html
hx-get="{% url 'edit_url' object.id %}"
hx-trigger="click"
hx-swap="outerHTML"
```

### 5.2. Form Element (for submission)

```html
hx-post="{% url 'edit_url' object.id %}"
hx-swap="outerHTML"
```

### 5.3. Form Triggers

- **Save**: `submit, keydown[metaKey&&key=='Enter'] from:body` (textarea)
- **Save**: `submit, blur from:input, keydown[key=='Enter'] from:body` (input)
- **Cancel**: `click` on cancel button

## 6. Best Practices

1. **Use Base Classes**: Always extend the base HTMX views rather than creating custom views
2. **Security First**: Ensure ownership checks are in place
3. **Consistent Templates**: Follow the same pattern for all editable fields
4. **Keyboard Support**: Maintain consistent keyboard shortcuts
5. **Error Handling**: Add appropriate form validation and error display
6. **Focus Management**: Ensure proper focus behavior with Alpine.js
7. **Accessibility**: Maintain ARIA attributes and keyboard navigation

## 7. Example Workflow

1. User clicks on editable field
2. HTMX sends GET request to the edit view
3. Edit view returns form template
4. User edits and submits (or cancels)
5. HTMX sends POST request to the same view
6. View processes the form and returns display template with updated data

This standardized approach ensures consistency, reduces code duplication, and improves maintainability across the application.
