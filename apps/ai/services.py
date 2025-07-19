from django.contrib.contenttypes.models import ContentType
from .models import AIWorkflow
from . import tasks


def orchestrate(target_ct: ContentType, target_id: int, workflow_func: str, user=None):
    workflow = AIWorkflow.objects.create(
        target_ct=target_ct,
        target_id=target_id,
        workflow_func=workflow_func,
        user=user,
    )

    getattr(tasks, workflow_func).delay(workflow.id)
