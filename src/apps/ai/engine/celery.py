from time import monotonic

from celery import Task, current_app
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.ai.models import Job
from apps.ai.types import ChatRequest
from apps.ai.types import Job as JobType
from apps.ai.types import User as UserType

User = get_user_model()


class JobTask(Task):
    _t0: float | None = None

    def before_start(self, task_id, args, kwargs):
        self._t0 = monotonic()
        with transaction.atomic():
            Job.objects.select_for_update().filter(celery_task_id=task_id).update(
                status=Job.Status.RUNNING,
                started_at=timezone.now(),
            )

    def on_success(self, retval, task_id, args, kwargs):
        Job.objects.filter(celery_task_id=task_id).update(
            status=Job.Status.SUCCESS,
            output_text=retval if isinstance(retval, str) else str(retval),
            finished_at=timezone.now(),
            runtime_ms=int((monotonic() - (self._t0 or monotonic())) * 1000),
        )

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        Job.objects.filter(celery_task_id=task_id).update(
            status=Job.Status.FAILED,
            error_message=str(exc),
            finished_at=timezone.now(),
            runtime_ms=int((monotonic() - (self._t0 or monotonic())) * 1000),
        )


def ensure_task_exists(name: str):
    if name not in current_app.tasks:
        raise ValueError(f"Unknown workflow '{name}'")


def enqueue_job(user: User, workflow: str, chat_request: ChatRequest, job: JobType | None = None) -> Job:
    """
    Enqueue a job with ChatRequest and optional Job.

    Args:
        user: Django User instance
        workflow: Task workflow name
        chat_request: ChatRequest with conversation/message data
        job: Optional job with story_uuid or page_uuid
    """
    ensure_task_exists(workflow)

    # Create combined payload for task
    from apps.ai.types import TaskPayload

    task_payload = TaskPayload(user=UserType(user_id=user.id), chat_request=chat_request, job=job)

    # Store serialized version for audit/replay
    audit_payload = {
        "user_id": user.id,
        "chat_request": chat_request.model_dump(mode="json"),
        "job": job.model_dump(mode="json") if job else None,
    }

    job_record = Job.objects.create(
        user=user,
        workflow=workflow,
        status=Job.Status.QUEUED,
        payload_json=audit_payload,
    )

    def _publish():
        Job.objects.filter(uuid=job_record.uuid).update(celery_task_id=job_record.uuid)
        task = current_app.tasks[workflow]
        # Serialize to dict to preserve discriminated union through Celery
        task.apply_async(kwargs={"payload": task_payload.model_dump(mode="json")}, task_id=str(job_record.uuid))
        Job.objects.filter(uuid=job_record.uuid).update(dispatched_at=timezone.now())

    transaction.on_commit(_publish)
    return job_record
