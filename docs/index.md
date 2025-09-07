# Overview

Welcome to the comprehensive documentation for **Story Sprout**, a modern Django-based storytelling platform with AI-powered features.

## 🚀 What is Story Sprout?

Story Sprout is a sophisticated web application that combines traditional storytelling with cutting-edge AI technology. Built on Django and powered by a modern tech stack, it provides users with an intuitive platform to create, manage, and enhance their stories.

## ✨ Key Features

- **AI-Powered Writing Assistant**: Advanced AI integration for story enhancement and suggestions
- **Modern UI/UX**: Built with Tailwind CSS, Alpine.js, and HTMX for a responsive, interactive experience
- **Real-time Updates**: Server-Sent Events (SSE) for live progress streaming
- **Secure Authentication**: Comprehensive user management with Django Allauth
- **Scalable Architecture**: Designed for performance with Celery, Redis, and PostgreSQL

## 🛠 Tech Stack Highlights

- **Backend**: Django 5.2+ with modern Python practices
- **Frontend**: Tailwind CSS + Alpine.js + HTMX (no heavy JS frameworks)
- **Database**: PostgreSQL with Redis for caching
- **AI Integration**: LiteLLM for flexible AI model support
- **Task Queue**: Celery with Redis broker
- **Package Management**: UV for fast, reliable dependency management

## 📚 Documentation Sections

### Getting Started
Learn about the project requirements, implementation roadmap, and technology choices.

### Architecture
Understand the application structure, data flow, and system design decisions.

### Development
Comprehensive guides for frontend development, UI patterns, and coding conventions.

### AI Features
Deep dive into AI workflow design, integration patterns, and feature implementation.

### Security
Security guidelines, best practices, and implementation details.

## 🔧 Quick Start

```bash
# Clone and setup the project
git clone https://github.com/your-username/story-sprout
cd story-sprout

# Install dependencies with uv
uv sync

# Setup database
uv run manage.py migrate

# Create superuser
uv run manage.py createsuperuser

# Start development server
uv run manage.py runserver
```

## 📖 Documentation Navigation

Use the navigation menu to explore different sections of the documentation. Each section provides detailed information about specific aspects of the Story Sprout platform.

- **Getting Started** - Project overview and setup
- **Architecture** - System design and structure
- **Development** - Coding guidelines and patterns
- **AI Features** - AI integration and workflows
- **Security** - Security practices and guidelines

## 🤝 Contributing

Story Sprout follows modern Django best practices and emphasizes clean, maintainable code. Check out our development guidelines and coding conventions for contribution information.

## 📝 Documentation Updates

This documentation is automatically updated with git revision dates. Each page shows when it was last modified to help you stay current with the latest information.

---

**Ready to dive in?** Check out the [PRD](prd.md) to understand the full scope and vision of Story Sprout.
