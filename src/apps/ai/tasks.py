"""
Celery tasks for AI services.
"""

import json
import logging

from celery import shared_task

from apps.ai.engine.agents import get_agent, writer_agent
from apps.ai.engine.celery import JobTask
from apps.ai.engine.dependencies import StoryAgentDeps
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
    deps = StoryAgentDeps(conversation_uuid=conversation_uuid)
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
    prompt = (
        "Create a fun, catchy title for this children's picture book.\n\n"
        "Instructions:\n"
        "1. First, get the current story information to understand the content\n"
        "2. Create a title that is:\n"
        "   - Kid-friendly: Simple, playful language for ages 2-3\n"
        "   - Captures the story: Reflects main theme, character, or adventure\n"
        "   - Light and fun: Whimsical and engaging, avoid scary themes\n"
        "   - Memorable: Use rhythm, rhyme, or alliteration when possible\n"
        "   - Concise: 2-5 words only\n"
        "   - Different from current title (if one exists)\n"
        "3. Use the update_story tool to set the new title\n\n"
        "Provide just the title (2-5 words). No explanations or formatting."
    )
    agent = writer_agent
    deps = StoryAgentDeps(conversation_uuid=None, story_uuid=payload.story_uuid)
    result = agent.run_sync(prompt, deps=deps)
    logger.info(f"story_title result: {result}")
    return f"task:ai_story_title_job:{payload.story_uuid}"


@shared_task(name="ai.story_description", base=JobTask)
def ai_story_description_job(payload: StoryJob) -> str:
    logger.info(f"story_description received: {payload} (type: {type(payload)})")
    prompt = (
        "Create a complete story arc with clear beginning, middle, and end for this children's picture book.\n\n"
        "Instructions:\n"
        "1. First, get the current story information to understand existing content\n"
        "2. Create a structured story outline that:\n"
        "   - Has a simple, clear plot for 2-3 year olds\n"
        "   - Includes gentle conflict and positive resolution\n"
        "   - Features relatable, charming characters\n"
        "   - Has visual potential for illustrations\n"
        "3. Use the update_story tool to set the story arc as the description\n\n"
        "Format the story arc as:\n"
        "Summary: (One compelling sentence summarizing the entire story)\n\n"
        "Beginning: (1-2 sentences introducing characters and problem)\n\n"
        "Middle: (2-3 sentences describing the adventure and challenges)\n\n"
        "End: (1-2 sentences describing resolution and happy ending)\n\n"
        "No formatting or markdown - just plain text with the structure above."
    )
    agent = writer_agent
    deps = StoryAgentDeps(conversation_uuid=None, story_uuid=payload.story_uuid)
    result = agent.run_sync(prompt, deps=deps)
    logger.info(f"story_description result: {result}")
    return f"task:ai_story_description_job:{payload.story_uuid}"


@shared_task(name="ai.story_brainstorm", base=JobTask)
def ai_story_brainstorm_job(payload: StoryJob) -> str:
    logger.info(f"story_brainstorm received: {payload} (type: {type(payload)})")
    prompt = (
        "Generate a completely original, creative story concept for a children's picture book from scratch.\n\n"
        "Instructions:\n"
        "1. Create something completely fresh and imaginative:\n"
        "   - Combine familiar elements in surprising ways\n"
        "   - Think beyond typical picture book scenarios\n"
        "   - Create unique, memorable characters (animals, objects, children, fantasy beings)\n"
        "   - Use magical realism or creative problem-solving themes\n"
        "2. Make it age-appropriate for 2-3 year olds:\n"
        "   - Simple but engaging conflicts with positive resolutions\n"
        "   - Gentle humor and playfulness\n"
        "   - Visual storytelling potential\n"
        "3. Use the update_story tool to set this original concept as the description\n\n"
        "Format the original story concept as:\n"
        "Summary: (One compelling sentence summarizing the entire story)\n\n"
        "Beginning: (1-2 sentences introducing characters and problem)\n\n"
        "Middle: (2-3 sentences describing the adventure and challenges)\n\n"
        "End: (1-2 sentences describing resolution and happy ending)\n\n"
        "No formatting or markdown - just plain text with the structure above."
    )
    agent = writer_agent
    deps = StoryAgentDeps(conversation_uuid=None, story_uuid=payload.story_uuid)
    result = agent.run_sync(prompt, deps=deps)
    logger.info(f"story_brainstorm result: {result}")

    # Let's update the title to reflect the new description!
    ai_story_title_job.apply_async(args=(payload,))
    return f"task:ai_story_brainstorm_job:{payload.story_uuid}"


