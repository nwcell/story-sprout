from django.apps import AppConfig


class AiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ai"

    def ready(self):
        from apps.ai import tasks  # noqa
        # from apps.ai import signals  # noqa
