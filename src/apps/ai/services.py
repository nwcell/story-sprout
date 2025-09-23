"""
AI services for managing artifacts and AI-related operations.
"""

import logging
import mimetypes
import uuid
from datetime import datetime
from typing import Literal
from uuid import UUID

from attr import dataclass
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from pydantic_ai.messages import BinaryContent, ImageUrl

from apps.ai.models import Artifacts, Conversation

logger = logging.getLogger(__name__)

EmojiType = Literal[""]

ColorType = Literal[
    "pink",
    "rose",
    "purple",
    "violet",
    "indigo",
    "blue",
    "sky",
    "cyan",
    "teal",
    "emerald",
    "green",
    "lime",
    "yellow",
    "amber",
    "orange",
    "red",
    "neutral",
    "slate",
    "rainbow",
]


@dataclass
class Chip:
    emoji = Literal
    color = ColorType
    value = str


class ConversationFilter:
    uuid: UUID | None = None
    user: User | None = None
    title: str | None = None
    meta: dict | None = None


class ConversationService:
    def __init__(self, uuid: UUID, new_conversation: bool = False):
        self.uuid = uuid

    def list_conversations(self, filter):
        if filter.uuid:
            return Conversation.objects.get(uuid=filter.uuid)
        # elif title

    def get_conversation(self, filter):
        return Conversation.objects.get(uuid=self.uuid)

    def get_messages(self):
        return self.get_conversation().messages.all()


class ChatService:
    def __init__(self, conversation_uuid):
        self.conversation_uuid = conversation_uuid

    def update_prompt(self, input):
        pass

    def update_chips(self, chips):
        pass

    def update_freeform(self, freeform_on: bool = True):
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
