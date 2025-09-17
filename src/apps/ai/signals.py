# yourapp/signals.py
from __future__ import annotations

from celery import current_app
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now

from .models import Job


def _publish_job(job: Job) -> None:
    """
    Publish the job to Celery and persist the returned task_id.
    Assumes the DB transaction has committed (call via on_commit).
    """
    # Send with exactly the kwargs we stored for replay
    result = current_app.send_task(job.workflow, kwargs=job.payload_json or {})
    # Update by PK to avoid re-running model save hooks
    Job.objects.filter(pk=job.pk).update(
        celery_task_id=result.id,
        dispatched_at=now(),
        updated_at=now(),
    )


# @receiver(post_save, sender=Job, dispatch_uid="jobs.autodispatch")
# def jobs_autodispatch(sender, instance: Job, created: bool, **kwargs):
#     """
#     Auto-dispatch when:
#       - a Job is created with QUEUED status, OR
#       - a Job is re-queued (status set to QUEUED) and has no task_id yet.
#
#     Idempotency guards:
#       - don't enqueue if celery_task_id is already set
#       - only enqueue when status is QUEUED
#     """
#     # Must be QUEUED and not already dispatched
#     if instance.status != Job.Status.QUEUED:
#         return
#     if instance.celery_task_id:
#         return
#
#     # Publish only after the outer transaction commits
#     transaction.on_commit(lambda: _publish_job(instance))
