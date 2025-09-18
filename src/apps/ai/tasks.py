"""
Celery tasks for AI services.
"""

import json
import logging

from celery import shared_task

from apps.ai.engine.agents import get_agent
from apps.ai.engine.celery import JobTask
from apps.ai.engine.types import AgentDependencies
from apps.ai.models import Conversation, Message
from apps.ai.schemas import PageJob, RequestSchema, StoryJob
from apps.ai.util.ai import AIEngine
from apps.stories.services import StoryService

logger = logging.getLogger(__name__)

ai = AIEngine()


@shared_task(name="ai.agent_task")
def agent_task(payload: RequestSchema) -> str:
    """Orchestrate pydantic-ai agent conversation."""
    logger.info(f"🚀 TASK STARTING: agent_orchestration - {payload}")
    logger.info(f"agent_orchestration received: {payload}")

    # Parse payload
    conversation_uuid = payload.conversation_uuid
    agent_type = payload.agent
    prompt = payload.prompt

    # Get conversation and build message history
    conversation = Conversation.objects.get(uuid=conversation_uuid)
    django_messages = list(conversation.messages.all().order_by("position"))

    # Convert Django messages to pydantic-ai ModelMessage objects
    messages = None
    if django_messages:
        from pydantic_ai.messages import ModelMessagesTypeAdapter

        # Extract content (which contains the serialized ModelMessage data)
        message_contents = [msg.content for msg in django_messages]
        # Convert back to ModelMessage objects for pydantic-ai
        messages = ModelMessagesTypeAdapter.validate_python(message_contents)

    # Run agent with prompt (sync version)
    agent = get_agent(agent_type)
    deps = AgentDependencies(conversation_uuid=conversation_uuid)
    result = agent.run_sync(prompt, deps=deps, message_history=messages)
    logger.info(f"agent_orchestration result: {result}")

    # Create messages using bulk_create - database trigger handles position assignment
    new_messages_json = result.new_messages_json()
    if new_messages_json:
        # Decode JSON bytes to Python objects for storage
        messages_data = json.loads(new_messages_json.decode("utf-8"))
        logger.info(f"agent_orchestration creating {len(messages_data)} messages")
        messages_to_create = [Message(conversation=conversation, content=msg_data) for msg_data in messages_data]
        Message.objects.bulk_create(messages_to_create)

    logger.info(f"agent_orchestration completed for conversation {conversation_uuid}")
    return f"Conversation {conversation_uuid} updated"


@shared_task(name="ai.story_title", base=JobTask)
def ai_story_title_job(payload: StoryJob) -> str:
    logger.info(f"story_title received: {payload} (type: {type(payload)})")
    story_service = StoryService(uuid=payload.story_uuid)
    story_obj = story_service.story_obj()
    out = ai.prompt_completion("story_title.md", {"story": story_obj})

    logger.info(f"story_title result: {out}")
    story_service.set_title(input=out)
    return f"job:{story_obj.channel}:ai_story_title_job"


@shared_task(name="ai.story_description", base=JobTask)
def ai_story_description_job(payload: StoryJob) -> str:
    logger.info(f"story_description received: {payload} (type: {type(payload)})")
    story_service = StoryService(uuid=payload.story_uuid)
    story_obj = story_service.story_obj()
    out = ai.prompt_completion("story_description.md", {"story": story_obj})
    logger.info(f"story_description result: {out}")
    story_service.set_description(input=out)
    return f"job:{story_obj.channel}:ai_story_description_job"


@shared_task(name="ai.story_brainstorm", base=JobTask)
def ai_story_brainstorm_job(payload: StoryJob) -> str:
    logger.info(f"story_brainstorm received: {payload} (type: {type(payload)})")
    story_service = StoryService(uuid=payload.story_uuid)
    story_obj = story_service.story_obj()
    out = ai.prompt_completion("story_brainstorm.md", {"story": story_obj})

    logger.info(f"story_brainstorm result: {out}")
    story_service.set_description(input=out)

    # Let's update the title, do reflect the new description!
    ai_story_title_job.apply_async(args=(payload,))
    return f"job:{story_obj.channel}:ai_story_brainstorm_job"


@shared_task(name="ai.page_content", base=JobTask)
def ai_page_content_job(payload: PageJob) -> str:
    logger.info(f"page_content received: {payload} (type: {type(payload)})")
    story_service = StoryService.load_from_page_uuid(payload.page_uuid)
    page_obj = story_service.get_page_obj(payload.page_uuid)
    out = ai.prompt_completion("page_content.md", {"page": page_obj, "generation_type": "content"})

    logger.info(f"page_content result: {out}")
    story_service.set_page_content(page_key=payload.page_uuid, input=out)
    return f"job:{page_obj.story.channel}:ai_page_content_job"


@shared_task(name="ai.page_image_text", base=JobTask)
def ai_page_image_text_job(payload: PageJob) -> str:
    logger.info(f"page_image_text received: {payload} (type: {type(payload)})")
    story_service = StoryService.load_from_page_uuid(payload.page_uuid)
    page_obj = story_service.get_page_obj(payload.page_uuid)
    out = ai.prompt_completion("page_image_text.md", {"page": page_obj})

    logger.info(f"page_image_text result: {out}")
    story_service.set_page_image_text(page_key=payload.page_uuid, input=out)
    return f"job:{page_obj.story.channel}:ai_page_image_text_job"


@shared_task(name="ai.page_image", base=JobTask)
def ai_page_image_job(payload: PageJob) -> str:
    logger.info(f"page_image received: {payload} (type: {type(payload)})")
    story_service = StoryService.load_from_page_uuid(payload.page_uuid)
    page_obj = story_service.get_page_obj(payload.page_uuid)

    # If no image_text, generate it first
    if not page_obj.image_text:
        logger.info(f"No image_text for page {page_obj.uuid}, generating image text first")
        ai_page_image_text_job(payload)
        # Refresh page to get the newly generated image_text
        story_service = StoryService.load_from_page_uuid(payload.page_uuid)
        page_obj = story_service.get_page_obj(payload.page_uuid)

    out = ai.generate_image(page_obj.image_text)

    logger.info(f"page_image result: {out}")
    if out:
        story_service.set_page_image(page_key=payload.page_uuid, image_data=out)
    return f"job:{page_obj.story.channel}:ai_page_image_job"
