# Story Sprout : AI-Powered Storytelling Platform

<div align="center">
  <img src="https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django 5.2"/>
  <img src="https://img.shields.io/badge/HTMX-Latest-2D79C7?style=for-the-badge&logo=html5&logoColor=white" alt="HTMX"/>
  <img src="https://img.shields.io/badge/Cotton-Components-FF6B6B?style=for-the-badge&logo=html5&logoColor=white" alt="Cotton Components"/>
  <img src="https://img.shields.io/badge/Tailwind-3.x-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS"/>
  <img src="https://img.shields.io/badge/Pydantic--AI-Latest-FF6B35?style=for-the-badge&logo=python&logoColor=white" alt="Pydantic AI"/>
  <img src="https://img.shields.io/badge/uv-Package_Manager-4051B5?style=for-the-badge&logo=python&logoColor=white" alt="uv"/>
</div>

A modern Django platform for creating AI-assisted illustrated stories. Built with HTMX, Cotton components, and Pydantic AI for a clean, maintainable architecture with real-time collaboration features.



## 🌟 Features

- 🚀 **Django 5.2+** with modern architecture patterns
- 🎨 **Cotton Components** for reusable, maintainable UI
- ⚡ **HTMX** for dynamic interactions without complex JavaScript
- 🎯 **Alpine.js** for lightweight client-side interactivity
- 🤖 **Pydantic AI** integration for type-safe AI workflows
- 🔐 **User Authentication** with django-allauth and social logins
- ✉️ **Email Verification** system
- 📱 **Responsive Interface** with Tailwind CSS
- ⚙️ **Async Task Processing** with Celery and Redis
- 📡 **Real-time Updates** via Server-Sent Events
- 🔧 **Modern Development Tools** (uv, ruff, pytest)
- 📊 **Django Ninja API** framework
- 💳 **Subscription System** foundation with Stripe
- 🏗️ **Multi-environment Configuration** management
- 📝 **Story and Page Management** with ordered models

## 🚀 Quick Start

1. **Clone the repository:**
```bash
git clone <repository-url>
cd story-sprout
```

2. **Install dependencies with uv:**
```bash
uv sync
```

3. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run migrations:**
```bash
make db-sync
# or: uv run services/web/manage.py migrate
```

5. **Create a superuser:**
```bash
make manage createsuperuser
# or: uv run services/web/manage.py createsuperuser
```

6. **Start the development servers:**
```bash
# Terminal 1: Django server
make web

# Terminal 2: Celery worker (for AI tasks)
make tasks
```

Visit http://localhost:8000 to see your application!

## 📁 Project Structure

```
story-sprout/
├── services/
│   ├── web/                 # Main Django application
│   │   ├── apps/            # Django apps
│   │   │   ├── accounts/    # User authentication
│   │   │   ├── ai/          # AI integration and job management
│   │   │   ├── common/      # Shared utilities
│   │   │   ├── dashboard/   # User dashboard
│   │   │   ├── landing/     # Landing page
│   │   │   ├── stories/     # Story and page management
│   │   │   └── subscriptions/ # Subscription system
│   │   ├── core/            # Django project configuration
│   │   │   └── settings/    # Environment-specific settings
│   │   ├── templates/       # HTML templates with Cotton components
│   │   └── static/          # Static assets
│   ├── docs_server/         # Documentation server
│   └── lab/                 # Experimental notebooks
├── docs/                    # Project documentation
├── scripts/                 # Utility scripts
└── Makefile                 # Development commands
```

## 🛠️ Technology Stack

- **Backend:** Django 5.2+ with Django Ninja API
- **Frontend:** HTMX, Cotton Components, Alpine.js
- **Styling:** Tailwind CSS
- **Database:** PostgreSQL (prod) / SQLite (dev)
- **Authentication:** django-allauth
- **AI Integration:** Pydantic AI, Google GenAI, LiteLLM
- **Task Queue:** Celery with Redis
- **Real-time:** Django EventStream (SSE)
- **Package Manager:** uv
- **Code Quality:** ruff, pytest, pre-commit

## 🔄 Celery Setup

Story Sprout uses Celery for handling asynchronous tasks like AI processing, email sending, and other background jobs.

### Prerequisites

- Redis server (used as message broker)

### Running Celery in Development

1. **Start Redis server** (if not already running):
   ```bash
   # Install Redis if needed
   # macOS: brew install redis
   # Ubuntu: sudo apt install redis-server
   
   # Start Redis server
   redis-server
   ```

2. **Start Celery worker** (from project root):
   ```bash
   # Start worker using the management command
   make tasks
   # or manually:
   uv run services/web/manage.py runworker
   ```

3. **Optional: Start Celery beat for scheduled tasks**:
   ```bash
   # This would need to be configured based on your setup
   uv run services/web/manage.py celery beat
   ```

### Using Celery in Your Code

Create tasks in your app's `tasks.py` file:

```python
from celery import shared_task

@shared_task
def my_background_task(param1, param2):
    # Task logic here
    return result
```

Call tasks asynchronously from your views:

```python
from myapp.tasks import my_background_task

# Call task asynchronously
result = my_background_task.delay(param1, param2)

# Or with more options
result = my_background_task.apply_async(
    args=[param1, param2],
    countdown=10  # Execute after 10 seconds
)
```
- **Email:** SendGrid (recommended)


## 🤝 Contributing

We love your input! We want to make contributing to Django SaaS Boilerplate as easy and transparent as possible. Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Maintainer

<div align="center">
  <img src="https://github.com/eriktaveras.png" width="100px" style="border-radius: 50%;" alt="Erik Taveras">
</div>

**Erik Taveras** - Full Stack Solutions Developer

- 🌐 Website: [www.eriktaveras.com](https://www.eriktaveras.com)
- 📧 Email: [hello@eriktaveras.com](mailto:hello@eriktaveras.com)
- 💻 GitHub: [@eriktaveras](https://github.com/eriktaveras)
- 🔗 LinkedIn: [Erik Taveras](https://linkedin.com/in/eriktaveras)

Specialized in Python, Django, and building scalable web applications and API solutions for businesses and startups.

## 🙏 Acknowledgments

- [Django](https://www.djangoproject.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [HTMX](https://htmx.org/)
- [Alpine.js](https://alpinejs.dev/)
- [Stripe](https://stripe.com/)
- [Font Awesome](https://fontawesome.com/)
- [Space Grotesk Font](https://fonts.google.com/specimen/Space+Grotesk)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=eriktaveras/django-saas-boilerplate&type=Date)](https://www.star-history.com/#eriktaveras/django-saas-boilerplate&Date)

## 📫 Contact & Support

If you have any questions or suggestions, please:

- 📝 Open an issue
- 📧 Reach out at [hello@eriktaveras.com](mailto:hello@eriktaveras.com)
- 🐦 Follow [@eriktaveras](https://twitter.com/eriktaveras) on Twitter

<div align="center">
  <p>Built with ❤️ by <a href="https://www.eriktaveras.com">Erik Taveras</a></p>
</div> 


