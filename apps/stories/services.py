from django_eventstream import send_event

from apps.stories.models import Story


def set_title_and_notify(story: Story, title: str) -> None:
    """Update story title and send SSE notification."""
    story.title = title
    story.save()
    send_event(story.channel, "get_story_title", "")


def set_description_and_notify(story: Story, description: str) -> None:
    """Update story description and send SSE notification."""
    story.description = description
    story.save()
    send_event(story.channel, "get_story_description", "")
