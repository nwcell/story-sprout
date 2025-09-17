import logging
from datetime import datetime
from uuid import UUID

import requests
from django.core.files.base import ContentFile
from django_eventstream import send_event
from pydantic import BaseModel

from apps.stories.models import Page, Story

logger = logging.getLogger(__name__)

# Type alias for page identification - can be either page number (int) or UUID
PageKey = int | UUID


class PageSchema(BaseModel):
    uuid: UUID
    page_number: int
    content: str | None
    image_text: str | None
    image_url: str | None
    is_first: bool
    is_last: bool


class StorySchema(BaseModel):
    uuid: UUID
    title: str | None
    description: str | None
    page_count: int
    pages: list[PageSchema]
    channel: str


class StoryService:
    def __init__(self, uuid: UUID):
        self.uuid = uuid

    def story_obj(self) -> Story:
        logger.info(f"StoryService.story_obj({self.uuid})")
        return Story.objects.get(uuid=self.uuid)

    def get_page_obj(self, page_key: PageKey) -> Page:
        """Get page by either page number (int) or UUID."""
        story_obj = self.story_obj()
        if isinstance(page_key, int):
            # page_key is page number
            return story_obj.get_page_by_num(page_key)
        else:
            # page_key is UUID
            return story_obj.pages.get(uuid=page_key)

    def get_page(self, page_key: PageKey) -> PageSchema:
        page_obj = self.get_page_obj(page_key)
        return PageSchema(
            uuid=page_obj.uuid,
            page_number=page_obj.page_number,
            content=page_obj.content,
            image_text=page_obj.image_text,
            image_url=page_obj.image.url if page_obj.image else None,
            is_first=page_obj.is_first,
            is_last=page_obj.is_last,
        )

    @classmethod
    def load_from_page_uuid(cls, page_uuid: UUID) -> "StoryService":
        page = Page.objects.get(uuid=page_uuid)
        return cls(page.story.uuid)

    @property
    def story(self) -> StorySchema:
        story_obj = self.story_obj()
        pages = []
        for page_obj in story_obj.pages.all():
            pages.append(
                PageSchema(
                    uuid=page_obj.uuid,
                    page_number=page_obj.page_number,
                    content=page_obj.content,
                    image_text=page_obj.image_text,
                    image_url=page_obj.image.url if page_obj.image else None,
                    is_first=page_obj.is_first,
                    is_last=page_obj.is_last,
                )
            )
        return StorySchema(
            uuid=story_obj.uuid,
            title=story_obj.title,
            description=story_obj.description,
            page_count=story_obj.page_count,
            pages=pages,
            channel=story_obj.channel,
        )

    def set_title(self, input: str) -> None:
        """Update story title and send SSE notification."""
        story_obj = self.story_obj()
        story_obj.title = input
        story_obj.save()
        send_event(story_obj.channel, "get_story_title", "")

    def set_description(self, input: str) -> None:
        """Update story description and send SSE notification."""
        story_obj = self.story_obj()
        story_obj.description = input
        story_obj.save()
        send_event(story_obj.channel, "get_story_description", "")

    def set_page_content(self, page_key: PageKey, input: str) -> None:
        """Update page content. page_key can be page number (int) or UUID."""
        story_obj = self.story_obj()
        page_instance = self.get_page_obj(page_key)
        page_instance.content = input
        page_instance.save()
        send_event(story_obj.channel, f"get_page_content#{page_instance.uuid}", "")

    def set_page_image_text(self, page_key: PageKey, input: str) -> None:
        """Update page image text. page_key can be page number (int) or UUID."""
        story_obj = self.story_obj()
        page_instance = self.get_page_obj(page_key)
        page_instance.image_text = input
        page_instance.save()
        send_event(story_obj.channel, f"get_page_image_text#{page_instance.uuid}", "")

    def set_page_image(self, page_key: PageKey, input: str) -> None:
        """Update page image. page_key can be page number (int) or UUID."""
        story_obj = self.story_obj()
        page_instance = self.get_page_obj(page_key)
        page_instance.image_text = input
        page_instance.save()
        send_event(story_obj.channel, f"get_page_image#{page_instance.uuid}", "")


def set_page_image_and_notify(page: Page, image_url: str) -> None:
    story = page.story

    # Download and save image from URL
    response = requests.get(image_url, timeout=30)
    response.raise_for_status()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"generated_image_{timestamp}.png"

    page.image.save(filename, ContentFile(response.content), save=True)
    send_event(story.channel, f"get_page_image#{page.uuid}", "")
