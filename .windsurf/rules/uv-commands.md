---
trigger: always_on
description: When executing commands, that impact uv, django, or python
---

# Working with UV

**Objective:** Every Python or Django command executed by Wave **must** go through **uv**—never directly through `python`, `pip`, or `virtualenv`.

---

## 1. Install `uv` (once per machine)

> **Run this only if `uv` is not already installed.**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```


## 2. Command-Rewrite Mapping

Wave must transform each legacy command into its uv equivalent before execution:

| Legacy Command | uv Equivalent | Description |
|---|---|---|
| `python <script.py>` | `uv run <script.py>` | Runs inside the project's virtual-env and auto-syncs dependencies |
| `python -m module …` | `uv run -m module …` | Same as above, module form |
| `python manage.py …` or `django-admin …` | `uv run manage.py …` | Single entry point for Django |
| `pip install <pkg>` | `uv add <pkg>` | Adds to pyproject.toml, updates uv.lock, syncs env |
| `pip uninstall <pkg>` | `uv remove <pkg>` | Removes package and syncs env |
| `pip freeze` / `pip list` | `uv lock` | Generates or updates the lockfile |
| `python -m venv .venv` or `virtualenv` | *(not needed)* | uv auto-creates .venv on first run, or run `uv venv --python 3.12` if you must specify a Python version |

**Wave directive:** apply the above substitutions automatically; otherwise refuse to run the snippet.


## 3. Project Workflow

### 3.1 Initialize (first time)
```bash
# Scaffold pyproject.toml & .python-version
uv init

# Add dependencies
uv add django djangorestframework psycopg[binary]
```


### 3.2 Daily Development
```bash
# Start dev server
uv run manage.py runserver

# Create a new app
uv run manage.py startapp <name>

# Make & apply migrations
uv run manage.py makemigrations
uv run manage.py migrate

# Run tests (pytest)
uv run -m pytest
```


### 3.3 Dependency Management
```bash
# Add dependencies
uv add django-debug-toolbar

# Upgrade a single package
uv lock --upgrade-package django

# Install exactly what is in uv.lock
uv sync
```

## 4. Handy Shortcuts
```bash
# Inspect dependency tree
uv tree

# Remove a package
uv remove <pkg>

# Run a one-off global tool
uvx ruff@latest check .

# Recreate the environment from scratch
rm -rf .venv && uv venv
```

## 5. Linting
```
# Check and auto-fix
uv run ruff check --fix

# Format code
uv run ruff format

# Both together (recommended before commits)
uv run ruff check --fix && uv run ruff format
```


## 5. Enforcement Footer (Wave)

If Wave encounters a shell snippet containing python, pip, django-admin, or virtualenv, it must rewrite it according to this rule, or refuse to execute it.