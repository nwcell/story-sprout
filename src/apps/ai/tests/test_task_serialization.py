"""
Tests for Celery task Pydantic model serialization.

These tests verify that Pydantic models are properly serialized and deserialized
when passed to Celery tasks, and that the tasks receive the models as expected.
"""

import logging
from unittest.mock import patch

from django.test import TestCase

from apps.ai.schemas import StoryJob
from apps.ai.tasks import ai_story_title_job
from apps.stories.models import Story

logger = logging.getLogger(__name__)


class TestTaskSerialization(TestCase):
    """Test Celery task serialization with Pydantic models."""

    def setUp(self):
        """Set up test data."""
        self.user = self._create_test_user()
        self.story = Story.objects.create(user=self.user, title="Test Story", description="Test description")

    def _create_test_user(self):
        """Create a test user."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        return User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

    def test_story_job_direct_call(self):
        """Test that StoryJob can be passed directly to task function."""
        payload = StoryJob(story_uuid=self.story.uuid)

        # Mock the AI completion to avoid external API calls
        with patch("apps.ai.tasks.ai.prompt_completion") as mock_completion:
            mock_completion.return_value = "Test Title"

            # This should work - direct function call with StoryJob object
            result = ai_story_title_job(payload)

            # Verify the task executed correctly
            self.assertIn("ai_story_title_job", result)
            mock_completion.assert_called_once()

    def test_story_job_serialization_deserialization(self):
        """Test that StoryJob serializes and deserializes correctly."""
        from celery_typed import PydanticModelDump

        payload = StoryJob(story_uuid=self.story.uuid)

        # Test serialization
        serializer = PydanticModelDump()
        serialized = serializer.pack(payload)

        # Verify serialized structure
        self.assertEqual(serialized["module"], "apps.ai.schemas")
        self.assertEqual(serialized["qualname"], "StoryJob")
        self.assertEqual(serialized["dump"]["story_uuid"], str(self.story.uuid))

        # Test deserialization
        deserialized = serializer.unpack(serialized)

        # Verify deserialized object
        self.assertIsInstance(deserialized, StoryJob)
        self.assertEqual(deserialized.story_uuid, self.story.uuid)

    def test_celery_task_signature_inspection(self):
        """Test that the task function signature is correct."""
        import inspect

        sig = inspect.signature(ai_story_title_job)
        params = list(sig.parameters.keys())

        # The function should expect a single 'payload' parameter
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0], "payload")

        # Get the parameter type annotation
        param = sig.parameters["payload"]
        self.assertEqual(param.annotation, StoryJob)

    @patch("apps.ai.tasks.ai.prompt_completion")
    def test_async_task_call_simulation(self, mock_completion):
        """Test simulating the async task call to identify where the issue occurs."""
        mock_completion.return_value = "Test Title"

        payload = StoryJob(story_uuid=self.story.uuid)

        # Simulate what Celery does internally
        # This should help us identify where the args/kwargs unpacking happens

        # Step 1: Serialize the payload (what happens before sending to broker)
        from celery_typed import PydanticModelDump

        serializer = PydanticModelDump()
        serialized = serializer.pack(payload)

        # Step 2: Deserialize the payload (what happens on worker)
        deserialized = serializer.unpack(serialized)

        # Step 3: Call the task function (this is where the issue likely occurs)
        # In Celery, this happens in Task.__call__ or Task.run

        # This should work (direct call with positional arg)
        result = ai_story_title_job(deserialized)
        self.assertIn("ai_story_title_job", result)

        # This should fail (if model fields are unpacked as kwargs)
        with self.assertRaises(TypeError) as cm:
            ai_story_title_job(story_uuid=self.story.uuid)

        self.assertIn("unexpected keyword argument", str(cm.exception))

    def test_task_base_class_behavior(self):
        """Test if the JobTask base class is interfering with argument handling."""

        from apps.ai.util.celery import JobTask

        # Create a mock task instance to test base class behavior
        task_instance = JobTask()

        # Test the hooks that JobTask implements
        task_id = "test-task-id"
        args = (StoryJob(story_uuid=self.story.uuid),)
        kwargs = {}

        # These should not modify the args/kwargs
        task_instance.before_start(task_id, args, kwargs)

        # Verify args and kwargs are unchanged
        self.assertEqual(len(args), 1)
        self.assertIsInstance(args[0], StoryJob)
        self.assertEqual(len(kwargs), 0)

    @patch("apps.ai.tasks.ai.prompt_completion")
    def test_reproduce_exact_error(self, mock_completion):
        """Try to reproduce the exact error we're seeing."""
        mock_completion.return_value = "Test Title"

        payload = StoryJob(story_uuid=self.story.uuid)

        # Get the actual Celery task object
        task = ai_story_title_job

        # Try to simulate what happens in task.delay()
        # This might reveal where the issue occurs

        try:
            # Test direct execution through Celery's task runner
            # This should reveal if the issue is in Celery's argument handling
            result = task.apply(args=(payload,), kwargs={})
            logger.info(f"Task apply result: {result}")

        except TypeError as e:
            logger.error(f"Task apply failed: {e}")

            # If we get the same error, we know it's in Celery's execution path
            if "unexpected keyword argument 'story_uuid'" in str(e):
                self.fail(f"Root cause identified: Celery is unpacking StoryJob fields as kwargs: {e}")
