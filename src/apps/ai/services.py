"""
AI services for managing artifacts and AI-related operations.
"""

import logging
import mimetypes
import uuid
from datetime import datetime
from typing import Annotated
from uuid import UUID

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import connection
from django.db.models import Q
from pydantic import BaseModel, BeforeValidator, TypeAdapter
from pydantic_ai.messages import BinaryContent, ImageUrl, ModelMessagesTypeAdapter

from apps.ai.models import Artifacts, Conversation
from apps.ai.types import ChatResponse
from apps.common.sse import send_template

logger = logging.getLogger(__name__)


class MessageSchema(BaseModel):
    uuid: UUID
    content: dict  # JSONField stores dict data
    position: int


def convert_messages(v):
    """Convert Django RelatedManager or QuerySet to list."""
    if hasattr(v, "all"):
        return list(v.all())
    return v


class ConversationSchema(BaseModel):
    uuid: UUID
    user_id: int
    title: str | None
    meta: dict
    created_at: datetime
    updated_at: datetime


class ConversationDetailSchema(ConversationSchema):
    messages: Annotated[list[MessageSchema], BeforeValidator(convert_messages)]


class ConversationService:
    def __init__(self, uuid: UUID):
        self.uuid = uuid
        self.adapter: TypeAdapter = ModelMessagesTypeAdapter

    @classmethod
    def create_conversation(
        cls, user_id: int, title: str | None = None, meta: dict | None = None
    ) -> "ConversationService":
        conversation = Conversation.objects.create(user_id=user_id, title=title or "", meta=meta or {})
        return cls(uuid=conversation.uuid)

    def list_conversations(
        self, user_id: int | None = None, title: str | None = None, meta: dict[str, str] | None = None
    ) -> list[ConversationSchema]:
        query = Q()

        logger.info(f"list_conversations called with user_id: {user_id}, title: {title}, meta: {meta}")
        if user_id:
            query &= Q(user_id=user_id)
        if title:
            # Use PostgreSQL full-text search if available, otherwise fallback to icontains
            if connection.vendor == "postgresql":
                query &= Q(title__search=title)
            else:
                query &= Q(title__icontains=title)
        if meta:
            for key, value in meta.items():
                lookup_key = f"meta__{key}"
                query &= Q(**{lookup_key: value})

        conversations = Conversation.objects.filter(query)
        return [ConversationSchema.model_validate(conv, from_attributes=True) for conv in conversations]

    def get_conversation(self) -> ConversationDetailSchema:
        conversation = Conversation.objects.get(uuid=self.uuid)
        return ConversationDetailSchema.model_validate(conversation, from_attributes=True)

    def get_model_messages(self):
        """Get model messages for this conversation."""
        conversation = Conversation.objects.get(uuid=self.uuid)
        return conversation.model_messages

    def add_model_messages(self, messages):
        """Add model messages to this conversation."""
        conversation = Conversation.objects.get(uuid=self.uuid)
        conversation.insert_model_messages(messages)

    def send_chat_response(self, chat_response: ChatResponse) -> None:
        """
        Send ChatResponse via SSE events to update the AI panel.

        This triggers two separate events:
        - 'prompt_row': Updates the message display
        - 'chip_row': Updates the chips display

        Args:
            chat_response: ChatResponse containing message and chips
        """
        logger.info(
            f"Sending chat response for conversation {self.uuid}: "
            f"{len(chat_response.message)} chars, {len(chat_response.chips)} chips"
        )

        # Send message update event
        self._send_message_event(chat_response.message)

        # Send chips update event
        self._send_chips_event(chat_response.chips)

    def sync_chat_display(self) -> None:
        """
        Sync the AI panel with the current conversation's chat display.

        This fetches the conversation's current chat_display and sends it via SSE
        to update the AI panel with the latest message and chips.
        """
        conversation = Conversation.objects.get(uuid=self.uuid)
        chat_display = conversation.chat_display

        logger.info(f"Syncing chat display for conversation {self.uuid}")
        self.send_chat_response(chat_display)

    def _send_message_event(self, message: str) -> None:
        """Send SSE event to update the prompt row with new message."""
        channel_name = f"conversation-{self.uuid}"
        send_template(channel_name, "prompt_row", "cotton/ai/panel/content/prompt_row.html", {"slot": message})
        logger.debug(f"Sent prompt_row event to {channel_name}")

    def _send_chips_event(self, chips: list) -> None:
        """Send SSE event to update the chip row with new chips."""
        channel_name = f"conversation-{self.uuid}"
        send_template(channel_name, "chip_row", "cotton/ai/panel/content/chip_row.html", {"chips": chips})
        logger.debug(f"Sent chip_row event to {channel_name} with {len(chips)} chips")


