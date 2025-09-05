"""
Celery tasks for AI services.
"""

import logging

from celery import shared_task
from django_eventstream import send_event

from apps.ai.schemas import StoryJob
from apps.ai.util.ai import AIEngine
from apps.ai.util.celery import JobTask
from apps.stories.models import Story

logger = logging.getLogger(__name__)


ai = AIEngine()


@shared_task(name="ai.story_title", base=JobTask)
def ai_story_title_job(payload: StoryJob) -> str:
    logger.info(f"story_title received: {payload} (type: {type(payload)})")
    story = Story.objects.get(uuid=payload.story_uuid)
    out = ai.prompt_completion("story_title.md", {"story": story})

    logger.info(f"story_title result: {out} (title: {out.title})")
    story.title = out
    story.save()
    send_event(story.channel, "get_story_title", "")
    return f"notified:{story.channel}:get_story_title"


@shared_task(name="ai.story_description", base=JobTask)
def ai_story_description_job(payload: StoryJob) -> str:
    logger.info(f"story_description received: {payload} (type: {type(payload)})")
    story = Story.objects.get(uuid=payload.story_uuid)
    out = ai.prompt_completion("story_description.md", {"story": story})

    logger.info(f"story_description result: {out}")
    story.description = out
    story.save()
    send_event(story.channel, "get_story_description", "")
    return f"notified:{story.channel}:get_story_description"
