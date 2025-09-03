from dataclasses import dataclass

from django.db import models

from apps.stories.models import Page, Story


@dataclass
class Workflow:
    name: str
    target_model: type[models.Model]


WORKFLOWS = {
    "story_title": Workflow(
        name="story_title",
        target_model=Story,
    ),
    "page_content": Workflow(
        name="page_content",
        target_model=Page,
    ),
}


def get_workflow(name: str) -> Workflow | None:
    """Fetches a workflow configuration from the registry."""
    return WORKFLOWS.get(name)
