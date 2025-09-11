# Makefile for Story Sprout project commands

.PHONY: manage runserver tasks makemigrations migrate db-sync kill-celery

manage:
	@uv run --project services/web python services/web/manage.py $*

web:
	@echo "Starting Django development server..."
	@uv run --project services/web python services/web/manage.py runserver

tasks:
	@echo "Starting single Celery worker (killing any existing workers)..."
	@echo "Clearing Redis queues to prevent stale tasks..."
	@redis-cli DEL celery > /dev/null 2>&1 || echo "Warning: Could not clear Redis (not running?)"
	@uv run --project services/web python services/web/manage.py runworker

kill-celery:
	@echo "Killing all Celery workers..."
	@./scripts/kill-celery.sh

makemigrations:
	@echo "Creating database migrations..."
	@uv run --project services/web python services/web/manage.py makemigrations

migrate:
	@echo "Applying database migrations..."
	@uv run --project services/web python services/web/manage.py migrate

db-sync: makemigrations migrate

docs-server:
	@uv run --project services/docs_server mkdocs serve -f services/docs_server/mkdocs.yml -a localhost:8001 -w docs

lab:
	@uv run --project services/lab marimo edit services/lab/apps --watch --host 0.0.0.0 --allow-origins * --proxy travis.local:2718 --headless
