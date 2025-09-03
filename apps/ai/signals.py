from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AIRequest

# from .tasks import dispatch_ai_workflow


@receiver(post_save, sender=AIRequest)
def trigger_ai_workflow(sender, instance, created, **kwargs):
    """
    Signal handler that triggers the AI workflow when a new AIRequest is created.
    """
    if created:
        print("dispatching", f"dispatch_ai_workflow.delay(str({instance.uuid}))")
