from django.contrib import admin
from django.utils.html import format_html

from .models import AiJob


@admin.register(AiJob)
class AiJobAdmin(admin.ModelAdmin):
    """Admin interface for AI generation jobs."""
    
    # Basic display configuration
    list_display = ['id', 'job_type', 'status', 'target_display', 'created_at', 'completed_at']
    list_filter = ['status', 'job_type', 'created_at']
    search_fields = ['id', 'template_key', 'model_name', 'last_error']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'started_at', 'completed_at', 'attempts']
    
    # Field organization
    fieldsets = [
        ('Job Information', {
            'fields': [
                'job_type', 'status', 'template_key', 'template_ver', 'model_name',
                'user', 'attempts'
            ],
        }),
        ('Target', {
            'fields': ['target_ct', 'target_id'],
        }),
        ('Data', {
            'fields': ['prompt_payload', 'last_error'],
            'classes': ['collapse'],
        }),
        ('Output', {
            'fields': ['output_text', 'output_ref'],
        }),
        ('Usage & Cost', {
            'fields': ['usage_tokens', 'cost_usd'],
        }),
        ('Timestamps', {
            'fields': ['created_at', 'started_at', 'completed_at'],
        }),
    ]
    
    def target_display(self, obj):
        """Display target object with link to admin if available."""
        if not obj.target:
            return "—"
            
        # Get the name of the target
        target_name = str(obj.target)
        
        # Try to create an admin link for the target
        try:
            content_type = obj.target_ct
            app_label = content_type.app_label
            model_name = content_type.model
            url = f'/admin/{app_label}/{model_name}/{obj.target_id}/change/'
            return format_html('<a href="{}">{}</a>', url, target_name)
        except Exception:
            return target_name
    
    target_display.short_description = 'Target'
