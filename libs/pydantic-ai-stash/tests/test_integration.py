"""Integration tests for pydantic-ai-stash."""

import pytest
from pydantic_ai.messages import (
    BinaryContent,
    ModelRequest,
    ModelResponse,
    SystemPromptPart,
    TextPart,
    UserPromptPart,
)

from pydantic_ai_stash import BinaryStash, FSAdapter


class TestIntegration:
    """Integration tests that test the complete workflow."""

    def test_complete_workflow_single_message(self, temp_storage_dir):
        """Test complete workflow with a single message containing mixed content."""
        # Setup
        adapter = FSAdapter(str(temp_storage_dir))
        stash = BinaryStash(adapter)

        # Create message with mixed content
        image_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        audio_data = b"RIFF\x24\x00\x00\x00WAVE"

        original_message = ModelRequest(
            parts=[
                UserPromptPart(
                    content=[
                        TextPart(content="Please analyze these files:"),
                        BinaryContent(
                            data=image_data,
                            media_type="image/png",
                            identifier="screenshot-1",
                            vendor_metadata={"source": "user_upload", "size": len(image_data)},
                        ),
                        TextPart(content="And this audio:"),
                        BinaryContent(
                            data=audio_data, media_type="audio/wav", identifier="recording-1"
                        ),
                        TextPart(content="What do you think?"),
                    ]
                )
            ]
        )

        # 1. Stash binaries
        stashed_messages = list(stash.stash_binaries_in_messages([original_message]))
        stashed_message = stashed_messages[0]

        # Verify URLs were created
        content = stashed_message.parts[0].content
        assert len(content) == 5
        assert isinstance(content[0], TextPart)
        assert content[0].content == "Please analyze these files:"

        assert hasattr(content[1], "url")
        assert content[1].url.startswith("media://")
        assert content[1].media_type == "image/png"
        assert content[1].identifier == "screenshot-1"

        assert isinstance(content[2], TextPart)
        assert content[2].content == "And this audio:"

        assert hasattr(content[3], "url")
        assert content[3].url.startswith("media://")
        assert content[3].media_type == "audio/wav"
        assert content[3].identifier == "recording-1"

        assert isinstance(content[4], TextPart)
        assert content[4].content == "What do you think?"

        # 2. Verify files exist in storage
        image_key = content[1].url.removeprefix("media://")
        audio_key = content[3].url.removeprefix("media://")

        assert adapter.exists(image_key)
        assert adapter.exists(audio_key)

        # 3. Load binaries back
        loaded_messages = list(stash.load_binaries_in_messages(stashed_messages))
        loaded_message = loaded_messages[0]

        # 4. Verify loaded content matches original
        loaded_content = loaded_message.parts[0].content
        assert len(loaded_content) == 5

        assert isinstance(loaded_content[1], BinaryContent)
        assert loaded_content[1].data == image_data
        assert loaded_content[1].media_type == "image/png"
        assert loaded_content[1].identifier == "screenshot-1"
        assert loaded_content[1].vendor_metadata == {
            "source": "user_upload",
            "size": len(image_data),
        }

        assert isinstance(loaded_content[3], BinaryContent)
        assert loaded_content[3].data == audio_data
        assert loaded_content[3].media_type == "audio/wav"
        assert loaded_content[3].identifier == "recording-1"

    def test_conversation_workflow(self, temp_storage_dir):
        """Test workflow with a multi-message conversation."""
        adapter = FSAdapter(str(temp_storage_dir))
        stash = BinaryStash(adapter)

        # Create a conversation with images
        image1 = BinaryContent(data=b"image1_data", media_type="image/jpeg")
        image2 = BinaryContent(data=b"image2_data", media_type="image/png")

        conversation = [
            ModelRequest(parts=[SystemPromptPart(content="You are a helpful assistant.")]),
            ModelRequest(
                parts=[UserPromptPart(content=[TextPart(content="Look at this image:"), image1])]
            ),
            ModelResponse(
                parts=[
                    TextPart(content="I can see the image. What would you like to know about it?")
                ]
            ),
            ModelRequest(
                parts=[
                    UserPromptPart(content=[TextPart(content="Compare it with this one:"), image2])
                ]
            ),
            ModelResponse(parts=[TextPart(content="Both images have been analyzed.")]),
        ]

        # Stash all binaries
        stashed_conversation = list(stash.stash_binaries_in_messages(conversation))

        # Verify structure is preserved
        assert len(stashed_conversation) == 5

        # First message (system) should be unchanged
        assert isinstance(stashed_conversation[0].parts[0], SystemPromptPart)

        # Second message should have stashed image
        user_content = stashed_conversation[1].parts[0].content
        assert isinstance(user_content[0], TextPart)
        assert hasattr(user_content[1], "url")
        assert user_content[1].url.startswith("media://")

        # Third message (response) should be unchanged
        assert isinstance(stashed_conversation[2].parts[0], TextPart)

        # Fourth message should have different stashed image
        user_content2 = stashed_conversation[3].parts[0].content
        assert hasattr(user_content2[1], "url")
        assert user_content2[1].url.startswith("media://")

        # URLs should be different (different content)
        assert user_content[1].url != user_content2[1].url

        # Load conversation back
        loaded_conversation = list(stash.load_binaries_in_messages(stashed_conversation))

        # Verify loaded images match originals
        loaded_image1 = loaded_conversation[1].parts[0].content[1]
        loaded_image2 = loaded_conversation[3].parts[0].content[1]

        assert isinstance(loaded_image1, BinaryContent)
        assert loaded_image1.data == b"image1_data"
        assert loaded_image1.media_type == "image/jpeg"

        assert isinstance(loaded_image2, BinaryContent)
        assert loaded_image2.data == b"image2_data"
        assert loaded_image2.media_type == "image/png"

    def test_no_deduplication_across_messages(self, temp_storage_dir):
        """Test that identical binary content creates separate storage entries."""
        adapter = FSAdapter(str(temp_storage_dir))
        stash = BinaryStash(adapter)

        # Same image content in different messages
        shared_image = BinaryContent(data=b"shared_image_data", media_type="image/jpeg")

        messages = [
            ModelRequest(
                parts=[
                    UserPromptPart(
                        content=[TextPart(content="First message with image:"), shared_image]
                    )
                ]
            ),
            ModelRequest(
                parts=[
                    UserPromptPart(
                        content=[TextPart(content="Second message with same image:"), shared_image]
                    )
                ]
            ),
        ]

        # Stash messages
        stashed_messages = list(stash.stash_binaries_in_messages(messages))

        # Get URLs from both messages
        url1 = stashed_messages[0].parts[0].content[1].url
        url2 = stashed_messages[1].parts[0].content[1].url

        # URLs should be different (UUID-based, no deduplication)
        assert url1 != url2

        # Verify both files exist in storage
        key1 = url1.removeprefix("media://")
        key2 = url2.removeprefix("media://")
        assert adapter.exists(key1)
        assert adapter.exists(key2)

        # Count files in storage directory - should be 2 separate files
        storage_files = list(temp_storage_dir.glob("*"))
        assert len(storage_files) == 2

    def test_error_handling_missing_file(self, temp_storage_dir):
        """Test error handling when loading references to missing files."""
        adapter = FSAdapter(str(temp_storage_dir))
        stash = BinaryStash(adapter)

        # Create message with stashed content
        image = BinaryContent(data=b"test_image", media_type="image/jpeg")
        stashed_messages = list(
            stash.stash_binaries_in_messages(
                [ModelRequest(parts=[UserPromptPart(content=[image])])]
            )
        )

        # Remove the file from storage
        stashed_url = stashed_messages[0].parts[0].content[0]
        key = stashed_url.url.removeprefix("media://")
        file_path = temp_storage_dir / key
        file_path.unlink()

        # Try to load - should raise error
        with pytest.raises(RuntimeError, match="Binary content not found"):
            list(stash.load_binaries_in_messages(stashed_messages))

    def test_large_binary_content(self, temp_storage_dir):
        """Test handling of large binary content."""
        adapter = FSAdapter(str(temp_storage_dir))
        stash = BinaryStash(adapter)

        # Create large binary content (1MB)
        large_data = b"x" * (1024 * 1024)
        large_image = BinaryContent(data=large_data, media_type="image/jpeg")

        message = ModelRequest(
            parts=[UserPromptPart(content=[TextPart(content="Large image:"), large_image])]
        )

        # Stash and load
        stashed_messages = list(stash.stash_binaries_in_messages([message]))
        loaded_messages = list(stash.load_binaries_in_messages(stashed_messages))

        # Verify content integrity
        loaded_image = loaded_messages[0].parts[0].content[1]
        assert isinstance(loaded_image, BinaryContent)
        assert loaded_image.data == large_data
        assert len(loaded_image.data) == 1024 * 1024

    def test_empty_messages_list(self, temp_storage_dir):
        """Test handling of empty message lists."""
        adapter = FSAdapter(str(temp_storage_dir))
        stash = BinaryStash(adapter)

        # Empty list should work fine
        stashed = list(stash.stash_binaries_in_messages([]))
        loaded = list(stash.load_binaries_in_messages([]))

        assert stashed == []
        assert loaded == []

    def test_messages_without_binary_content(self, temp_storage_dir):
        """Test handling of messages that contain no binary content."""
        adapter = FSAdapter(str(temp_storage_dir))
        stash = BinaryStash(adapter)

        text_only_messages = [
            ModelRequest(parts=[SystemPromptPart(content="System message")]),
            ModelRequest(parts=[UserPromptPart(content=[TextPart(content="Just text content")])]),
            ModelResponse(parts=[TextPart(content="Response text")]),
        ]

        # Stash and load should be no-ops
        stashed = list(stash.stash_binaries_in_messages(text_only_messages))
        loaded = list(stash.load_binaries_in_messages(stashed))

        # Messages should be identical (deep copied but same content)
        assert len(stashed) == 3
        assert len(loaded) == 3

        for orig, stashed_msg, loaded_msg in zip(text_only_messages, stashed, loaded, strict=False):
            assert isinstance(orig, type(stashed_msg)) and isinstance(stashed_msg, type(loaded_msg))
            assert orig.parts == stashed_msg.parts == loaded_msg.parts

    def test_nested_content_structures(self, temp_storage_dir):
        """Test handling of complex nested content structures."""
        adapter = FSAdapter(str(temp_storage_dir))
        stash = BinaryStash(adapter)

        # Create message with deeply nested content structure
        image = BinaryContent(data=b"nested_image", media_type="image/jpeg")

        # Complex nested structure
        message = ModelRequest(
            parts=[
                UserPromptPart(
                    content=[
                        TextPart(content="Start"),
                        image,
                        TextPart(content="Middle"),
                        image,  # Same image again for deduplication test
                        TextPart(content="End"),
                    ]
                )
            ]
        )

        # Process through stash/load cycle
        stashed = list(stash.stash_binaries_in_messages([message]))
        loaded = list(stash.load_binaries_in_messages(stashed))

        # Verify structure is preserved
        loaded_content = loaded[0].parts[0].content

        assert len(loaded_content) == 5
        assert isinstance(loaded_content[0], TextPart)
        assert loaded_content[0].content == "Start"

        assert isinstance(loaded_content[1], BinaryContent)
        assert loaded_content[1].data == b"nested_image"

        assert isinstance(loaded_content[2], TextPart)
        assert loaded_content[2].content == "Middle"

        assert isinstance(loaded_content[3], BinaryContent)
        assert loaded_content[3].data == b"nested_image"

        assert isinstance(loaded_content[4], TextPart)
        assert loaded_content[4].content == "End"
