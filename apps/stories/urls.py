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

    # HTMX endpoints for page editing
    path('pages/<int:page_id>/', views.get_page_content, name='get_page_content'),
    path('pages/<int:page_id>/edit/', views.edit_page_content, name='edit_page_content'),
    path('pages/<int:page_id>/toggle-generating/', views.toggle_content_generating, name='toggle_content_generating'),
    path('pages/<int:page_id>/check-generating-status/', views.check_content_generating_status, name='check_content_generating_status'),
    path('pages/<int:page_id>/delete/', views.delete_page, name='delete_page'),

    # Image text editing endpoints
    path('pages/<int:page_id>/image-text/', views.get_page_image_text, name='get_page_image_text'),
    path('pages/<int:page_id>/image-text/edit/', views.edit_page_image_text, name='edit_page_image_text'),
    path('pages/<int:page_id>/image-text/update/', views.update_page_image_text, name='update_page_image_text'),

    # Image upload and deletion endpoints
    path('pages/<int:page_id>/image/upload/', views.upload_page_image, name='upload_page_image'),
    path('pages/<int:page_id>/image/delete/', views.delete_page_image, name='delete_page_image'),
    path('pages/<int:page_id>/move/<str:direction>/', views.move_page, name='move_page'),
] 