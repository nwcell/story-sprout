"""Tests for the stories app."""

from apps.stories.models import Page, Story
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class StoriesAppLoadTest(TestCase):
    """Test that the stories app loads correctly."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

    def test_story_model_creation(self):
        """Test that Story model can be created and has expected attributes."""
        story = Story.objects.create(user=self.user, title="Test Story", description="A test story description")

        # Verify story was created
        self.assertEqual(story.title, "Test Story")
        self.assertEqual(story.description, "A test story description")
        self.assertEqual(story.user, self.user)
        self.assertIsNotNone(story.uuid)
        self.assertIsNotNone(story.created_at)
        self.assertIsNotNone(story.updated_at)

        # Test string representation
        self.assertEqual(str(story), "Test Story")

        # Test page count property
        self.assertEqual(story.page_count, 0)

    def test_page_model_creation(self):
        """Test that Page model can be created and has expected attributes."""
        story = Story.objects.create(user=self.user, title="Test Story")
        page = Page.objects.create(story=story, content="This is page content", image_text="Image description")

        # Verify page was created
        self.assertEqual(page.content, "This is page content")
        self.assertEqual(page.image_text, "Image description")
        self.assertEqual(page.story, story)
        self.assertIsNotNone(page.uuid)
        self.assertEqual(page.order, 0)  # First page should have order 0

        # Test page properties
        self.assertTrue(page.is_first)
        self.assertTrue(page.is_last)  # Only page, so both first and last
        self.assertEqual(page.page_number, 1)

        # Test string representation
        self.assertEqual(str(page), "Page 1 of Test Story")

        # Update story page count
        self.assertEqual(story.page_count, 1)

    def test_models_can_be_imported(self):
        """Test that models can be imported without errors."""
        # If we got this far, the imports in the module worked
        self.assertTrue(hasattr(Story, "objects"))
        self.assertTrue(hasattr(Page, "objects"))

        # Test model meta attributes
        self.assertEqual(Story._meta.verbose_name, "Story")
        self.assertEqual(Page._meta.verbose_name, "Page")
