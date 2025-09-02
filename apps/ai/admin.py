from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from markdownx.utils import markdownify

from .models import AiJob, AIRequest, AIWorkflow


@admin.register(AIRequest)
class AIRequestAdmin(admin.ModelAdmin):
    list_display = ("uuid", "user", "workflow_name", "target_display", "status", "created_at")
    list_filter = ("status", "workflow_name", "user")
    search_fields = ("uuid", "user__username", "workflow_name")
    readonly_fields = ("uuid", "created_at", "completed_at", "celery_task_id")

    def target_display(self, obj):
        """Display target object with link to admin if available."""
        if not obj.target:
            return "—"

        target_name = str(obj.target)
        try:
            content_type = obj.target_ct
            app_label = content_type.app_label
            model_name = content_type.model
            url = f"/admin/{app_label}/{model_name}/{obj.target_id}/change/"
            return format_html('<a href="{}">{}</a>', url, target_name)
        except Exception:
            return target_name

    target_display.short_description = "Target"


@admin.register(AIWorkflow)
class AIWorkflowAdmin(admin.ModelAdmin):
    """Admin interface for AI Workflows."""

    # Basic display configuration
    list_display = ["id", "uuid", "workflow_func", "target_display"]
    list_filter = ["workflow_func"]
    search_fields = ["id", "uuid", "workflow_func"]
    date_hierarchy = "created_at"
    readonly_fields = ["uuid", "created_at", "updated_at"]

    # Field organization
    fieldsets = [
        (
            "Workflow Information",
            {
                "fields": ["uuid", "workflow_func", "user"],
            },
        ),
        (
            "Target",
            {
                "fields": ["target_ct", "target_id"],
            },
        ),
        (
            "Timestamps",
            {
                "fields": ["created_at", "updated_at"],
            },
        ),
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
            url = f"/admin/{app_label}/{model_name}/{obj.target_id}/change/"
            return format_html('<a href="{}">{}</a>', url, target_name)
        except Exception:
            return target_name

    target_display.short_description = "Target"


@admin.register(AiJob)
class AiJobAdmin(admin.ModelAdmin):
    """Admin interface for AI generation jobs."""

    # Basic display configuration
    list_display = ["id", "workflow_display", "status", "created_at", "completed_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["id", "last_error", "prompt_result"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at", "started_at", "completed_at", "attempts", "formatted_prompt_payload"]

    # Field organization
    fieldsets = [
        (
            "Job Information",
            {
                "fields": ["workflow", "status", "attempts"],
            },
        ),
        (
            "Data",
            {
                "fields": ["formatted_prompt_payload", "last_error"],
                "classes": ["collapse"],
            },
        ),
        (
            "Output",
            {
                "fields": ["prompt_result"],
            },
        ),
        (
            "Usage & Cost",
            {
                "fields": ["usage_tokens", "cost_usd"],
            },
        ),
        (
            "Timestamps",
            {
                "fields": ["created_at", "started_at", "completed_at"],
            },
        ),
    ]

    def workflow_display(self, obj):
        """Display workflow with link to admin."""
        if not obj.workflow:
            return "—"

        # Get the name of the workflow
        workflow_name = str(obj.workflow)

        # Create admin link for the workflow
        url = f"/admin/ai/aiworkflow/{obj.workflow.id}/change/"
        return format_html('<a href="{}">{}</a>', url, workflow_name)

    workflow_display.short_description = "Workflow"

    def formatted_prompt_payload(self, obj):
        if not obj.prompt_payload:
            return "—"

        md_text = str(obj.prompt_payload)
        return mark_safe(markdownify(md_text))

    formatted_prompt_payload.short_description = "Prompt Payload"