class ChatService:
    def __init__(self, conversation_uuid):
        self.conversation_uuid = conversation_uuid

    def update_prompt(self, input):
        pass

    def update_chips(self, chips):
        pass

    def update_chat(self, freeform_on: bool = True):
        pass


class ArtifactService:
    """Service for managing artifacts using the AI app's Artifacts model."""

    def build_absolute_url(self, relative_url: str) -> str:
        """
        Build absolute URL using Django best practices.

        Args:
            relative_url: The relative URL from a file field

        Returns:
            Always returns an absolute URL
        """
        # Use environment-based configuration for absolute URLs
        base_url = getattr(settings, "BASE_URL", None)
        if base_url:
            # Use configured BASE_URL
            return f"{base_url.rstrip('/')}{relative_url}"

        # Fallback to localhost for development
        return f"http://localhost:8000{relative_url}"

    def save_image(
        self,
        image_data: bytes,
        filename: str = None,
        file_extension: str = "png",
        return_uuid: bool = False,
    ) -> str:
        """
        Save image data as an artifact and return the URL or UUID.

        Args:
            image_data: Binary image data
            filename: Optional custom filename (without extension)
            file_extension: File extension (default: png)
            return_uuid: If True, return artifact UUID; if False, return URL

        Returns:
            Artifact UUID or URL path to the saved image
        """
        if filename is None:
            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"generated_image_{timestamp}_{unique_id}"

        # Ensure filename has correct extension
        if not filename.endswith(f".{file_extension}"):
            filename = f"{filename}.{file_extension}"

        try:
            # Create artifact instance and save file
            artifact = Artifacts()
            artifact.file.save(filename, ContentFile(image_data), save=True)

            if return_uuid:
                logger.info(f"Saved image artifact: {artifact.uuid}")
                return str(artifact.uuid)
            else:
                # Return absolute URL for external access
                file_url = self.build_absolute_url(artifact.file.url)
                logger.info(f"Saved image artifact: {artifact.uuid} -> {file_url}")
                return file_url

        except Exception as e:
            logger.error(f"Failed to save image artifact: {e}")
            raise

    def save_file(self, file_data: bytes, filename: str) -> str:
        """
        Save arbitrary file data as an artifact.

        Args:
            file_data: Binary file data
            filename: Filename with extension

        Returns:
            URL path to the saved file
        """
        try:
            # Create artifact instance and save file
            artifact = Artifacts()
            artifact.file.save(filename, ContentFile(file_data), save=True)

            # Return absolute URL for external access
            file_url = self.build_absolute_url(artifact.file.url)
            logger.info(f"Saved file artifact: {artifact.uuid} -> {file_url}")
            return file_url

        except Exception as e:
            logger.error(f"Failed to save file artifact: {e}")
            raise

    def get_artifact_by_uuid(self, artifact_uuid: str):
        """Get artifact instance by UUID."""
        try:
            return Artifacts.objects.get(uuid=artifact_uuid)
        except Artifacts.DoesNotExist:
            return None

    def delete_artifact(self, artifact_uuid: str) -> bool:
        """Delete an artifact by UUID."""
        try:
            artifact = Artifacts.objects.get(uuid=artifact_uuid)
            # Delete the file from storage
            if artifact.file:
                artifact.file.delete()
            # Delete the database record
            artifact.delete()
            logger.info(f"Deleted artifact: {artifact_uuid}")
            return True
        except Artifacts.DoesNotExist:
            logger.warning(f"Artifact not found: {artifact_uuid}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete artifact {artifact_uuid}: {e}")
            return False

    def create_image_content(self, artifact_uuid: str, use_binary: bool = True) -> "BinaryContent | ImageUrl":
        """
        Create appropriate pydantic-ai content type from saved artifact.

        Args:
            artifact_uuid: UUID of the saved artifact
            use_binary: If True, return BinaryContent; if False, return ImageUrl

        Returns:
            BinaryContent or ImageUrl instance for pydantic-ai
        """
        artifact = self.get_artifact_by_uuid(artifact_uuid)
        if not artifact:
            raise ValueError(f"Artifact not found: {artifact_uuid}")

        if use_binary:
            # Return binary content directly - works around pydantic-ai ImageUrl bug
            with artifact.file.open("rb") as f:
                data = f.read()

            # Get media type from file extension using Python's mimetypes module
            media_type, _ = mimetypes.guess_type(artifact.file.name)
            if not media_type or not media_type.startswith("image/"):
                media_type = "image/png"  # Default fallback

            logger.info(f"Creating BinaryContent from artifact {artifact_uuid}: {len(data)} bytes, type: {media_type}")
            return BinaryContent(data=data, media_type=media_type)
        else:
            # Return absolute URL for external access
            image_url = self.build_absolute_url(artifact.file.url)
            logger.info(f"Creating ImageUrl from artifact {artifact_uuid}: {image_url}")
            return ImageUrl(url=image_url, force_download=True)
