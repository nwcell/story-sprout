# Makefile for Story Sprout project

# Variables
web_dir = src
uv_cmd = uv run
manage_cmd = uv run $(uv_cmd) manage.py
docs_port = 8001
web_port = 8000

# Default target
help: ## Show this help message
	@echo "Story Sprout Development Commands:"
	@echo ""
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m %-20s\033[0m %s\n", $$1, $$2}'
.PHONY: help

# Development targets
web: ## 🌱 Start Django development server
	@echo "🌱 Starting Django development server on port $(web_port)..."
	@$(manage_cmd) runserver $(web_port)
.PHONY: web

tasks: ## 🔄 Start Celery worker
	@echo "🔄 Starting Celery worker (killing existing workers)..."
	@echo "🧹 Clearing Redis queues..."
	@redis-cli DEL celery > /dev/null 2>&1 || echo "⚠️  Warning: Could not clear Redis (not running?)"
	@$(manage_cmd) runworker
.PHONY: tasks

tasks-kill: ## 🛑 Kill all Celery workers
	@echo "🛑 Killing all Celery workers..."
	@./scripts/kill-celery.sh
.PHONY: kill

db: db-mm db-migrate ## ✅ Sync database (mm + migrate)
	@echo "✅ Database synchronized"
.PHONY: db

# Database targets
db-mm: ## 📝 Create database migrations
	@echo "📝 Creating database migrations..."
	@$(manage_cmd) makemigrations
.PHONY: mm

db-migrate: ## ⬆️  Apply database migrations
	@echo "⬆️  Applying database migrations..."
	@$(manage_cmd) migrate
.PHONY: migrate

# Documentation targets
docs: ## 📚 Start documentation server
	@echo "📚 Starting documentation server on port $(docs_port)..."
	@$(uv_cmd) mkdocs serve -f docs/mkdocs.yml -a localhost:$(docs_port) -w docs
.PHONY: docs

# Notebook targets
kernel: ## 🔧 Install Jupyter kernel
	@echo "🔧 Installing Jupyter kernel..."
	@$(uv_cmd) python -m ipykernel install --name=story-sprout --display-name "Python (story-sprout)" --prefix .venv
	@echo "✅ Kernel installed at .venv/share/jupyter/kernels/story-sprout"
.PHONY: kernel

nb: kernel ## 📓 Start Jupyter Lab
	@echo "📓 Starting Jupyter Lab..."
	@$(uv_cmd) jupyter lab notebooks
.PHONY: nb

# Utility targets
manage: ## 🛠️  Run Django management command
	@$(manage_cmd) $(filter-out $@,$(MAKECMDGOALS))
.PHONY: manage

clean: ## 🧹 Clean temporary files
	@echo "🧹 Cleaning temporary files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type f -name ".coverage" -delete
	@echo "✅ Cleanup complete"
.PHONY: clean

test: ## 🧪 Run tests
	@echo "🧪 Running tests..."
	@$(uv_cmd) pytest
.PHONY: test

# Prevent make from interpreting arguments as targets
%:
	@:
