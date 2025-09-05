# Makefile for Story Sprout project commands

.PHONY: manage runserver tasks makemigrations migrate db-sync kill-celery list-workers

manage:
	@uv run manage.py $*

dev:
	@echo "Starting Django development server..."
	@uv run manage.py runserver

tasks:
	@echo "Starting single Celery worker (killing any existing workers)..."
	@echo "Clearing Redis queues to prevent stale tasks..."
	@redis-cli DEL celery > /dev/null 2>&1 || echo "Warning: Could not clear Redis (not running?)"
	@uv run manage.py runworker

kill-celery:
	@echo "Killing all Celery workers..."
	@./scripts/kill-celery.sh

list-workers:
	@echo "📋 Active Celery workers:"
	@uv run celery -A core inspect active 2>/dev/null || echo "No workers found or broker not available"
	@echo ""
	@echo "🖥️  System processes:"
	@ps aux | grep 'celery.*worker' | grep -v grep || echo "No worker processes found"

makemigrations:
	@echo "Creating database migrations..."
	@uv run manage.py makemigrations

migrate:
	@echo "Applying database migrations..."
	@uv run manage.py migrate

db-sync: makemigrations migrate

serve-docs:
	@uv run mkdocs serve --dev-addr=127.0.0.1:8001
