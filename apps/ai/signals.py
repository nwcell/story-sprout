from dataclasses import dataclass
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .services import orchestrate

@dataclass
class Trigger:
    app_label: str
    model_name: str
    field_name: str
    workflow_func: str

TRIGGERS = [
    Trigger(
        app_label='stories',
        model_name='page',
        field_name='content_generating',
        workflow_func='page_content_workflow',
    ),
]

@receiver(pre_save)
def handle_boolean_field_changes(sender, instance, **kwargs):
    """
    Signal handler that detects when a registered boolean field changes from False to True
    and triggers the orchestrate function.
    """
    path = (sender._meta.app_label, sender._meta.model_name)
    trigger = next((t for t in TRIGGERS if path == (t.app_label, t.model_name)), None)
    if not trigger:
        return

    if not instance.pk:
        return
    try:
        old_instance = sender.objects.get(pk=instance.pk)
        old_value = getattr(old_instance, trigger.field_name, False)
    except sender.DoesNotExist:
        old_value = False
    
    new_value = getattr(instance, trigger.field_name, False)
    
    if old_value is False and new_value is True:
        orchestrate(
            target_ct=ContentType.objects.get_for_model(sender),
            target_id=instance.pk,
            workflow_func=trigger.workflow_func,
            user=instance.story.user,
        )

