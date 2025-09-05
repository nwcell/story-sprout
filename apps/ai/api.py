import logging

from django.http import HttpResponse
from ninja import Router

from apps.ai.schemas import JobStatus, StoryJob
from apps.ai.util.celery import enqueue_job

router = Router()
logger = logging.getLogger(__name__)


# TODO: Add Auth
@router.post("/jobs/story-title")
def ai_story_title(request, payload: StoryJob) -> JobStatus:
    # API validates via Pydantic (Ninja) here; Celery validates again at run time.
    logger.info(f"ai_story_title received: {payload} (type: {type(payload)})")
    job = enqueue_job(
        user=request.user,
        workflow="ai.story_title",
        payload=payload,
    )
    if request.htmx:
        return HttpResponse(status=204)
    return {"job_uuid": str(job.uuid), "status": job.status}
