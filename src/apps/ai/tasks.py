"""
Celery tasks for AI services.
"""

import json
import logging
from textwrap import dedent

from celery import shared_task

from apps.ai.engine.agents import writer_agent
from apps.ai.engine.celery import JobTask
from apps.ai.engine.dependencies import StoryAgentDeps
from apps.ai.models import Conversation, Message
from apps.ai.types import PageJob, StoryJob, TaskPayload
from apps.ai.util.ai import AIEngine
from apps.stories.services import StoryService

logger = logging.getLogger(__name__)

ai = AIEngine()


@shared_task(name="ai.agent_task")
def agent_task(payload: dict) -> str:
    """Orchestrate pydantic-ai agent conversation."""
    # Deserialize payload with proper type discrimination
    task_payload = TaskPayload.model_validate(payload)
    logger.info(f"🚀 TASK STARTING: agent_orchestration - {task_payload}")

    # Parse payload
    conversation_uuid = task_payload.chat_request.conversation_uuid
    agent = writer_agent
    message = task_payload.chat_request.message

    # Get conversation and build message history
    conversation = Conversation.objects.get(uuid=conversation_uuid)

    # Run agent with message (sync version)
    deps = StoryAgentDeps(
        user_id=task_payload.user.user_id,
        conversation_uuid=conversation_uuid,
        story_uuid=conversation.meta["story_uuid"]
    )

    result = agent.run_sync(
        message,
        deps=deps,
        message_history=conversation.model_messages,
    )
    logger.info(f"agent_orchestration result: {result}")

    # Create messages using bulk_create - database trigger handles position assignment
    new_messages_json = result.new_messages_json()
    if new_messages_json:
        # Decode JSON bytes to Python objects for storage
        messages_data = json.loads(new_messages_json.decode("utf-8"))
        logger.info(f"agent_orchestration creating {len(messages_data)} messages")
        messages_to_create = [Message(conversation=conversation, content=msg_data) for msg_data in messages_data]
        Message.objects.bulk_create(messages_to_create)

    logger.info(f"agent_orchestration completed with {repr(result.output)}")
    return f"Conversation {conversation_uuid} updated"


@shared_task(name="ai.story_title", base=JobTask)
def ai_story_title_job(payload: dict) -> str:
    # Deserialize payload with proper type discrimination
    task_payload = TaskPayload.model_validate(payload)
    if not isinstance(task_payload.job, StoryJob):
        raise ValueError("ai_story_title_job requires StoryJob")

    logger.info(f"story_title received: {task_payload} (type: {type(task_payload)})")
    prompt = dedent("""\
        Create a fun, catchy title for this children's picture book.

        Instructions:
        1. First, get the current story information to understand the content
        2. Create a title that is:
        - Kid-friendly: Simple, playful language for ages 2-3
        - Captures the story: Reflects main theme, character, or adventure
        - Light and fun: Whimsical and engaging, avoid scary themes
        - Memorable: Use rhythm, rhyme, or alliteration when possible
        - Concise: 2-5 words only
        - Different from current title (if one exists)
        3. Use the update_story tool to set the new title
        4. Once you've successfully updated the title, your task is complete

        Do not provide additional output after using the update_story tool.
    """)
    agent = writer_agent
    deps = StoryAgentDeps(
        user_id=task_payload.user.user_id,
        conversation_uuid=None,
        story_uuid=task_payload.job.story_uuid
    )
    result = agent.run_sync(prompt, deps=deps)
    logger.info(f"story_title result: {result}")
    return f"task:ai_story_title_job:{task_payload.job.story_uuid}"


@shared_task(name="ai.story_description", base=JobTask)
def ai_story_description_job(payload: dict) -> str:
    # Deserialize payload with proper type discrimination
    task_payload = TaskPayload.model_validate(payload)
    if not isinstance(task_payload.job, StoryJob):
        raise ValueError("ai_story_description_job requires StoryJob")

    logger.info(f"story_description received: {task_payload} (type: {type(task_payload)})")
    prompt = dedent("""\
        Create a complete story arc with clear beginning, middle, and end for this children's picture book.

        Instructions:
        1. First, get the story information to understand the overall narrative
        2. Create a structured story outline that:
        - Has a simple, clear plot for 2-3 year olds
        - Includes gentle conflict and positive resolution
        - Features relatable, charming characters
        - Has visual potential for illustrations
        3. Format the story arc as:
        Summary: (One compelling sentence summarizing the entire story)

        Beginning: (1-2 sentences introducing characters and problem)

        Middle: (2-3 sentences describing the adventure and challenges)

        End: (1-2 sentences describing resolution and happy ending)

        4. Use the update_story tool to set the formatted story arc as the description
        5. Once you've successfully updated the description, your task is complete

        Do not provide additional output after using the update_story tool.
    """)
    agent = writer_agent
    deps = StoryAgentDeps(
        user_id=task_payload.user.user_id,
        conversation_uuid=None,
        story_uuid=task_payload.job.story_uuid
    )
    result = agent.run_sync(prompt, deps=deps)
    logger.info(f"story_description result: {result}")
    return f"task:ai_story_description_job:{task_payload.job.story_uuid}"


