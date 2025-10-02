import logging
from typing import Annotated
from uuid import UUID

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from ninja import File, Form, Query, Router, UploadedFile
from pydantic import BaseModel

from apps.ai.engine.celery import enqueue_job
from apps.ai.models import Artifacts, Conversation
from apps.ai.schemas import JobStatus
from apps.ai.schemas import PageJob as OldPageJob
from apps.ai.schemas import StoryJob as OldStoryJob
from apps.ai.services import ConversationDetailSchema, ConversationSchema, ConversationService
from apps.ai.types import ChatRequest, PageJob, StoryJob

router = Router()
logger = logging.getLogger(__name__)


class CreateConversationSchema(BaseModel):
    title: str | None = None
    meta: dict | None = None


# @router.get("/agents", tags=["Agents"])
# def agents(request) -> list[str]:
#     _user = request.user
#     logger.info(f"API: agents endpoint called by user {_user}")
#     logger.debug("API: Getting agent types list")
#     return list_agent_types()


@router.get("/conversations", response=list[ConversationSchema], tags=["Conversations"])
def list_conversations(
    request,
    title: Annotated[str | None, Query(description="Filter by title (substring match)")] = None,
) -> list[ConversationSchema]:
    """List conversations with optional filtering by title and meta key-value pairs.

    Meta filtering uses deepobject style: meta[key]=value
    Examples:
    - ?title=my story&meta[story_uuid]=12345&meta[status]=draft
    - ?meta[category]=stories&meta[author]=john&meta[priority]=high
    """
    # Parse meta parameters from deepobject style: meta[key]=value
    meta = {}
    for param_name, param_value in request.GET.items():
        if param_name.startswith("meta[") and param_name.endswith("]"):
            key = param_name[5:-1]  # Extract key from meta[key]
            meta[key] = param_value
    meta_filter = meta if meta else None
    logger.info(
        f"API: list_conversations endpoint called by user {request.user} with title {title} and meta {meta_filter}"
    )
    conversation_service = ConversationService(uuid=None)
    return conversation_service.list_conversations(user_id=request.user.id, title=title, meta=meta_filter)


@router.post("/conversations", response=ConversationSchema, tags=["Conversations"])
def create_conversation(request, payload: CreateConversationSchema) -> ConversationSchema:
    conversation_service = ConversationService.create_conversation(
        user_id=request.user.id, title=payload.title, meta=payload.meta
    )
    return conversation_service.get_conversation()


@router.get("/conversations/{conversation_uuid}", response=ConversationDetailSchema, tags=["Conversations"])
def get_conversations(request, conversation_uuid: UUID) -> ConversationDetailSchema:
    conversation_service = ConversationService(uuid=conversation_uuid)
    conversation = conversation_service.get_conversation()
    if conversation.user_id != request.user.id:
        raise Http404("Conversation not found")
    return conversation


@router.post("/chat", response=None, tags=["Chat"])
def send_chat(
    request,
    payload: Form[ChatRequest],
    files: list[UploadedFile] | None = File(None),
) -> None:
    logger.info(f"send_chat received: {payload}")
    user = request.user

    # Validate conversation ownership
    get_object_or_404(Conversation, uuid=payload.conversation_uuid, user=request.user)

    # Handle image uploads
    artifact_uuids = []
    if files:
        for file in files:
            # Validate file type
            if file.content_type not in ["image/jpeg", "image/png", "image/webp", "image/jpg"]:
                logger.warning(f"Invalid file type received: {file.content_type}")
                continue
            artifact = Artifacts.objects.create(file=file)
            artifact_uuids.append(artifact.uuid)

    # Enqueue agent orchestration task
    logger.info(f"send_chat enqueuing agent task: {payload}")
    chat_request = ChatRequest(
        conversation_uuid=payload.conversation_uuid,
        message=payload.message,
        artifact_uuids=artifact_uuids,
    )
    enqueue_job(user=user, workflow="ai.agent_task", chat_request=chat_request)

    return HttpResponse(status=204)


