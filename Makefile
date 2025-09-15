# Makefile for Story Sprout project commands

.PHONY: manage runserver tasks makemigrations migrate db-sync kill-celery

manage:
	@uv run services/web/manage.py $*

web:
	@echo "Starting Django development server..."
	@uv run services/web/manage.py runserver

tasks:
	@echo "Starting single Celery worker (killing any existing workers)..."
	@echo "Clearing Redis queues to prevent stale tasks..."
	@redis-cli DEL celery > /dev/null 2>&1 || echo "Warning: Could not clear Redis (not running?)"
	@uv run services/web/manage.py runworker

kill-celery:
	@echo "Killing all Celery workers..."
	@./scripts/kill-celery.sh

makemigrations:
	@echo "Creating database migrations..."
	@uv run services/web/manage.py makemigrations

migrate:
	@echo "Applying database migrations..."
	@uv run services/web/manage.py migrate

db-sync: makemigrations migrate

docs-server:
	@uv run mkdocs serve -f docs/mkdocs.yml -a localhost:8001 -w docs

.PHONY: kernel
kernel:
	@uv run python -m ipykernel install --name=story-sprout --display-name "Python (story-sprout)" --prefix .venv
	@echo "✅ kernel installed at .venv/share/jupyter/kernels/story-sprout"

.PHONY: notebooks
notebooks: kernel
	@uv run jupyter lab notebooks

.PHONY: nb
nb: notebooks
