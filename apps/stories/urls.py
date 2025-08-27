from django.urls import path

from . import views

app_name = "stories"

urlpatterns = [
    path("", views.stories, name="stories"),
    path("new/", views.new_story, name="new_story"),
    path("<uuid:story_uuid>/", views.story_detail, name="story_detail"),
]