# TODO: Add Auth
@router.post("/jobs/story/title/suggest")
def ai_story_title(request, payload: OldStoryJob) -> JobStatus:
    # API validates via Pydantic (Ninja) here; Celery validates again at run time.
    logger.info(f"ai_story_title received: {payload} (type: {type(payload)})")
    chat_request = ChatRequest()
    story_job = StoryJob(story_uuid=payload.story_uuid)
    job = enqueue_job(
        user=request.user,
        workflow="ai.story_title",
        chat_request=chat_request,
        job=story_job,
    )
    if request.htmx:
        return HttpResponse(status=204)
    return {"job_uuid": str(job.uuid), "status": job.status}


# TODO: Add Auth
@router.post("/jobs/story/description/suggest")
def ai_story_description(request, payload: OldStoryJob) -> JobStatus:
    # API validates via Pydantic (Ninja) here; Celery validates again at run time.
    logger.info(f"ai_story_description received: {payload} (type: {type(payload)})")
    chat_request = ChatRequest()
    story_job = StoryJob(story_uuid=payload.story_uuid)
    job = enqueue_job(
        user=request.user,
        workflow="ai.story_description",
        chat_request=chat_request,
        job=story_job,
    )
    if request.htmx:
        return HttpResponse(status=204)
    return {"job_uuid": str(job.uuid), "status": job.status}


# TODO: Add Auth
@router.post("/jobs/story/brainstorm")
def ai_story_brainstorm(request, payload: OldStoryJob) -> JobStatus:
    # API validates via Pydantic (Ninja) here; Celery validates again at run time.
    logger.info(f"ai_story_brainstorm received: {payload} (type: {type(payload)})")
    chat_request = ChatRequest()
    story_job = StoryJob(story_uuid=payload.story_uuid)
    job = enqueue_job(
        user=request.user,
        workflow="ai.story_brainstorm",
        chat_request=chat_request,
        job=story_job,
    )
    if request.htmx:
        return HttpResponse(status=204)
    return {"job_uuid": str(job.uuid), "status": job.status}


@router.post("/jobs/page/content/suggest")
def ai_page_content(request, payload: OldPageJob) -> JobStatus:
    # API validates via Pydantic (Ninja) here; Celery validates again at run time.
    logger.info(f"ai_page_content received: {payload} (type: {type(payload)})")
    chat_request = ChatRequest()
    page_job = PageJob(page_uuid=payload.page_uuid)
    job = enqueue_job(
        user=request.user,
        workflow="ai.page_content",
        chat_request=chat_request,
        job=page_job,
    )
    if request.htmx:
        return HttpResponse(status=204)
    return {"job_uuid": str(job.uuid), "status": job.status}


@router.post("/jobs/page/image_text/suggest")
def ai_page_image_text(request, payload: OldPageJob) -> JobStatus:
    # API validates via Pydantic (Ninja) here; Celery validates again at run time.
    logger.info(f"ai_page_image_text received: {payload} (type: {type(payload)})")
    chat_request = ChatRequest()
    page_job = PageJob(page_uuid=payload.page_uuid)
    job = enqueue_job(
        user=request.user,
        workflow="ai.page_image_text",
        chat_request=chat_request,
        job=page_job,
    )
    if request.htmx:
        return HttpResponse(status=204)
    return {"job_uuid": str(job.uuid), "status": job.status}


@router.post("/jobs/page/image/generate")
def ai_page_image_generate(request, payload: OldPageJob) -> JobStatus:
    # API validates via Pydantic (Ninja) here; Celery validates again at run time.
    logger.info(f"ai_page_image_generate received: {payload} (type: {type(payload)})")
    chat_request = ChatRequest()
    page_job = PageJob(page_uuid=payload.page_uuid)
    job = enqueue_job(
        user=request.user,
        workflow="ai.page_image",
        chat_request=chat_request,
        job=page_job,
    )
    if request.htmx:
        return HttpResponse(status=204)
    return {"job_uuid": str(job.uuid), "status": job.status}