@shared_task(name="ai.story_brainstorm", base=JobTask)
def ai_story_brainstorm_job(payload: dict) -> str:
    # Deserialize payload with proper type discrimination
    task_payload = TaskPayload.model_validate(payload)
    if not isinstance(task_payload.job, StoryJob):
        raise ValueError("ai_story_brainstorm_job requires StoryJob")

    logger.info(f"story_brainstorm received: {task_payload} (type: {type(task_payload)})")
    prompt = dedent("""\
        Generate a completely original, creative story concept for a children's picture book from scratch.

        Instructions:
        1. Create something completely fresh and imaginative:
        - Combine familiar elements in surprising ways
        - Think beyond typical picture book scenarios
        - Create unique, memorable characters (animals, objects, children, fantasy beings)
        - Use magical realism or creative problem-solving themes
        2. Make it age-appropriate for 2-3 year olds:
        - Simple but engaging conflicts with positive resolutions
        - Gentle humor and playfulness
        - Visual storytelling potential
        3. Format the original story concept as:
        Summary: (One compelling sentence summarizing the entire story)

        Beginning: (1-2 sentences introducing characters and problem)

        Middle: (2-3 sentences describing the adventure and challenges)

        End: (1-2 sentences describing resolution and happy ending)

        4. Use the update_story tool to set this formatted concept as the description
        5. Once you've successfully updated the description, your task is complete

        Do not provide additional output after using the update_story tool.
    """)
    agent = writer_agent
    deps = StoryAgentDeps(
        user_id=task_payload.user.user_id,
        conversation_uuid=None,
        story_uuid=task_payload.job.story_uuid
    )
    result = agent.run_sync(prompt, deps=deps)
    logger.info(f"story_brainstorm result: {result}")

    # Let's update the title to reflect the new description!
    ai_story_title_job.apply_async(kwargs={"payload": payload})
    return f"task:ai_story_brainstorm_job:{task_payload.job.story_uuid}"


@shared_task(name="ai.page_content", base=JobTask)
def ai_page_content_job(payload: dict) -> str:
    # Deserialize payload with proper type discrimination
    task_payload = TaskPayload.model_validate(payload)
    if not isinstance(task_payload.job, PageJob):
        raise ValueError("ai_page_content_job requires PageJob")

    logger.info(f"page_content received: {task_payload} (type: {type(task_payload)})")

    # Get page context first to determine page number and story
    story_service = StoryService.load_from_page_uuid(task_payload.job.page_uuid)
    page_obj = story_service.get_page_obj(task_payload.job.page_uuid)
    prompt = dedent(f"""\
        Write and save content for page {page_obj.page_number} of this children's picture book.

        Instructions:
        1. First, get the story information to understand the overall narrative
        2. Get the current page information for page {page_obj.page_number}
        to understand the page's role in the story:
        - Beginning (first 25% of pages): Introduce characters, setting, and main problem
        - Middle (middle 50% of pages): Develop adventure and build toward turning point
        - End (last 25% of pages): Resolve problem and provide happy conclusion
        4. Write content that:
        - Directly advances the story arc from previous page
        - Maintains narrative flow and logical progression
        - Uses simple, engaging language for 2-3 year olds (1-3 short sentences)
        - Avoids repetition of previous page structure

        5. IMPORTANT: Use the update_page tool with page_num={page_obj.page_number} and your written content
        to save the content to the page. Do not just return text - you must use the tool.
        6. Once you've successfully updated the page content, your task is complete

        Do not provide additional output after using the update_page tool.
    """)

    agent = writer_agent
    deps = StoryAgentDeps(
        user_id=task_payload.user.user_id,
        conversation_uuid=None,
        page_uuid=task_payload.job.page_uuid
    )
    result = agent.run_sync(prompt, deps=deps)
    logger.info(f"page_content result: {result}")
    return f"task:ai_page_content_job:{task_payload.job.page_uuid}"


