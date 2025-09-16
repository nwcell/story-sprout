from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Conversation(models.Model):
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=240, blank=True)
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or str(self.id)

    def get_ordered_messages(self):
        """Return messages ordered by position."""
        return self.messages.all().order_by("position")


class Message(models.Model):
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    content = models.JSONField()
    position = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["conversation", "position"]
        unique_together = [["conversation", "position"]]

    def save(self, *args, **kwargs):
        if self.position is None:
            # Atomic auto-increment position relative to conversation
            from django.db import transaction

            with transaction.atomic():
                max_position = (
                    Message.objects.filter(conversation=self.conversation)
                    .select_for_update()
                    .aggregate(max_pos=models.Max("position"))["max_pos"]
                )
                self.position = (max_position or -1) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.conversation} - Message {self.position}"

    @classmethod
    def from_pydantic_message(cls, conversation, message):
        """Create a Message from a pydantic-ai ModelMessage."""
        return cls.objects.create(
            conversation=conversation, content=message.model_dump() if hasattr(message, "model_dump") else message
        )

    def to_pydantic_message(self):
        """Convert this Message to a pydantic-ai compatible format."""
        # This would need proper deserialization based on message type
        # For now, return the content directly
        return self.content


class Artifacts(models.Model):
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    file = models.FileField(upload_to="artifacts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Job(models.Model):
    class Status(models.TextChoices):
        QUEUED = "QUEUED"
        RUNNING = "RUNNING"
        SUCCESS = "SUCCESS"
        FAILED = "FAILED"

    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workflow = models.CharField(max_length=64)  # e.g. "wf.story_title"
    payload_json = models.JSONField(default=dict)  # what you actually sent
    celery_task_id = models.CharField(max_length=50, blank=True, db_index=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    output_text = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    runtime_ms = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)
    dispatched_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.workflow} [{self.status}]"
