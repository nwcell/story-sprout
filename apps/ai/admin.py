from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.utils.safestring import mark_safe
from .models import AIPrompt
from .tasks import process_ai_prompt

@admin.register(AIPrompt)
class AIPromptAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'truncated_prompt', 
        'user', 
        'status_badge', 
        'max_tokens',
        'created_at', 
        'processed_at'
    )
    list_filter = ('status', 'user', 'created_at', 'processed_at')
    search_fields = ('prompt', 'result', 'user__username')
    readonly_fields = (
        'uuid', 
        'status', 
        'created_at', 
        'updated_at', 
        'processed_at', 
        'task_id',
        'error_message', 
        'formatted_result'
    )
    fieldsets = (
        ('Prompt Information', {
            'fields': ('user', 'prompt', 'max_tokens'),
        }),
        ('Result', {
            'fields': ('formatted_result',),
            'classes': ('collapse',),
        }),
        ('Status Information', {
            'fields': ('status', 'error_message', 'task_id'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'processed_at'),
            'classes': ('collapse',),
        }),
    )
    actions = ['process_selected_prompts']
    
    def get_queryset(self, request):
        # Prefetch related user to avoid N+1 queries
        return super().get_queryset(request).select_related('user')
    
    def truncated_prompt(self, obj):
        """Show a truncated version of the prompt."""
        max_length = 50
        if len(obj.prompt) > max_length:
            return f"{obj.prompt[:max_length]}..."
        return obj.prompt
    truncated_prompt.short_description = 'Prompt'
    
    def status_badge(self, obj):
        """Show a colored status badge."""
        status_colors = {
            'pending': 'bg-gray-500',
            'processing': 'bg-blue-500',
            'completed': 'bg-green-500',
            'failed': 'bg-red-500',
        }
        color = status_colors.get(obj.status, 'bg-gray-500')
        return format_html(
            '<span class="{} text-white py-1 px-2 rounded">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.allow_tags = True
    
    def formatted_result(self, obj):
        """Show the result in a nicely formatted way."""
        if not obj.result:
            return "-"
        
        return mark_safe(f'<div class="p-3 bg-gray-100 rounded">{obj.result}</div>')
    formatted_result.short_description = 'Result'
    

    
    def process_selected_prompts(self, request, queryset):
        """Process selected prompts using Celery."""
        count = 0
        for prompt in queryset:
            if prompt.status in ['pending', 'failed']:
                # Send to Celery for processing
                process_ai_prompt.delay(prompt.id)
                count += 1
        
        if count > 0:
            message = f"{count} prompt{'s' if count > 1 else ''} sent for processing. Check back later for results."
            self.message_user(request, message, messages.SUCCESS)
        else:
            self.message_user(request, "No prompts were processed. Only pending or failed prompts can be processed.", messages.WARNING)
    
    process_selected_prompts.short_description = "Process selected prompts with AI"
    
    def save_model(self, request, obj, form, change):
        """When creating a new prompt, set the user to the current admin user."""
        if not change:  # New object
            obj.user = request.user
        super().save_model(request, obj, form, change)
        
        # If this is a new prompt, process it automatically
        if not change:
            self.message_user(
                request, 
                "Your prompt has been created and sent for processing. Refresh in a few moments to see the result.", 
                messages.SUCCESS
            )
            process_ai_prompt.delay(obj.id)
