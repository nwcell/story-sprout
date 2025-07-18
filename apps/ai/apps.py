from django.apps import AppConfig


class AiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai'
    
    def ready(self):
        # Import signals to register them with Django's signal dispatcher
        # This import is intentional to register signal handlers, even though not used directly
        import apps.ai.signals  # noqa
