import logging
from datetime import datetime
from uuid import UUID

import requests
from django.core.files.base import ContentFile
from django.db.models import ImageField as DjangoImageField
from django_eventstream import send_event
from pydantic import BaseModel

from apps.stories.models import Page, Story

logger = logging.getLogger(__name__)

# Type alias for page identification - can be either page number (int) or UUID
PageKey = int | UUID

# Type alias for image data - can be URL string or binary data
ImageData = str | bytes


class ImageField(BaseModel):
    url: str
    height: int | None = None
    width: int | None = None
    name: str
    size: int
    content_type: str


class PageSchema(BaseModel):
    uuid: UUID
    page_number: int
    content: str | None
    image_text: str | None
    image: ImageField | None
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

    def _create_image_field(self, django_image_field: DjangoImageField) -> ImageField:
        """Convert Django ImageField to our Pydantic ImageField."""
        return ImageField(
            url=django_image_field.url,
            height=django_image_field.height,
            width=django_image_field.width,
            name=django_image_field.name,
            size=django_image_field.size,
            content_type=django_image_field.content_type,
        )

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

        # Create ImageField from Django ImageField
        image_field = self._create_image_field(page_obj.image) if page_obj.image else None

        return PageSchema(
            uuid=page_obj.uuid,
            page_number=page_obj.page_number,
            content=page_obj.content,
            image_text=page_obj.image_text,
            image=image_field,
            is_first=page_obj.is_first,
            is_last=page_obj.is_last,
        )

    def get_page_image_binary(self, page_key: PageKey) -> bytes | None:
        """Get binary data of page image directly from Django storage."""
        page_obj = self.get_page_obj(page_key)

        if not page_obj.image:
            return None

        # Read binary data directly from Django storage
        with page_obj.image.open("rb") as image_file:
            return image_file.read()

    @classmethod
    def load_from_page_uuid(cls, page_uuid: UUID) -> "StoryService":
        page = Page.objects.get(uuid=page_uuid)
        return cls(page.story.uuid)

    @property
    def story(self) -> StorySchema:
        story_obj = self.story_obj()
        pages = []

        # Loop based on page_count and use existing get_page method
        for page_num in range(1, story_obj.page_count + 1):
            page_schema = self.get_page(page_num)
            pages.append(page_schema)

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

    def set_page_image(self, page_key: PageKey, image_data: ImageData) -> None:
        """Update page image. Accepts either URL (str) or binary data (bytes).
        page_key can be page number (int) or UUID."""
        story_obj = self.story_obj()
        page_instance = self.get_page_obj(page_key)

        if image_data:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_image_{timestamp}.png"

            if isinstance(image_data, str):
                # Handle URL - download the image
                response = requests.get(image_data)
                response.raise_for_status()
                page_instance.image.save(filename, ContentFile(response.content), save=True)
            elif isinstance(image_data, bytes):
                # Handle binary data directly
                page_instance.image.save(filename, ContentFile(image_data), save=True)
            else:
                raise ValueError(f"Unsupported image_data type: {type(image_data)}")

        send_event(story_obj.channel, f"get_page_image#{page_instance.uuid}", "")
