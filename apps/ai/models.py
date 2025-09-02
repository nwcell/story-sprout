import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

User = get_user_model()


class AIRequest(models.Model):
    """
    An explicit request to run an AI workflow against a target object.
    This replaces the signal-based trigger system.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    celery_task_id = models.UUIDField(null=True, blank=True)

    # The object the AI will modify
    target_ct = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField()
    target = GenericForeignKey("target_ct", "target_id")

    # The specific AI workflow to execute
    workflow_name = models.CharField(max_length=100)

    # Flexible input parameters for the workflow
    input_params = models.JSONField(default=dict, blank=True)

    # Tracking and output
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    output_text = models.TextField(blank=True)
    error_message = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"AIRequest for {self.target} ({self.workflow_name})"

    @classmethod
    def create_for_target(cls, user, target, workflow_name, **kwargs):
        """
        Creates and saves a new AIRequest instance for a specific target object.
        `kwargs` will be saved as the `input_params`.
        """
        from django.contrib.contenttypes.models import ContentType

        content_type = ContentType.objects.get_for_model(target)

        ai_request = cls.objects.create(
            user=user,
            target_ct=content_type,
            target_id=target.pk,
            workflow_name=workflow_name,
            input_params=kwargs,
        )
        return ai_request


class AIWorkflow(models.Model):
    """Model for tracking AI generation workflows with generic foreign keys to target objects."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    target_ct = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField()
    target = GenericForeignKey("target_ct", "target_id")
    workflow_func = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.target} - {self.workflow_func}"

    class Meta:
        verbose_name = "AI Workflow"
        verbose_name_plural = "AI Workflows"
        ordering = ["-created_at"]


class AiJob(models.Model):
    """Model for tracking AI generation jobs with generic foreign keys to target objects."""

    STATUS = [
        ("pending", "Pending"),  # row created, not yet queued
        ("queued", "Queued"),  # Celery task dispatched
        ("running", "Running"),  # worker executing
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]
    workflow = models.ForeignKey(AIWorkflow, on_delete=models.SET_NULL, null=True)

    # Job data
    prompt_payload = models.JSONField(help_text="Rendered context (no secrets)")
    status = models.CharField(
        max_length=20, choices=STATUS, default="pending", help_text="Current status of the AI job"
    )
    attempts = models.PositiveSmallIntegerField(default=0, help_text="Number of processing attempts")
    last_error = models.TextField(blank=True, help_text="Last error message if the job failed")

    # Output
    prompt_result = models.TextField(blank=True)

    # Usage tracking
    usage_tokens = models.JSONField(null=True, blank=True, help_text='Token usage like {"in":123,"out":456}')
    cost_usd = models.DecimalField(
        max_digits=8, decimal_places=4, null=True, blank=True, help_text="Cost of the AI request in USD"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True, help_text="When job processing started")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="When job processing completed")

    def __str__(self):
        """Return a string representation of the AI job."""
        return f"{self.workflow} #{self.id} ({self.status})"

    def mark_as_queued(self):
        """Mark the job as queued (Celery task dispatched)."""
        self.status = "queued"
        self.save(update_fields=["status"])

    def mark_as_running(self):
        """Mark the job as running and increment attempts."""
        self.status = "running"
        self.started_at = timezone.now()
        self.attempts += 1
        self.save(update_fields=["status", "started_at", "attempts"])

    def mark_as_succeeded(self, prompt_result=None, usage_tokens=None, cost_usd=None):
        """Mark the job as succeeded with output and usage info."""
        self.status = "succeeded"
        self.completed_at = timezone.now()

        update_fields = ["status", "completed_at"]

        if prompt_result is not None:
            self.prompt_result = prompt_result
            update_fields.append("prompt_result")
        if usage_tokens is not None:
            self.usage_tokens = usage_tokens
            update_fields.append("usage_tokens")
        if cost_usd is not None:
            self.cost_usd = Decimal(str(cost_usd))
            update_fields.append("cost_usd")

        self.save(update_fields=update_fields)

    def mark_as_failed(self, error_message):
        """Mark the job as failed with an error message."""
        self.status = "failed"
        self.last_error = str(error_message)[:5000]  # Truncate long errors
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "last_error", "completed_at"])

    def mark_as_cancelled(self):
        """Mark the job as cancelled."""
        self.status = "cancelled"
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at"])

    class Meta:
        verbose_name = "AI Job"
        verbose_name_plural = "AI Jobs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["workflow", "status"]),
        ]