@shared_task(name="ai.page_content", base=JobTask)
def ai_page_content_job(payload: PageJob) -> str:
    logger.info(f"page_content received: {payload} (type: {type(payload)})")

    # Get page context first to determine page number and story
    story_service = StoryService.load_from_page_uuid(payload.page_uuid)
    page_obj = story_service.get_page_obj(payload.page_uuid)
    page_num = page_obj.page_number
    prompt = (
        f"Write content for page {page_num} of this children's picture book.\n\n"
        "Instructions:\n"
        "1. First, get the story information to understand the overall narrative\n"
        f"2. Get the current page information for page {page_num}\n"
        "3. Analyze the page's role in the story:\n"
        "   - Beginning (first 25% of pages): Introduce characters, setting, and main problem\n"
        "   - Middle (middle 50% of pages): Develop adventure and build toward turning point\n"
        "   - End (last 25% of pages): Resolve problem and provide happy conclusion\n"
        "4. Write content that:\n"
        "   - Directly advances the story arc from previous page\n"
        "   - Maintains narrative flow and logical progression\n"
        "   - Uses simple, engaging language for 2-3 year olds (1-3 short sentences)\n"
        "   - Avoids repetition of previous page structure\n"
        f"5. Use the update_page tool to set the content for page {page_num}\n\n"
        "Provide ONLY the 1-3 sentences of text for the page. No commentary or formatting."
    )

    agent = writer_agent
    deps = StoryAgentDeps(conversation_uuid=None, page_uuid=payload.page_uuid)
    result = agent.run_sync(prompt, deps=deps)
    logger.info(f"page_content result: {result}")
    return f"task:ai_page_content_job:{payload.page_uuid}"


@shared_task(name="ai.page_image_text", base=JobTask)
def ai_page_image_text_job(payload: PageJob) -> str:
    logger.info(f"page_image_text received: {payload} (type: {type(payload)})")

    # Get page context first to determine page number and story
    story_service = StoryService.load_from_page_uuid(payload.page_uuid)
    page_obj = story_service.get_page_obj(payload.page_uuid)
    page_num = page_obj.page_number

    prompt = (
        f"Create a descriptive scene description for page {page_num} of this children's picture book.\n\n"
        "Instructions:\n"
        "1. First, get the story information to understand the overall narrative\n"
        f"2. Get the current page information for page {page_num} including its content\n"
        "3. Create a purely descriptive scene that captures what should be visually depicted\n"
        "4. Focus on these scene elements:\n"
        "   - Characters: Who is in the scene? What are they doing? What expressions?\n"
        "   - Setting/Environment: Where does this take place? Physical environment?\n"
        "   - Actions: What specific actions or movements are happening?\n"
        "   - Objects/Props: What important objects or items are visible?\n"
        "   - Composition: How are elements arranged? Foreground/background?\n"
        "5. Guidelines:\n"
        "   - Be purely descriptive and objective\n"
        "   - Do NOT include artistic style, mood, lighting, or color descriptions\n"
        "   - Focus on WHAT is happening and WHERE, not HOW it should look\n"
        "   - Keep it concise but detailed for accurate visual representation\n"
        f"6. Use the update_page tool to set the image_text for page {page_num}\n\n"
        "Provide a clear descriptive paragraph that objectively describes the scene."
    )

    agent = writer_agent
    deps = StoryAgentDeps(conversation_uuid=None, page_uuid=payload.page_uuid)
    result = agent.run_sync(prompt, deps=deps)
    logger.info(f"page_image_text result: {result}")
    return f"task:ai_page_image_text_job:{payload.page_uuid}"


@shared_task(name="ai.page_image", base=JobTask)
def ai_page_image_job(payload: PageJob) -> str:
    logger.info(f"page_image received: {payload} (type: {type(payload)})")
    story_service = StoryService.load_from_page_uuid(payload.page_uuid)
    page_obj = story_service.get_page_obj(payload.page_uuid)
    page_num = page_obj.page_number

    # If no image_text, generate it first
    if not page_obj.image_text:
        logger.info(f"No image_text for page {page_obj.uuid}, generating image text first")
        ai_page_image_text_job(payload)
        # Refresh page to get the newly generated image_text
        page_obj = story_service.get_page_obj(payload.page_uuid)
        page_num = page_obj.page_number

    # Build enhanced prompt for the image agent
    content = page_obj.content or ""
    text_instruction = f'Include this text at the bottom of the image: "{content}"' if content else ""

    enhanced_prompt = [
        f"Create a watercolor style illustration for page {page_num} of this children's picture book.\n\n"
        f"Scene description: {page_obj.image_text}\n\n"
        "Style requirements:\n"
        "- Watercolor painting style with soft, flowing colors\n"
        "- Child-friendly and whimsical aesthetic\n"
        "- Leave space at the bottom for text overlay\n"
        f"{text_instruction}\n"
        "- Suitable for ages 2-3\n\n"
        "Generate the illustration now."
    ]

    # Use the writer agent with generate_image tool
    deps = StoryAgentDeps(page_uuid=payload.page_uuid)
    result = writer_agent.run_sync("".join(enhanced_prompt), deps=deps)
    logger.info(f"page_image result: {result}")

    # The image generation and page update will be handled by the writer agent using tools
    # No need to manually extract and save images since the agent will use update_page tool

    return f"job:{page_obj.story.channel}:ai_page_image_job"
