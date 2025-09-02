# Makefile for Story Sprout project commands

.PHONY: manage runserver tasks makemigrations migrate db-sync

manage:
	@uv run manage.py $*

runserver:
	@echo "Starting Django development server..."
	@uv run manage.py runserver

tasks:
	@echo "Starting Celery worker..."
	@uv run -m celery -A core worker -l INFO

makemigrations:
	@echo "Creating database migrations..."
	@uv run manage.py makemigrations

migrate:
	@echo "Applying database migrations..."
	@uv run manage.py migrate

db-sync: makemigrations migrate

docs:
	@uv run mkdocs serve --dev-addr=127.0.0.1:8001
