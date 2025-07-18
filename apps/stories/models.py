from django.db import models
from django.contrib.auth import get_user_model
from ordered_model.models import OrderedModel
import uuid

User = get_user_model()

class Story(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    @property
    def page_count(self):
        return self.pages.count()

    class Meta:
        verbose_name = "Story"
        verbose_name_plural = "Stories"
        ordering = ["user", "-created_at"]

class Page(OrderedModel):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='pages')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    content = models.TextField()
    content_generating = models.BooleanField(default=False, help_text="Whether content is being generated for this page")
    content_draft = models.TextField(blank=True, null=True, help_text="Draft content stored while generating")
    image_text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='page_images', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # OrderedModel configuration
    order_with_respect_to = 'story'
    
    @property
    def is_first(self):
        """Return True if this is the first page in the story."""
        return self.order == 0
    
    @property
    def is_last(self):
        """Return True if this is the last page in the story."""
        return self.order == self.story.pages.count() - 1
    
    def __str__(self):
        return f"Page {self.order + 1} of {self.story.title}"
    
    class Meta(OrderedModel.Meta):
        verbose_name = "Page"
        verbose_name_plural = "Pages"
        ordering = ['story__user', 'story', 'order']