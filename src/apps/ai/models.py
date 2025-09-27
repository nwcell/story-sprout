from collections import defaultdict
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import Max
from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter
from pydantic_core import to_jsonable_python

from apps.ai.types import ChatResponse, Chip, chat_response_adapter

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
        Message.objects.bulk_create(messages_to_create)

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
    def bulk_create(self, objs, **kwargs):
        messages_by_conv = defaultdict(list)
        for msg in objs:
            # Ensure conversation is attached if only conversation_id is set
            if msg.conversation_id and not hasattr(msg, '_conversation_cache'):
                # This is a simplification; direct access like this is tricky.
                # The logic in insert_model_messages already provides the conversation object.
                pass
            messages_by_conv[msg.conversation_id].append(msg)

        with transaction.atomic():
            for conv_id, messages in messages_by_conv.items():
                last_position = (
                    self.get_queryset()
                    .filter(conversation_id=conv_id)
                    .aggregate(Max("position"))["position__max"]
                    or 0
                )
                for i, msg in enumerate(messages):
                    msg.position = last_position + i + 1
        return super().bulk_create(objs, **kwargs)


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

    def __str__(self):
        return f"{self.conversation} - Message {self.position}"

    def save(self, *args, **kwargs):
        if self.position is None:
            with transaction.atomic():
                last_position = (
                    Message.objects.filter(conversation=self.conversation)
                    .select_for_update()
                    .aggregate(Max("position"))["position__max"]
                    or 0
                )
                self.position = last_position + 1
        super().save(*args, **kwargs)

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
