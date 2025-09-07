from django_eventstream import send_event

from apps.stories.models import Page, Story


def set_story_title_and_notify(story: Story, title: str) -> None:
    """Update story title and send SSE notification."""
    story.title = title
    story.save()
    send_event(story.channel, "get_story_title", "")


def set_story_description_and_notify(story: Story, description: str) -> None:
    """Update story description and send SSE notification."""
    story.description = description
    story.save()
    send_event(story.channel, "get_story_description", "")


def set_page_content_and_notify(page: Page, content: str) -> None:
    story = page.story
    page.content = content
    page.save()
    send_event(story.channel, f"get_page_content#{page.uuid}", "")


def set_page_image_text_and_notify(page: Page, image_text: str) -> None:
    story = page.story
    page.image_text = image_text
    page.save()
    send_event(story.channel, f"get_page_image_text#{page.uuid}", "")


def set_page_image_and_notify(page: Page, image_file) -> None:
    """Update page image and send SSE notification."""
    story = page.story
    page.image.save(image_file.name, image_file, save=True)
    send_event(story.channel, f"get_page_image#{page.uuid}", "")
