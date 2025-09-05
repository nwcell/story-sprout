# Makefile for Story Sprout project commands

.PHONY: manage runserver tasks makemigrations migrate db-sync

manage:
	@uv run manage.py $*

dev:
	@echo "Starting Django development server..."
	@uv run manage.py runserver

tasks:
	@echo "Starting Celery worker..."
	@echo "Clearing Redis queues to prevent stale tasks..."
	@redis-cli DEL celery > /dev/null 2>&1 || echo "Warning: Could not clear Redis (not running?)"
	@uv run manage.py runworker

makemigrations:
	@echo "Creating database migrations..."
	@uv run manage.py makemigrations

migrate:
	@echo "Applying database migrations..."
	@uv run manage.py migrate

db-sync: makemigrations migrate

serve-docs:
	@uv run mkdocs serve --dev-addr=127.0.0.1:8001
