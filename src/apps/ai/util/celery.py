from time import monotonic

from celery import Task, current_app
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from pydantic import BaseModel

from apps.ai.models import Job

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


def enqueue_job(user: User, workflow: str, payload: BaseModel | dict) -> Job:
    """
    Enqueue a job with Pydantic model or dict payload.

    The payload will be passed directly to the task - celery-typed handles
    serialization of Pydantic models automatically.
    """
    ensure_task_exists(workflow)

    # Store serialized version for audit/replay
    audit_payload = payload.model_dump(mode="json") if isinstance(payload, BaseModel) else payload

    job = Job.objects.create(
        user=user,
        workflow=workflow,
        status=Job.Status.QUEUED,
        payload_json=audit_payload,  # audit/replay: we store serialized version
    )

    def _publish():
        # Pass payload directly - celery-typed handles Pydantic serialization
        Job.objects.filter(uuid=job.uuid).update(celery_task_id=job.uuid)
        task = current_app.tasks[workflow]
        task.apply_async(args=(payload,), kwargs=None, task_id=str(job.uuid))
        Job.objects.filter(uuid=job.uuid).update(dispatched_at=timezone.now())

    transaction.on_commit(_publish)
    return job
