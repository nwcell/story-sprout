"""
Common types for AI agents.
"""

import logging
from uuid import UUID

from google.genai import Client as GoogleClient

from apps.ai.services import ArtifactService
from apps.stories.services import StoryService

logger = logging.getLogger(__name__)


class StoryAgentDeps:
    """Container for all agent dependencies."""

    user_id: int
    story_uuid: UUID | None
    story_service: StoryService
    artifact_service: ArtifactService
    image_client: GoogleClient
    image_model: str

    def __init__(
        self,
        user_id: int,
        *,
        conversation_uuid: UUID | None = None,
        story_uuid: UUID | None = None,
        page_uuid: UUID | None = None,
        image_model: str = "gemini-2.5-flash-image-preview",
    ) -> None:
        """
        Initialize agent dependencies.

        Args:
            user_id: ID of the user
            conversation_uuid: UUID of the conversation (optional)
            story_uuid: UUID of the story (mutually exclusive with page_uuid)
            page_uuid: UUID of a page (mutually exclusive with story_uuid)
            image_model: Image generation model to use

        Raises:
            ValueError: If neither or both story_uuid and page_uuid are provided
            PermissionError: If the user does not have permission to access the story
        """
        logger.info(
            f"StoryAgentDeps.__init__(user_id={user_id}, conv={conversation_uuid}, "
            f"story={story_uuid}, page={page_uuid}, model={image_model})"
        )
        if (story_uuid is None) == (page_uuid is None):
            raise ValueError("Must provide exactly one of story_uuid or page_uuid")

        logger.debug(f"Building story service <story_uuid({story_uuid}) | page_uuid({page_uuid})>")
        self.story_service = (
            StoryService.load_from_page_uuid(page_uuid) if page_uuid else StoryService(uuid=story_uuid)
        )
        self.story_uuid = self.story_service.uuid
        self.user_id = user_id

        logger.debug("Initializing artifact service, image client, and image model")
        self.artifact_service = ArtifactService()
        self.image_client = GoogleClient()
        self.image_model = image_model

        # Verify user has access to the story
        self._auth()

    def _auth(self) -> None:
        """
        Verify that the user has permission to access this story.

        Raises:
            PermissionError: If the user does not own the story
        """
        story = self.story_service.story_obj()
        if story.user_id != self.user_id:
            logger.warning(
                f"Permission denied: user {self.user_id} attempted to access story {self.story_uuid} "
                f"owned by user {story.user_id}"
            )
            raise PermissionError(f"User {self.user_id} does not have permission to access story {self.story_uuid}")
