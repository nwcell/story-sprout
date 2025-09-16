import logging
from uuid import UUID

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from ninja import Router

from apps.ai.models import Conversation
from apps.ai.schemas import ConversationDetailSchema, ConversationSchema, JobStatus, PageJob, RequestSchema, StoryJob
from apps.ai.util.celery import enqueue_job

router = Router()
logger = logging.getLogger(__name__)


@router.get("/agents", tags=["Agents"])
def agents(request) -> list[str]:
    _user = request.user
    return ["writer"]


@router.get("/conversations", response=list[ConversationSchema], tags=["Conversations"])
def list_conversations(request) -> list[ConversationSchema]:
    user = request.user
    return Conversation.objects.filter(user=user)


@router.get("/conversations/{conversation_uuid}", response=ConversationDetailSchema, tags=["Conversations"])
def get_conversations(request, conversation_uuid: UUID) -> ConversationDetailSchema:
    user = request.user
    conversation = get_object_or_404(Conversation, uuid=conversation_uuid, user=user)
    return conversation


@router.post("/request", response=ConversationSchema, tags=["Request"])
def create_request(request, payload: RequestSchema) -> ConversationSchema:
    user = request.user
    conversation = Conversation.objects.create(user=user)
    # Start running the workflow
    return conversation


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
