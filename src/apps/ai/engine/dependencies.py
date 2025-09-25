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

    story_uuid: UUID | None
    story_service: StoryService
    # conversation_uuid: UUID | None
    # conversation_service: ConversationService
    artifact_service: ArtifactService
    image_client: GoogleClient
    image_model: str

    def __init__(
        self,
        *,
        conversation_uuid: UUID | None = None,
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
        logger.info(f"StoryAgentDeps.__init__({conversation_uuid}, {story_uuid}, {page_uuid}, {image_model})")
        if (story_uuid is None) == (page_uuid is None):
            raise ValueError("Must provide exactly one of story_uuid or page_uuid")

        logger.debug(f"Building story service <story_uuid({story_uuid}) | page_uuid({page_uuid})>")
        self.story_service = StoryService.load_from_page_uuid(page_uuid) if page_uuid else StoryService(uuid=story_uuid)
        self.story_uuid = self.story_service.uuid

        # TODO: Maybe add user id as a story attribute?

        # if conversation_uuid:
        #     logger.debug(f"Using provided conversation UUID: {conversation_uuid}")
        #     self.conversation_uuid = conversation_uuid
        #     self.conversation_service = ConversationService(uuid=conversation_uuid)
        # elif self.story_service.get_story().conversation_uuid:
        #     logger.debug(f"Using story conversation UUID: {self.story_service.get_story().conversation_uuid}")
        #     self.conversation_uuid = self.story_service.get_story().conversation_uuid
        #     self.conversation_service = ConversationService(uuid=self.conversation_uuid)
        # else:
        #     logger.debug("Creating new conversation")
        #     logger.debug(f"New Conversation w/ user_id <{self.story_service.story_obj().user_id}>")
        #     self.user_id = self.story_service.story_obj().user_id
        #     self.conversation_service = ConversationService.create_conversation(
        #         user_id=self.user_id,
        #         meta={"story_uuid": self.story_uuid},
        #     )

        logger.debug("Initializing artifact service, image client, and image model")
        self.artifact_service = ArtifactService()
        self.image_client = GoogleClient()
        self.image_model = image_model
