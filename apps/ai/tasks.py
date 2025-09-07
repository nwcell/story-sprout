"""
Celery tasks for AI services.
"""

import logging

from celery import shared_task

from apps.ai.schemas import PageJob, StoryJob
from apps.ai.util.ai import AIEngine
from apps.ai.util.celery import JobTask
from apps.stories.models import Page, Story
from apps.stories.services import (
    set_page_content_and_notify,
    set_page_image_and_notify,
    set_page_image_text_and_notify,
    set_story_description_and_notify,
    set_story_title_and_notify,
)

logger = logging.getLogger(__name__)


ai = AIEngine()


@shared_task(name="ai.story_title", base=JobTask)
def ai_story_title_job(payload: StoryJob) -> str:
    logger.info(f"story_title received: {payload} (type: {type(payload)})")
    story = Story.objects.get(uuid=payload.story_uuid)
    out = ai.prompt_completion("story_title.md", {"story": story})

    logger.info(f"story_title result: {out} (title: {out.title})")
    set_story_title_and_notify(story, out)
    return f"job:{story.channel}:ai_story_title_job"


@shared_task(name="ai.story_description", base=JobTask)
def ai_story_description_job(payload: StoryJob) -> str:
    logger.info(f"story_description received: {payload} (type: {type(payload)})")
    story = Story.objects.get(uuid=payload.story_uuid)
    out = ai.prompt_completion("story_description.md", {"story": story})

    logger.info(f"story_description result: {out}")
    set_story_description_and_notify(story, out)
    return f"job:{story.channel}:ai_story_description_job"


@shared_task(name="ai.story_brainstorm", base=JobTask)
def ai_story_brainstorm_job(payload: StoryJob) -> str:
    logger.info(f"story_brainstorm received: {payload} (type: {type(payload)})")
    story = Story.objects.get(uuid=payload.story_uuid)
    out = ai.prompt_completion("story_brainstorm.md", {"story": story})

    logger.info(f"story_brainstorm result: {out}")
    set_story_description_and_notify(story, out)

    # Let's update the title, do reflect the new description!
    ai_story_title_job.delay(payload)
    return f"job:{story.channel}:ai_story_brainstorm_job"


@shared_task(name="ai.page_content", base=JobTask)
def ai_page_content_job(payload: PageJob) -> str:
    logger.info(f"page_content received: {payload} (type: {type(payload)})")
    page = Page.objects.get(uuid=payload.page_uuid)
    out = ai.prompt_completion("page_content.md", {"page": page, "generation_type": "content"})

    logger.info(f"page_content result: {out}")
    set_page_content_and_notify(page, out)
    return f"job:{page.story.channel}:ai_page_content_job"


@shared_task(name="ai.page_image_text", base=JobTask)
def ai_page_image_text_job(payload: PageJob) -> str:
    logger.info(f"page_image_text received: {payload} (type: {type(payload)})")
    page = Page.objects.get(uuid=payload.page_uuid)
    out = ai.prompt_completion("page_image_text.md", {"page": page})

    logger.info(f"page_image_text result: {out}")
    set_page_image_text_and_notify(page, out)
    return f"job:{page.story.channel}:ai_page_image_text_job"


@shared_task(name="ai.page_image", base=JobTask)
def ai_page_image_job(payload: PageJob) -> str:
    logger.info(f"page_image received: {payload} (type: {type(payload)})")
    page = Page.objects.get(uuid=payload.page_uuid)

    # If no image_text, generate it first
    if not page.image_text:
        logger.info(f"No image_text for page {page.uuid}, generating image text first")
        ai_page_image_text_job(payload)
        # Refresh page to get the newly generated image_text
        page.refresh_from_db()

    out = ai.generate_image(page.image_text)

    logger.info(f"page_image result: {out}")
    if out:
        set_page_image_and_notify(page, out)
    return f"job:{page.story.channel}:ai_page_image_job"
