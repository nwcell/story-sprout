import logging

from django.http import HttpResponse
from ninja import Router

from apps.ai.schemas import JobStatus, PageJob, StoryJob
from apps.ai.util.celery import enqueue_job

router = Router()
logger = logging.getLogger(__name__)


# TODO: Add Auth
@router.post("/jobs/story/title/suggest")
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


# TODO: Add Auth
@router.post("/jobs/story/description/suggest")
def ai_story_description(request, payload: StoryJob) -> JobStatus:
    # API validates via Pydantic (Ninja) here; Celery validates again at run time.
    logger.info(f"ai_story_description received: {payload} (type: {type(payload)})")
    job = enqueue_job(
        user=request.user,
        workflow="ai.story_description",
        payload=payload,
    )
    if request.htmx:
        return HttpResponse(status=204)
    return {"job_uuid": str(job.uuid), "status": job.status}


# TODO: Add Auth
@router.post("/jobs/story/brainstorm")
def ai_story_brainstorm(request, payload: StoryJob) -> JobStatus:
    # API validates via Pydantic (Ninja) here; Celery validates again at run time.
    logger.info(f"ai_story_brainstorm received: {payload} (type: {type(payload)})")
    job = enqueue_job(
        user=request.user,
        workflow="ai.story_brainstorm",
        payload=payload,
    )
    if request.htmx:
        return HttpResponse(status=204)
    return {"job_uuid": str(job.uuid), "status": job.status}


@router.post("/jobs/page/content/suggest")
def ai_page_content(request, payload: PageJob) -> JobStatus:
    # API validates via Pydantic (Ninja) here; Celery validates again at run time.
    logger.info(f"ai_page_content received: {payload} (type: {type(payload)})")
    job = enqueue_job(
        user=request.user,
        workflow="ai.page_content",
        payload=payload,
    )
    if request.htmx:
        return HttpResponse(status=204)
    return {"job_uuid": str(job.uuid), "status": job.status}


@router.post("/jobs/page/image_text/suggest")
def ai_page_image_text(request, payload: PageJob) -> JobStatus:
    # API validates via Pydantic (Ninja) here; Celery validates again at run time.
    logger.info(f"ai_page_image_text received: {payload} (type: {type(payload)})")
    job = enqueue_job(
        user=request.user,
        workflow="ai.page_image_text",
        payload=payload,
    )
    if request.htmx:
        return HttpResponse(status=204)
    return {"job_uuid": str(job.uuid), "status": job.status}


@router.post("/jobs/page/image/generate")
def ai_page_image_generate(request, payload: PageJob) -> JobStatus:
    # API validates via Pydantic (Ninja) here; Celery validates again at run time.
    logger.info(f"ai_page_image_generate received: {payload} (type: {type(payload)})")
    job = enqueue_job(
        user=request.user,
        workflow="ai.page_image",
        payload=payload,
    )
    if request.htmx:
        return HttpResponse(status=204)
    return {"job_uuid": str(job.uuid), "status": job.status}
