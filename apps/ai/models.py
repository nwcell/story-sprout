from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class AIPrompt(models.Model):
    """Model for storing AI prompts and their results."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                            help_text="User who created this prompt")
    prompt = models.TextField(help_text="The prompt text to send to the AI")
    max_tokens = models.IntegerField(default=100, 
                                    help_text="Maximum number of tokens for the response")
    result = models.TextField(blank=True, null=True, 
                            help_text="The AI-generated result")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                            default='pending',
                            help_text="Current status of the AI processing")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True,
                                        help_text="When the prompt was processed")
    task_id = models.CharField(max_length=255, blank=True, null=True, 
                            help_text="Celery task ID")
    error_message = models.TextField(blank=True, null=True,
                                    help_text="Error message if the task failed")
    tokens_used = models.IntegerField(default=0,
                                    help_text="Number of tokens used in the AI response")
    model = models.CharField(max_length=50, blank=True, null=True,
                          help_text="The AI model used to generate the response")
    
    def __str__(self):
        """Return a string representation of the prompt."""
        return f"{self.prompt[:50]}{'...' if len(self.prompt) > 50 else ''}"
    
    def mark_as_processing(self, task_id):
        """Mark the prompt as being processed with the given task ID."""
        self.status = 'processing'
        self.task_id = task_id
        self.save(update_fields=['status', 'task_id', 'updated_at'])
    
    def mark_as_completed(self, result, tokens_used=0, model=None):
        """Mark the prompt as completed with the given result and metadata."""
        self.status = 'completed'
        self.result = result
        self.processed_at = timezone.now()
        self.tokens_used = tokens_used
        if model:
            self.model = model
        self.save(update_fields=['status', 'result', 'processed_at', 'tokens_used', 'model', 'updated_at'])
    
    def mark_as_failed(self, error_message):
        """Mark the prompt as failed with the given error message."""
        self.status = 'failed'
        self.error_message = error_message
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'processed_at', 'updated_at'])
    
    class Meta:
        verbose_name = "AI Prompt"
        verbose_name_plural = "AI Prompts"
        ordering = ["-created_at"]
