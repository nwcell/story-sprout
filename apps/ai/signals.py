import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.ai.models import AIRequest
from apps.ai.workflows import dispatch_workflow

logger = logging.getLogger(__name__)


@receiver(post_save, sender=AIRequest)
def trigger_ai_workflow(sender, instance, created, **kwargs):
    """
    Signal handler that triggers the AI workflow when a new AIRequest is created.
    """
    if created or instance.status == AIRequest.Status.PENDING:
        logger.info(f"Triggering AI workflow for {instance}")
        dispatch_workflow(instance.workflow, request_uuid=str(instance.uuid))
