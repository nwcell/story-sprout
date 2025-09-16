import logging
import time
from datetime import datetime
from uuid import UUID

from django.core.cache import cache
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from ninja import Router

from apps.ai.agents import list_agent_types
from apps.ai.models import Conversation
from apps.ai.schemas import ConversationDetailSchema, ConversationSchema, JobStatus, PageJob, RequestSchema, StoryJob
from apps.ai.tasks import agent_task
from apps.ai.util.celery import enqueue_job

router = Router()
logger = logging.getLogger(__name__)


@router.get("/agents", tags=["Agents"])
def agents(request) -> list[str]:
    _user = request.user
    logger.info(f"API: agents endpoint called by user {_user}")
    logger.debug(f"API: Getting agent types list")
    return list_agent_types()


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
    logger.info(f"create_request received: {payload}")
    user = request.user

    # Get or create conversation
    if payload.conversation_uuid:
        conversation = get_object_or_404(Conversation, uuid=payload.conversation_uuid, user=user)
        logger.info(f"create_request found conversation: {conversation}")
    else:
        # Create new conversation with readable datetime title
        now = datetime.now()
        title = f"New Chat {now.strftime('%Y-%m-%d %H:%M')}"
        conversation = Conversation.objects.create(user=user, title=title)
        logger.info(f"create_request created conversation: {conversation}")

        # Update payload with the new conversation UUID
        payload.conversation_uuid = conversation.uuid

    # Enqueue agent orchestration task
    logger.info(f"create_request enqueuing agent task: {payload}")
    agent_task.delay(payload)
    logger.info(f"create_request enqueued agent task: {payload}")

    return conversation


@router.get("/conversations/{conversation_uuid}/stream")
def stream_conversation_updates(request, conversation_uuid: UUID):
    """Stream real-time updates for a conversation via SSE."""

    def event_stream():
        channel_name = f"conversation_{conversation_uuid}"
        last_message_count = 0

        while True:
            try:
                # Check for new messages
                conversation = Conversation.objects.get(uuid=conversation_uuid, user=request.user)
                current_message_count = conversation.messages.count()

                if current_message_count > last_message_count:
                    # Send new messages
                    new_messages = conversation.messages.all()[last_message_count:]
                    for message in new_messages:
                        data = {
                            "type": "message",
                            "uuid": str(message.uuid),
                            "content": message.content,
                            "position": message.position,
                        }
                        yield f"data: {data}\n\n"

                    last_message_count = current_message_count

                # Check for completion signal
                completion_signal = cache.get(f"{channel_name}_complete")
                if completion_signal:
                    cache.delete(f"{channel_name}_complete")
                    yield "event: complete\ndata: Conversation updated\n\n"
                    break

                time.sleep(1)  # Poll every second

            except Conversation.DoesNotExist:
                yield "event: error\ndata: Conversation not found\n\n"
                break
            except Exception as e:
                logger.error(f"SSE streaming error: {e}")
                yield f"event: error\ndata: {str(e)}\n\n"
                break

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["Connection"] = "keep-alive"
    return response


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
