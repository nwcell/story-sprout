import django_eventstream
from django.urls import path

from . import views

app_name = "stories"

urlpatterns = [
    path("", views.stories, name="stories"),
    path("<uuid:story_uuid>/", views.story_detail, name="story_detail"),
    path(
        "<uuid:story_uuid>/events/",
        django_eventstream.views.events,
        {"format-channels": ["story-{story_uuid}"]},
        name="events",
    ),
]