@shared_task(name="ai.page_image_text", base=JobTask)
def ai_page_image_text_job(payload: dict) -> str:
    # Deserialize payload with proper type discrimination
    task_payload = TaskPayload.model_validate(payload)
    if not isinstance(task_payload.job, PageJob):
        raise ValueError("ai_page_image_text_job requires PageJob")

    logger.info(f"page_image_text received: {task_payload} (type: {type(task_payload)})")

    # Get page context first to determine page number and story
    story_service = StoryService.load_from_page_uuid(task_payload.job.page_uuid)
    page_obj = story_service.get_page_obj(task_payload.job.page_uuid)
    prompt = dedent(f"""\
        Create and save a descriptive scene description for page {page_obj.page_number}
        of this children's picture book.

        Instructions:
        1. First, get the story information to understand the overall narrative
        2. Get the current page information for page {page_obj.page_number} including its content
        3. Create a purely descriptive scene that captures what should be visually depicted
        4. Focus on these scene elements:\n
         - Characters: Who is in the scene? What are they doing? What expressions?
         - Setting/Environment: Where does this take place? Physical environment?
         - Actions: What specific actions or movements are happening?
         - Objects/Props: What important objects or items are visible?
         - Composition: How are elements arranged? Foreground/background?
        5. Guidelines:
         - Be purely descriptive and objective
         - Do NOT include artistic style, mood, lighting, or color descriptions
         - Focus on WHAT is happening and WHERE, not HOW it should look
         - Keep it concise but detailed for accurate visual representation

        6. IMPORTANT: Use the update_page tool with page_num={page_obj.page_number} and
        image_text set to your scene description
        to save it to the page. Do not just return text - you must use the tool.
        7. Once you've successfully updated the page image_text, your task is complete

        Do not provide additional output after using the update_page tool.
    """)

    agent = writer_agent
    deps = StoryAgentDeps(
        user_id=task_payload.user.user_id,
        conversation_uuid=None,
        page_uuid=task_payload.job.page_uuid
    )
    result = agent.run_sync(prompt, deps=deps)
    logger.info(f"page_image_text result: {result}")
    return f"task:ai_page_image_text_job:{task_payload.job.page_uuid}"


@shared_task(name="ai.page_image", base=JobTask)
def ai_page_image_job(payload: dict) -> str:
    # Deserialize payload with proper type discrimination
    task_payload = TaskPayload.model_validate(payload)
    if not isinstance(task_payload.job, PageJob):
        raise ValueError("ai_page_image_job requires PageJob")

    logger.info(f"page_image received: {task_payload} (type: {type(task_payload)})")
    story_service = StoryService.load_from_page_uuid(task_payload.job.page_uuid)
    page_obj = story_service.get_page_obj(task_payload.job.page_uuid)
    page_num = page_obj.page_number

    # If no image_text, generate it first and return early
    if not page_obj.image_text:
        logger.info(f"No image_text for page {page_obj.uuid}, generating image text first")
        ai_page_image_text_job.apply_async(kwargs={"payload": payload})
        # Return early - the image generation will be triggered again after image_text is ready
        return f"task:ai_page_image_job:generating_image_text:{task_payload.job.page_uuid}"

    # Build focused prompt for image generation only
    content = page_obj.content or ""
    image_text = page_obj.image_text or ""

    enhanced_prompt = dedent(f"""\
        Generate an illustration for page {page_num} using the artist_request tool,
        then update the page image using update_page tool.

        Use this prompt for artist_request:
        Create a watercolor style illustration for page {page_num}.
        Scene description: {image_text}
        Include this text at the bottom of the image: '{content}'
        Review all previous pages to maintain consistent character designs, art style, colors,
        font style, and visual elements throughout the story.
        Style: watercolor painting with soft, flowing colors, child-friendly and whimsical,
        suitable for ages 2-3, with readable text at the bottom that matches previous pages.

        After generating the image, use update_page tool with page_num={page_num} and
        the image_url from artist_request. Do NOT modify the image_text field - only update the image.

        Once you've successfully generated the image and updated the page, respond with a simple
        confirmation that the task is complete. Keep your response brief.
    """)

    # Use the writer agent with generate_image tool
    deps = StoryAgentDeps(user_id=task_payload.user.user_id, page_uuid=task_payload.job.page_uuid)
    result = writer_agent.run_sync(enhanced_prompt, deps=deps)
    logger.info(f"page_image result: {result}")

    # The image generation and page update will be handled by the writer agent using tools
    # No need to manually extract and save images since the agent will use update_page tool

    return f"job:{page_obj.story.channel}:ai_page_image_job"
