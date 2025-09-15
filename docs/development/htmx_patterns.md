# HTMX and Cotton Component Patterns for Story Sprout

This document outlines the standardized patterns for HTMX interactions in the Story Sprout application, using Django Cotton components for reusable UI elements.

## 1. Cotton Component Architecture

Story Sprout uses Django Cotton components for reusable UI elements that integrate seamlessly with HTMX for dynamic interactions.

### 1.1. Cotton Component Structure

Cotton components are located in `templates/cotton/` and follow this pattern:

```
templates/cotton/
├── stories/
│   ├── title.html          # Story title component
│   ├── description.html    # Story description component
│   └── page/
│       ├── content.html    # Page content component
│       └── image_text.html # Page image text component
├── fields/
│   ├── input.html          # Input field component
│   └── textarea.html       # Textarea field component
└── button/
    ├── save.html           # Save button component
    └── cancel.html         # Cancel button component
```

### 1.2. Component Props and Slots

Cotton components use props for configuration and slots for content:

```html
<!-- Example: Using the input field component -->
<c-fields.input
    name="title"
    value="{{ story.title }}"
    placeholder="Enter story title"
    hx-post="{% url 'stories:update_title' story.uuid %}"
    hx-trigger="blur"
/>
```

## 2. HTMX Integration Patterns

### 2.1. Inline Editing with Cotton Components

Cotton components can be enhanced with HTMX attributes for inline editing:

```html
<!-- In your template -->
<c-stories.title
    story="{{ story }}"
    hx-get="{% url 'stories:edit_title' story.uuid %}"
    hx-trigger="click"
    hx-swap="outerHTML"
/>
```

### 2.2. Form Submission Pattern

```html
<!-- Cotton component with HTMX form -->
<c-fields.input
    name="title"
    value="{{ story.title }}"
    hx-post="{% url 'stories:update_title' story.uuid %}"
    hx-trigger="blur, keydown[key=='Enter']"
    hx-swap="outerHTML"
/>
```

### 2.3. Real-time Updates with SSE

Components can listen for Server-Sent Events for real-time updates:

```html
<c-htmx.sse
    channel="story-{{ story.uuid }}"
    events="story.updated"
    hx-get="{% url 'stories:get_story' story.uuid %}"
/>
```

## 3. Common Patterns

### 3.1. AI-Enhanced Fields

Many components include AI generation capabilities:

```html
<c-stories.description
    story="{{ story }}"
    magic_url="{% url 'ai:generate_description' story.uuid %}"
/>
```

### 3.2. Modal Integration

Cotton components work with modal dialogs:

```html
<c-modal
    id="story-settings"
    title="Story Settings"
>
    <c-stories.detail story="{{ story }}" />
</c-modal>
```

### 3.3. Button Components

Standardized button components for consistent styling:

```html
<c-button.save
    hx-post="{% url 'stories:save' story.uuid %}"
    hx-trigger="click"
/>

<c-button.cancel
    hx-get="{% url 'stories:detail' story.uuid %}"
    hx-target="#content"
/>
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
