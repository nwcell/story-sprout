# Ruff Usage Guide

**Ruff** is our code linter and formatter for the Story Sprout project. It enforces consistent code style and catches potential issues.

## Configuration

Ruff is configured in `pyproject.toml` with the following standards:
- **Line length**: 119 characters maximum
- **Docstring/comment length**: 79 characters maximum  
- **Auto-fixing**: Enabled by default
- **Quote style**: Double quotes
- **Import sorting**: Enabled with isort integration

## Daily Commands

### Check code without making changes
```bash
uv run ruff check
```

### Check and show what would be fixed
```bash
uv run ruff check --diff
```

### Check and auto-fix issues
```bash
uv run ruff check --fix
```

### Format code (auto-fix formatting issues)
```bash
uv run ruff format
```

### Check specific files or directories
```bash
uv run ruff check apps/stories/
uv run ruff check apps/stories/models.py
```

### Format specific files
```bash
uv run ruff format apps/stories/models.py
```

## IDE Integration

### Auto-format on save
Configure your IDE to run `uv run ruff format` on file save for automatic formatting.

### VS Code
Add to your VS Code settings.json:
```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": true,
      "source.organizeImports.ruff": true
    }
  }
}
```

## Pre-commit Hook (Optional)

To automatically run Ruff before each commit:

1. Install pre-commit:
```bash
uv add --dev pre-commit
```

2. Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.12.9
    hooks:
      - id: ruff
        args: [ --fix ]
      - id: ruff-format
```

3. Install the hook:
```bash
uv run pre-commit install
```

## Rules Overview

Ruff is configured with these rule sets:
- **E, W**: pycodestyle errors and warnings
- **F**: Pyflakes (unused imports, undefined variables)
- **UP**: pyupgrade (modern Python syntax)
- **B**: flake8-bugbear (common bugs and design problems)
- **SIM**: flake8-simplify (code simplification suggestions)
- **I**: isort (import sorting)

## Common Fixes

### Import Organization
Ruff automatically organizes imports in this order:
1. Standard library imports
2. Django core imports  
3. Third-party package imports
4. Local application imports

### Line Length
- Code lines: 119 characters max
- Docstrings/comments: 79 characters max
- Ruff will automatically wrap long lines where possible

### String Quotes
- Uses double quotes consistently
- Preserves existing quote style if changing would require escaping

## Running in CI/CD

For continuous integration, use:
```bash
# Check formatting (fail if not formatted)
uv run ruff format --check

# Check linting (fail if issues found)
uv run ruff check
```

## Best Practices

1. **Run before committing**: Always run `uv run ruff check --fix && uv run ruff format` before pushing code
2. **Fix issues promptly**: Don't accumulate lint violations
3. **Review auto-fixes**: While most fixes are safe, review changes before committing
4. **Use IDE integration**: Set up auto-format on save for the best experience
5. **Team consistency**: Everyone should use the same Ruff configuration

## Troubleshooting

### Issue: "No Python installation found"
**Solution**: Make sure you're using `uv run` prefix for all Ruff commands

### Issue: "Module not found"  
**Solution**: Run `uv sync` to ensure all dependencies are installed

### Issue: "Permission denied"
**Solution**: Check file permissions and ensure you're in the project directory

## Getting Help

- **Ruff documentation**: https://docs.astral.sh/ruff/
- **Configuration reference**: https://docs.astral.sh/ruff/configuration/
- **Rules reference**: https://docs.astral.sh/ruff/rules/
