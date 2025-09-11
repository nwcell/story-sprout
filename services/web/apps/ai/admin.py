from __future__ import annotations

import json
from collections.abc import Iterable

from celery import current_app
from django.contrib import admin, messages
from django.db import transaction
from django.utils.html import format_html
from django.utils.timezone import now

from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    # ------- List view -------
    list_display = (
        "uuid",
        "workflow",
        "user",
        "status",
        "created_at",
        "started_at",
        "finished_at",
        "duration_ms",
        "celery_task_id_short",
    )
    list_filter = ("status", "workflow", ("created_at", admin.DateFieldListFilter))
    search_fields = (
        "uuid",
        "workflow",
        "celery_task_id",
        "user__username",
        "user__email",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    # ------- Detail view -------
    readonly_fields = (
        "uuid",
        "user",
        "workflow",
        "payload_pretty",
        "celery_task_id",
        "status",
        "output_text",
        "error_message",
        "runtime_ms",
        "created_at",
        "updated_at",
        "started_at",
        "finished_at",
        "dispatched_at",
    )
    fields = (
        "uuid",
        "user",
        "workflow",
        "payload_pretty",
        "status",
        ("created_at", "updated_at"),
        ("started_at", "finished_at"),
        ("runtime_ms", "celery_task_id"),
        "output_text",
        "error_message",
        "dispatched_at",
    )

    actions = ("requeue_selected",)

    # ------- Pretty JSON payload -------
    @admin.display(description="Payload (pretty JSON)")
    def payload_pretty(self, obj: Job) -> str:
        try:
            txt = json.dumps(obj.payload_json or {}, indent=2, sort_keys=True)
        except Exception:
            txt = str(obj.payload_json)
        return format_html("<pre style='max-height:420px;overflow:auto'>{}</pre>", txt)

    # ------- Helpers for list view -------
    @admin.display(description="Duration (ms)")
    def duration_ms(self, obj: Job) -> int | None:
        # Prefer stored runtime_ms; fallback to derive if finished
        if obj.runtime_ms is not None:
            return obj.runtime_ms
        if obj.started_at and obj.finished_at:
            return int((obj.finished_at - obj.started_at).total_seconds() * 1000)
        return None

    @admin.display(description="Task ID", ordering="celery_task_id")
    def celery_task_id_short(self, obj: Job) -> str:
        tid = obj.celery_task_id or ""
        return f"{tid[:8]}…" if len(tid) > 9 else tid

    # ------- Admin action: Requeue -------
    @admin.action(description="Requeue selected jobs")
    def requeue_selected(self, request, queryset: Iterable[Job]):
        # Only requeue jobs not currently RUNNING
        to_requeue = list(queryset.exclude(status=Job.Status.RUNNING))
        if not to_requeue:
            self.message_user(request, "Nothing to requeue.", level=messages.INFO)
            return

        # Validate Celery task name exists before we start
        missing = [j for j in to_requeue if j.workflow not in current_app.tasks]
        if missing:
            self.message_user(
                request,
                f"Skipped {len(missing)} job(s): unknown workflow names present.",
                level=messages.WARNING,
            )
            to_requeue = [j for j in to_requeue if j not in missing]

        count = 0
        for job in to_requeue:
            # Reset state to QUEUED; keep payload_json as-is (replayable)
            Job.objects.filter(pk=job.pk).update(
                status=Job.Status.QUEUED,
                error_message="",
                output_text="",
                runtime_ms=None,
                started_at=None,
                finished_at=None,
                dispatched_at=None,
                celery_task_id="",
                updated_at=now(),
            )

            # Publish after the DB commit to avoid drift
            def _publish(jid=job.pk, workflow=job.workflow, kwargs=job.payload_json):
                res = current_app.send_task(workflow, kwargs=kwargs)
                Job.objects.filter(pk=jid).update(
                    celery_task_id=res.id,
                    dispatched_at=now(),
                    updated_at=now(),
                )

            transaction.on_commit(_publish)
            count += 1

        if count:
            self.message_user(request, f"Requeued {count} job(s).", level=messages.SUCCESS)
