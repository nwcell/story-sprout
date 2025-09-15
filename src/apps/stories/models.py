import uuid

from django.contrib.auth import get_user_model
from django.db import models
from ordered_model.models import OrderedModel

User = get_user_model()


class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=50, default="New Story", blank=True, null=True)
    description = models.TextField(default="", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or "Untitled Story"

    @property
    def page_count(self):
        return self.pages.count()

    @property
    def channel(self):
        return f"story-{self.uuid}"

    def get_page_by_num(self, num):
        """Get a page by it's page number in the book (1-indexed)"""
        return self.pages.get(order=num - 1)

    class Meta:
        verbose_name = "Story"
        verbose_name_plural = "Stories"
        ordering = ["user", "-created_at"]


class Page(OrderedModel):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="pages")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    content = models.TextField(blank=True, null=True, default="", help_text="Content for this page")
    image_text = models.TextField(blank=True, null=True, default="", help_text="Image text for this page")
    image = models.ImageField(upload_to="page_images", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # OrderedModel configuration
    order_with_respect_to = "story"

    @property
    def is_first(self):
        """Return True if this is the first page in the story."""
        return self.order == 0

    @property
    def is_last(self):
        """Return True if this is the last page in the story."""
        return self.order == self.story.pages.count() - 1

    @property
    def page_number(self):
        return self.order + 1

    def get_previous_page(self):
        """Return the previous page in the story, or None if this is the first page."""
        if self.is_first:
            return None
        return self.story.pages.get(order=self.order - 1)

    def get_next_page(self):
        """Return the next page in the story, or None if this is the last page."""
        if self.is_last:
            return None
        return self.story.pages.get(order=self.order + 1)

    @property
    def image_binary(self):
        """Return the binary data of the page image, or None if no image."""
        if not self.image:
            return None
        with self.image.open("rb") as f:
            return f.read()

    def __str__(self):
        story_title = self.story.title or "Untitled Story"
        return f"Page {self.page_number} of {story_title}"

    class Meta(OrderedModel.Meta):
        verbose_name = "Page"
        verbose_name_plural = "Pages"
        ordering = ["story__user", "story", "order"]
