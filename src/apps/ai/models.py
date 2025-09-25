from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models
from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter
from pydantic_core import to_jsonable_python

from apps.ai.types import ChatResponse, chat_response_adapter, Chip

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
        return self.title or f"Conversation: {str(self.uuid)}"

    def get_ordered_messages(self):
        """Return messages ordered by position."""
        return self.messages.all().order_by("position")

    @property
    def model_messages(self) -> list[ModelMessage]:
        """Return messages ordered by position."""
        messages = list(self.messages.all().order_by("position").values_list("content", flat=True))
        return ModelMessagesTypeAdapter.validate_python(messages)

    def insert_model_messages(self, messages: list[ModelMessage]):
        messages = to_jsonable_python(messages)
        messages_to_create = [Message(conversation=self, content=msg_data) for msg_data in messages]

    def latest_response(self):
        """Return the latest ModelResponse message."""
        queryset = self.messages.filter(content__kind="response").order_by("-position")
        return queryset.values_list("content", flat=True).first()

    # TODO: This is gonna be brittle... denormalize?
    @property
    def chat_display(self) -> ChatResponse:
        """Return a response shape from the latest response"""
        chat_response: ChatResponse | None = None
        response = self.latest_response()

        if response:
            for part in response.get("parts", []):
                if part.get("tool_name") == "final_result":
                    chat_response = chat_response_adapter.validate_python(part["args"])
                    break

        if chat_response is None:
            chat_response = ChatResponse(
                message="What sounds fun right now?",
                chips=[
                    Chip(emoji="🌟", color="sky", value="Cook up something new"),
                    Chip(emoji="🛠️", color="emerald", value="Build on our story"),
                    Chip(emoji="🤖", color="violet", value="Ask the writer bot"),
                ],
            )

        return chat_response


class MessageManager(models.Manager):
    """Custom manager that handles position auto-assignment for bulk operations."""

    def bulk_create(
        self,
        objs,
        batch_size=None,
        ignore_conflicts=False,
        update_conflicts=False,
        update_fields=None,
        unique_fields=None,
    ):
        """Override bulk_create to assign positions before database insert."""
        from django.db import transaction

        # Group objects by conversation for position assignment
        conv_groups = {}
        for obj in objs:
            conv_id = obj.conversation_id or obj.conversation.id
            if conv_id not in conv_groups:
                conv_groups[conv_id] = []
            conv_groups[conv_id].append(obj)

        with transaction.atomic():
            # Assign positions for each conversation group
            for conv_id, conv_objs in conv_groups.items():
                # Get current max position for this conversation
                max_position = self.filter(conversation_id=conv_id).aggregate(max_pos=models.Max("position"))["max_pos"]
                starting_position = (max_position or -1) + 1

                # Assign sequential positions to objects without positions
                for i, obj in enumerate(conv_objs):
                    if obj.position is None:
                        obj.position = starting_position + i

            # Call parent bulk_create with positioned objects
            return super().bulk_create(
                objs,
                batch_size=batch_size,
                ignore_conflicts=ignore_conflicts,
                update_conflicts=update_conflicts,
                update_fields=update_fields,
                unique_fields=unique_fields,
            )


class Message(models.Model):
    """
    Message within a conversation with auto-assigned sequential position.

    Position auto-assignment works with:
    - Single create: Message.objects.create(conversation=conv, content=data)
    - Bulk create: Message.objects.bulk_create([Message(conversation=conv, content=data), ...])

    Both operations will automatically assign sequential positions within each conversation.
    """

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    content = models.JSONField()
    position = models.IntegerField(
        null=True, blank=True, help_text="Auto-assigned sequential position within conversation"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MessageManager()

    class Meta:
        ordering = ["conversation", "position"]
        unique_together = [["conversation", "position"]]

    def save(self, *args, **kwargs):
        """Auto-assign position if not set (for single creates)."""
        if self.position is None:
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
