import django_eventstream
from django.urls import path

app_name = "ai"

urlpatterns = [
    path(
        "conversations/<uuid:conversation_uuid>/events/",
        django_eventstream.views.events,
        {"format-channels": ["conversation-{conversation_uuid}"]},
        name="conversation_events",
    ),
]