from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.module_loading import import_string

from apps.stories.models import Page, Story


@dataclass
class Workflow:
    name: str
    target_model: type[models.Model]
    task: str  # String path to the task function


WORKFLOWS = {
    "story_title": Workflow(
        name="story_title",
        target_model=Story,
        task="apps.ai.tasks.story_title",
    ),
    "page_content": Workflow(
        name="page_content",
        target_model=Page,
        task="apps.ai.tasks.page_content",
    ),
}


def get_workflow(name: str) -> Workflow | None:
    """Fetches a workflow configuration from the registry."""
    if name not in WORKFLOWS:
        raise ValidationError(f"Unknown workflow: {name}. Allowed: {list(WORKFLOWS)}")
    return WORKFLOWS.get(name)


def dispatch_workflow(name: str, **kwargs):
    """
    Look up by string and enqueue the matching Celery task.
    """
    workflow = get_workflow(name)
    task_func = import_string(workflow.task)
    return task_func.delay(**kwargs)
