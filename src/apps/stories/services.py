import logging
import mimetypes
from datetime import datetime
from typing import Any, Literal
from uuid import UUID

import requests
from django.core.files.base import ContentFile
from django.db.models import ImageField as DjangoImageField
from django_eventstream import send_event
from google.genai.types import Part
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
        )

    def _get_story_queryset(self):
        """Get QuerySet for this story.
        Returns a QuerySet that can be used with .get(), .first(), .update(), etc.
        """
        return Story.objects.filter(uuid=self.uuid)

    def story_obj(self) -> Story:
        logger.info(f"StoryService.story_obj({self.uuid})")
        return self._get_story_queryset().get()

    def _get_page_queryset(self, page_key: PageKey):
        """Get QuerySet for a page by key.
        Returns a QuerySet that can be used with .get(), .first(), .update(), etc.
        """
        if isinstance(page_key, int):
            # page_key is page number (1-indexed)
            return Page.objects.filter(story__uuid=self.uuid, order=page_key - 1)
        else:
            # page_key is UUID
            return Page.objects.filter(uuid=page_key, story__uuid=self.uuid)

    def get_page_obj(self, page_key: PageKey) -> Page:
        """Get page by either page number (int) or UUID."""
        return self._get_page_queryset(page_key).get()

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

    def get_story(self, fresh: bool = False) -> StorySchema:
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
        self._get_story_queryset().update(title=input)
        self.refresh_story("title")

    def set_description(self, input: str) -> None:
        """Update story description and send SSE notification."""
        self._get_story_queryset().update(description=input)
        self.refresh_story("description")

    def update_story(self, title: str | None = None, description: str | None = None) -> None:
        if title:
            self.set_title(title)
        if description:
            self.set_description(description)

    def set_page_content(self, page_key: PageKey, input: str) -> None:
        """Update page content. page_key can be page number (int) or UUID."""
        self._get_page_queryset(page_key).update(content=input)
        self.refresh_page(page_key, "content")

    def set_page_image_text(self, page_key: PageKey, input: str) -> None:
        """Update page image text. page_key can be page number (int) or UUID."""
        self._get_page_queryset(page_key).update(image_text=input)
        self.refresh_page(page_key, "image_text")

    def set_page_image(self, page_key: PageKey, image_data: ImageData) -> None:
        page_instance = self._get_page_queryset(page_key).get()

        if image_data:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_image_{timestamp}.png"

            if isinstance(image_data, str):
                # Handle URL - download the image
                # TODO: DONT USE REQUESTS
                response = requests.get(image_data)
                response.raise_for_status()
                page_instance.image.save(filename, ContentFile(response.content), save=True)
            elif isinstance(image_data, bytes):
                # Handle binary data directly
                page_instance.image.save(filename, ContentFile(image_data), save=True)
            else:
                raise ValueError(f"Unsupported image_data type: {type(image_data)}")

        self.refresh_page(page_key, "image")

    def update_page(
        self,
        page_key: PageKey,
        content: str | None = None,
        image_text: str | None = None,
        image_data: ImageData | None = None,
    ) -> None:
        if content:
            self.set_page_content(page_key, content)
        if image_text:
            self.set_page_image_text(page_key, image_text)
        if image_data:
            self.set_page_image(page_key, image_data)

    def refresh_story(self, target: Literal["title", "description", "page_list", None]):
        story = self.get_story()
        if target == "title":
            send_event(story.channel, "get_story_title", "")
        elif target == "description":
            send_event(story.channel, "get_story_description", "")
        elif target == "page_list":
            send_event(story.channel, "list_pages", "")
        elif target is None:
            # Currently, there is no hook to refresh an entire story
            send_event(story.channel, "get_story_title", "")
            send_event(story.channel, "get_story_description", "")
            send_event(story.channel, "list_pages", "")

    def refresh_page(self, page_key: PageKey, target: Literal["content", "image_text", "image", None]):
        story = self.get_story()
        page = self.get_page(page_key)
        if target == "content":
            send_event(story.channel, f"get_page_content#{page.uuid}", "")
        elif target == "image_text":
            send_event(story.channel, f"get_page_image_text#{page.uuid}", "")
        elif target == "image":
            send_event(story.channel, f"get_page_image#{page.uuid}", "")
        elif target is None:
            send_event(story.channel, f"get_page#{page.uuid}", "")

    def gemini_parts(self) -> list[Any]:
        """
        Prepares the story for the Gemini API by separating JSON metadata
        from binary image data.
        """
        story = self.get_story(fresh=False)
        contents: list[Any] = []

        # 1) Story-level metadata
        contents.append(story.model_dump_json(exclude={"pages"}))

        # 2) Per-page payloads and images
        for page in story.pages:
            contents.append(page.model_dump_json(exclude={"image"}))

            page_obj = self.get_page_obj(page.uuid)
            page_image = page_obj.image
            if page_image:
                page_image.open("rb")
                try:
                    data = page_image.read()
                finally:
                    page_image.close()
                mime, _ = mimetypes.guess_type(getattr(page_image, "name", "image"))
                if not mime:
                    continue
                part = Part.from_bytes(data=data, mime_type=mime)
                contents.append(part)

        return contents
