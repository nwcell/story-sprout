from apps.core.views import HtmxEditableFieldView, HtmxToggleView
from django.shortcuts import render, get_object_or_404
from .models import Story, Page
from .forms import StoryTitleForm, StoryDescriptionForm, PageContentForm

class EditableStoryTitleView(HtmxEditableFieldView):
    """Unified HTMX view for displaying and editing a story's title"""
    model = Story
    form_class = StoryTitleForm
    template_name = 'stories/components/story_title.html'
    field_name = 'title'
    
    def get_object(self, request, *args, **kwargs):
        """Get story object using story_uuid from URL"""
        return get_object_or_404(self.model, uuid=kwargs.get('story_uuid'))
    
    def check_permissions(self, obj):
        """Check if user has permission to edit this story's title"""
        user = self.request.user
        return user.is_authenticated and (user == obj.user or user.is_staff)


class EditableStoryDescriptionView(HtmxEditableFieldView):
    """Unified HTMX view for displaying and editing a story's description"""
    model = Story
    form_class = StoryDescriptionForm
    template_name = 'cotton/editable_field.html'
    field_name = 'description'
    
    def get_object(self, request, *args, **kwargs):
        """Get story object using story_uuid from URL"""
        return get_object_or_404(self.model, uuid=kwargs.get('story_uuid'))
    
    def check_permissions(self, obj):
        """Check if user has permission to edit this story's description"""
        user = self.request.user
        return user.is_authenticated and (user == obj.user or user.is_staff)
