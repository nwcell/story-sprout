---
trigger: always_on
---

# Story Sprout Coding Conventions

## General Principles

1. **Be Pythonic** - Follow [PEP 8](https://pep8.org/) and the [Zen of Python](https://peps.python.org/pep-0020/)
2. **Less is More** - Write minimal, readable code that solves the problem at hand
3. **Only Change What's Necessary** - Don't refactor or modify code unrelated to the task
4. **Make Meaningful Changes** - Every change should have a clear purpose

## Specific Guidelines

### Code Structure

- **Modules**: Keep modules focused on a single responsibility
- **Imports**: Group imports in the following order:
  1. Standard library imports
  2. Django core imports
  3. Third-party package imports
  4. Local application imports
- **File Size**: If a file exceeds 500 lines, consider breaking it up

### Naming Conventions

- **Variables**: Use `snake_case` for variables and functions
- **Classes**: Use `PascalCase` for class names
- **Constants**: Use `UPPER_SNAKE_CASE` for constants
- **Private Methods**: Prefix with underscore (`_method_name`)
- **Boolean Variables**: Use prefixes like `is_`, `has_`, `should_` 

### Django-Specific

- **Models**:
  - Field names should be clear and descriptive
  - Include `help_text` for complex fields
  - Always implement `__str__` method
  - Use Meta class for ordering and other options
  - Use descriptive `related_name` for relationships

- **Views**:
  - Use class-based views where appropriate
  - Keep view logic minimal, move complex logic to models or services
  - Name URL patterns clearly and consistently

- **Templates**:
  - Use template inheritance consistently
  - Keep template logic minimal
  - Use consistent naming for template blocks

- **Admin**:
  - Customize admin with appropriate list_display, search_fields
  - Use fieldsets for complex models

### Comments

- **When to Comment**:
  - Complex algorithms or business logic
  - Non-obvious code behavior
  - Public API documentation

- **When NOT to Comment**:
  - Obvious code
  - As a replacement for clear naming
  - To explain what the code does (vs. why it does it)
  - Commented-out code

- **Docstrings**:
  - Use docstrings for modules, classes, and functions
  - Follow [PEP 257](https://peps.python.org/pep-0257/)

### Code Edits

1. **Surgical Changes**:
   - Make precise changes that address specific requirements
   - Don't modify unrelated code just to "improve" it
   
2. **No Unnecessary Comments**:
   - Don't add comments that state the obvious
   - Don't add comments like `# Fixed issue` or `# Updated settings`

3. **Dependency Management**:
   - Use `uv` for all package management
   - Be specific about package versions in pyproject.toml

### Testing

- Write tests for new functionality
- Update tests when modifying existing functionality
- Follow AAA pattern (Arrange, Act, Assert)

## Code Quality Tools

- **Linting**: Use tools like Ruff, Flake8, or Pylint
- **Formatting**: Use Black for code formatting
- **Type Hints**: Use type hints where appropriate

## Version Control

- **Commit Messages**: Write clear, concise commit messages
- **Branch Names**: Use descriptive branch names for features/fixes

## Project-Specific Conventions

### Story Sprout Models

- Use `OrderedModel` from `django-ordered-model` for models that need ordering
- Implement proper `order_with_respect_to` for relationships
- Use UUIDs for public-facing identifiers
- Always include timestamps (`created_at`, `updated_at`)

### Error Handling

- Use explicit exception handling
- Provide meaningful error messages
- Log appropriate information for debugging

### Security

- Never hardcode sensitive information
- Use environment variables for configuration
- Follow Django's security best practices

---

**Remember**: Code is read much more often than it is written. Prioritize readability and maintainability over cleverness.