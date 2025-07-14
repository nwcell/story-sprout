from django.urls import path
from . import views

app_name = 'stories'

urlpatterns = [
    path('', views.stories, name='stories'),
    path('new/', views.new_story, name='new_story'),
    path('<uuid:story_uuid>/', views.story_detail, name='story_detail'),
    
    # HTMX endpoints for in-place editing
    path('<uuid:story_uuid>/title/', views.get_story_title, name='get_story_title'),
    path('<uuid:story_uuid>/edit/title/', views.edit_story_title, name='edit_story_title'),
    path('<uuid:story_uuid>/description/', views.get_story_description, name='get_story_description'),
    path('<uuid:story_uuid>/edit/description/', views.edit_story_description, name='edit_story_description'),
    path('<uuid:story_uuid>/add-page/', views.add_page, name='add_page'),
    path('pages/<int:page_id>/', views.get_page_content, name='get_page_content'),
    path('pages/<int:page_id>/edit/', views.edit_page_content, name='edit_page_content'),
    path('pages/<int:page_id>/delete/', views.delete_page, name='delete_page'),
] 