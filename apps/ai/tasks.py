"""
Celery tasks for AI services.
"""

import logging

from celery import shared_task

from apps.ai.schemas import StoryIn, StoryTitleOut
from apps.ai.util.ai import AIEngine
from apps.ai.util.celery import JobTask
from apps.stories.models import Story

logger = logging.getLogger(__name__)


ai = AIEngine()


@shared_task(name="ai.story_title", base=JobTask)
def story_title(arg: StoryIn) -> StoryTitleOut:
    logger.info(f"story_title received: {arg} (type: {type(arg)})")
    story = Story.objects.get(uuid=arg.story_uuid)
    out = ai.prompt_completion("story_title.md", {"story": story})

    logger.info(f"story_title result: {out} (title: {out.title})")
    story.title = out
    story.save()
    return out
