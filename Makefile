# Makefile for Story Sprout project

# Variables
work_dir = $(shell git rev-parse --show-toplevel)
web_dir = src
app = config
uv_cmd = uv run
manage_cmd = $(uv_cmd) manage.py
celery_cmd = $(uv_cmd) --directory $(web_dir) celery
celery_pidfile = .run/celery.pid
celery_host = dev@%h
docs_port = 8001
web_port = 8000
network_port = 80
network_host = 0.0.0.0
caffeinate_cmd = caffeinate -is


# --- Watchdog config ---
watchmedo        := uv run watchmedo
watch_patterns   := "*.py;*.toml;*.html;*.js;*.css"
ignore_patterns  := "*/.git/*;*/.venv/*;*/node_modules/*;*/.pytest_cache/*;*/.mypy_cache/*;*/.run/*;*/dist/*;*/build/*;*/static/*;*/media/*"

# Helper macro
define WATCH
	$(watchmedo) auto-restart \
	  --directory=. --recursive \
	  --patterns=$(watch_patterns) \
	  --ignore-patterns=$(ignore_patterns) \
	  --signal SIGTERM --kill-after 5 -- \
	  $(1)
endef


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

web-network: ## 🌱 Start Django development server on network
	@echo "🌱 Starting Django development server on network port $(web_port)..."
	@$(caffeinate_cmd) $(manage_cmd) runserver $(network_host):$(network_port)
.PHONY: web-network

tasks: ## 🔄 Start Celery worker
	@echo "🔄 Starting Celery worker"
	@$(call WATCH,$(celery_cmd) -A $(app) worker \
		--loglevel=INFO \
		--pool=solo \
		--hostname=$(celery_host) \
		--without-gossip --without-mingle --without-heartbeat)
.PHONY: tasks

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
	@$(uv_cmd) mkdocs serve -f mkdocs.yml -a localhost:$(docs_port) -w docs
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
	@echo "🧺 Purging Celery queues..."
	@$(celery_cmd) -A $(app) purge --force
	@echo "✅ Cleanup complete"
.PHONY: clean

test: ## 🧪 Run tests
	@echo "🧪 Running tests..."
	@$(uv_cmd) pytest
.PHONY: test

# Prevent make from interpreting arguments as targets
%:
	@:
