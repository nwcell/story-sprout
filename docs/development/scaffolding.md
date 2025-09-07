# Project Scaffolding and Core Libraries

This document provides an overview of the core libraries and scaffolding used in the Story Sprout project. Understanding these components is crucial for effective development.

## `django-cotton`

`django-cotton` brings a component-based design approach to our Django templates, allowing us to create reusable UI components with a clean, declarative syntax similar to modern JavaScript frameworks. This helps us build a decoupled, maintainable, and highly reusable frontend.

### Key Concepts

- **Component-Based:** Instead of relying heavily on `{% include %}` and `{% extends %}`, we can create self-contained components (e.g., `<c-button>`, `<c-card>`) that encapsulate both structure and logic.
- **Custom Loader:** Cotton uses a custom template loader (`django_cotton.cotton_loader.Loader`) that compiles these components into standard Django template syntax on the fly. This process is cached for performance.
- **Props and Slots:** We can pass data to components using attributes (props) and render child content using a default `{{ slot }}` variable, making them flexible and composable.

### Example

A simple button component might look like this:

A button component is typically defined in its own directory, such as `templates/cotton/button/`.
```html
<button class="bg-blue-500 text-white font-bold py-2 px-4 rounded">
    {{ slot }}
</button>
```

**Usage in a template:**
```html
{% load cotton %}

<c-button>
    Click Me
</c-button>
```

