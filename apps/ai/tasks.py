"""
Celery tasks for AI services.
"""

import logging

from celery import shared_task

from apps.ai.schemas import StoryJob
from apps.ai.util.ai import AIEngine
from apps.ai.util.celery import JobTask
from apps.stories.models import Story
from apps.stories.services import set_description_and_notify, set_title_and_notify

logger = logging.getLogger(__name__)


ai = AIEngine()


@shared_task(name="ai.story_title", base=JobTask)
def ai_story_title_job(payload: StoryJob) -> str:
    logger.info(f"story_title received: {payload} (type: {type(payload)})")
    story = Story.objects.get(uuid=payload.story_uuid)
    out = ai.prompt_completion("story_title.md", {"story": story})

    logger.info(f"story_title result: {out} (title: {out.title})")
    set_title_and_notify(story, out)
    return f"job:{story.channel}:ai_story_title_job"


@shared_task(name="ai.story_description", base=JobTask)
def ai_story_description_job(payload: StoryJob) -> str:
    logger.info(f"story_description received: {payload} (type: {type(payload)})")
    story = Story.objects.get(uuid=payload.story_uuid)
    out = ai.prompt_completion("story_description.md", {"story": story})

    logger.info(f"story_description result: {out}")
    set_description_and_notify(story, out)
    return f"job:{story.channel}:ai_story_description_job"


@shared_task(name="ai.story_brainstorm", base=JobTask)
def ai_story_brainstorm_job(payload: StoryJob) -> str:
    logger.info(f"story_brainstorm received: {payload} (type: {type(payload)})")
    story = Story.objects.get(uuid=payload.story_uuid)
    out = ai.prompt_completion("story_brainstorm.md", {"story": story})

    logger.info(f"story_brainstorm result: {out}")
    set_description_and_notify(story, out)

    # Let's update the title, do reflect the new description!
    ai_story_title_job.delay(payload)
    return f"job:{story.channel}:ai_story_brainstorm_job"
