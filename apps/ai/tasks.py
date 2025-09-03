"""
Celery tasks for AI services.
"""

import logging

from celery import shared_task

from apps.ai.engine import AIEngine
from apps.ai.models import AIRequest

logger = logging.getLogger(__name__)


ai = AIEngine()


@shared_task
def story_title(request_uuid: str):
    request = AIRequest.objects.get(uuid=request_uuid)
    request.status = AIRequest.Status.RUNNING
    request.save(update_fields=["status"])

    try:
        story = request.target
        out = ai.prompt_completion("story_title.md", {"story": story})
        request.output_text = out
        request.status = AIRequest.Status.SUCCESS
        request.save(update_fields=["status", "output_text"])
        return out
    except Exception as e:
        request.error_message = str(e)
        request.status = AIRequest.Status.FAILED
        request.save(update_fields=["status", "error_message"])
        raise e


@shared_task
def page_content(request_uuid: str):
    request = AIRequest.objects.get(uuid=request_uuid)
    request.status = AIRequest.Status.RUNNING
    request.save(update_fields=["status"])

    try:
        page = request.target
        out = ai.prompt_completion("page_content.md", {"page": page})
        print(out)
        request.output_text = out
        request.status = AIRequest.Status.SUCCESS
        request.save(update_fields=["status", "output_text"])
        return out
    except Exception as e:
        request.error_message = str(e)
        request.status = AIRequest.Status.FAILED
        request.save(update_fields=["status", "error_message"])
        raise e
