"""
Common types for AI agents.
"""

from uuid import UUID

from google.genai import Client as GoogleClient

from apps.ai.services import ArtifactService
from apps.stories.services import StoryService


class StoryAgentDeps:
    """Container for all agent dependencies."""

    conversation_uuid: UUID | None
    story_uuid: UUID | None
    story_service: StoryService
    artifact_service: ArtifactService
    image_client: GoogleClient
    image_model: str
    # image_model_config: = GenerateContentConfig

    def __init__(
        self,
        conversation_uuid: UUID | None = None,
        *,
        story_uuid: UUID | None = None,
        page_uuid: UUID | None = None,
        image_model: str = "gemini-2.5-flash-image-preview",
    ) -> None:
        """
        Initialize agent dependencies.

        Args:
            conversation_uuid: UUID of the conversation (optional)
            story_uuid: UUID of the story (mutually exclusive with page_uuid)
            page_uuid: UUID of a page (mutually exclusive with story_uuid)
            image_model: Image generation model to use

        Raises:
            ValueError: If neither or both story_uuid and page_uuid are provided
        """
        if (story_uuid is None) == (page_uuid is None):
            raise ValueError("Must provide exactly one of story_uuid or page_uuid")

        self.conversation_uuid = conversation_uuid
        self.story_service = StoryService.load_from_page_uuid(page_uuid) if page_uuid else StoryService(uuid=story_uuid)
        self.story_uuid = self.story_service.uuid
        self.artifact_service = ArtifactService()
        self.image_client = GoogleClient()
        self.image_model = image_model
