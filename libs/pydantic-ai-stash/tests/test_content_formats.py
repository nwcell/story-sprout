"""Tests for different content format handling in pydantic-ai-stash."""

from pydantic_ai.messages import (
    BinaryContent,
    ImageUrl,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)

from pydantic_ai_stash.core import BinaryStash


class TestContentFormats:
    """Test handling of different content formats (list vs single content)."""

    def test_single_binary_content_stash_and_load(self, fs_adapter):
        """Test stashing when content is a single BinaryContent object."""
        stash = BinaryStash(fs_adapter)

        # Create message with single BinaryContent (not in a list)
        binary_content = BinaryContent(data=b"single_content", media_type="image/jpeg")
        message = ModelRequest(parts=[UserPromptPart(content=binary_content)])

        # Stash binaries
        stashed_messages = list(stash.stash_binaries_in_messages([message]))
        stashed_content = stashed_messages[0].parts[0].content

        # Should be converted to URL
        assert isinstance(stashed_content, ImageUrl)
        assert stashed_content.url.startswith("media://")
        assert stashed_content.media_type == "image/jpeg"

        # Load back
        loaded_messages = list(stash.load_binaries_in_messages(stashed_messages))
        loaded_content = loaded_messages[0].parts[0].content

        # Should be back to BinaryContent
        assert isinstance(loaded_content, BinaryContent)
        assert loaded_content.data == b"single_content"
        assert loaded_content.media_type == "image/jpeg"

    def test_single_text_content_unchanged(self, fs_adapter):
        """Test that single text content remains unchanged."""
        stash = BinaryStash(fs_adapter)

        # Create message with single TextPart (not in a list)
        message = ModelRequest(parts=[UserPromptPart(content=TextPart(content="Hello world"))])

        # Stash and load should be no-ops
        stashed_messages = list(stash.stash_binaries_in_messages([message]))
        loaded_messages = list(stash.load_binaries_in_messages(stashed_messages))

        # Content should remain as TextPart
        assert isinstance(stashed_messages[0].parts[0].content, TextPart)
        assert isinstance(loaded_messages[0].parts[0].content, TextPart)
        assert loaded_messages[0].parts[0].content.content == "Hello world"

    def test_mixed_list_content(self, fs_adapter):
        """Test list content with mix of text and binary."""
        stash = BinaryStash(fs_adapter)

        binary_content = BinaryContent(data=b"mixed_content", media_type="image/png")
        text_content = TextPart(content="Description")

        message = ModelRequest(
            parts=[
                UserPromptPart(
                    content=[text_content, binary_content, TextPart(content="More text")]
                )
            ]
        )

        # Stash binaries
        stashed_messages = list(stash.stash_binaries_in_messages([message]))
        stashed_content = stashed_messages[0].parts[0].content

        # Check structure: TextPart, ImageUrl, TextPart
        assert len(stashed_content) == 3
        assert isinstance(stashed_content[0], TextPart)
        assert stashed_content[0].content == "Description"
        assert isinstance(stashed_content[1], ImageUrl)
        assert stashed_content[1].url.startswith("media://")
        assert isinstance(stashed_content[2], TextPart)
        assert stashed_content[2].content == "More text"

        # Load back
        loaded_messages = list(stash.load_binaries_in_messages(stashed_messages))
        loaded_content = loaded_messages[0].parts[0].content

        # Check structure restored: TextPart, BinaryContent, TextPart
        assert len(loaded_content) == 3
        assert isinstance(loaded_content[0], TextPart)
        assert loaded_content[0].content == "Description"
        assert isinstance(loaded_content[1], BinaryContent)
        assert loaded_content[1].data == b"mixed_content"
        assert isinstance(loaded_content[2], TextPart)
        assert loaded_content[2].content == "More text"

    def test_empty_list_content(self, fs_adapter):
        """Test handling of empty list content."""
        stash = BinaryStash(fs_adapter)

        message = ModelRequest(parts=[UserPromptPart(content=[])])

        # Should handle empty lists gracefully
        stashed_messages = list(stash.stash_binaries_in_messages([message]))
        loaded_messages = list(stash.load_binaries_in_messages(stashed_messages))

        assert stashed_messages[0].parts[0].content == []
        assert loaded_messages[0].parts[0].content == []

    def test_multiple_binaries_in_single_content(self, fs_adapter):
        """Test list with multiple binary content items."""
        stash = BinaryStash(fs_adapter)

        binary1 = BinaryContent(data=b"content1", media_type="image/jpeg")
        binary2 = BinaryContent(data=b"content2", media_type="audio/wav")
        binary3 = BinaryContent(data=b"content3", media_type="video/mp4")

        message = ModelRequest(parts=[UserPromptPart(content=[binary1, binary2, binary3])])

        # Stash binaries
        stashed_messages = list(stash.stash_binaries_in_messages([message]))
        stashed_content = stashed_messages[0].parts[0].content

        # All should be converted to appropriate URL types
        assert len(stashed_content) == 3
        assert isinstance(stashed_content[0], ImageUrl)
        assert isinstance(
            stashed_content[1], type(stash._bc_to_typed_url(binary2, "test"))
        )  # AudioUrl
        assert isinstance(
            stashed_content[2], type(stash._bc_to_typed_url(binary3, "test"))
        )  # VideoUrl

        # Load back
        loaded_messages = list(stash.load_binaries_in_messages(stashed_messages))
        loaded_content = loaded_messages[0].parts[0].content

        # All should be back to BinaryContent
        assert len(loaded_content) == 3
        assert all(isinstance(item, BinaryContent) for item in loaded_content)
        assert loaded_content[0].data == b"content1"
        assert loaded_content[1].data == b"content2"
        assert loaded_content[2].data == b"content3"

    def test_nested_message_parts_different_formats(self, fs_adapter):
        """Test message with multiple parts having different content formats."""
        stash = BinaryStash(fs_adapter)

        # Different parts with different content formats
        single_binary = BinaryContent(data=b"single", media_type="image/jpeg")
        list_binary = BinaryContent(data=b"list_item", media_type="image/png")

        message = ModelRequest(
            parts=[
                UserPromptPart(content=single_binary),  # Single content
                UserPromptPart(content=[TextPart(content="Text"), list_binary]),  # List content
                UserPromptPart(content=TextPart(content="Just text")),  # Single text
            ]
        )

        # Stash binaries
        stashed_messages = list(stash.stash_binaries_in_messages([message]))

        # Check each part was handled correctly
        assert isinstance(stashed_messages[0].parts[0].content, ImageUrl)  # Single -> URL
        assert len(stashed_messages[0].parts[1].content) == 2  # List preserved
        assert isinstance(
            stashed_messages[0].parts[1].content[1], ImageUrl
        )  # Binary in list -> URL
        assert isinstance(stashed_messages[0].parts[2].content, TextPart)  # Text unchanged

        # Load back
        loaded_messages = list(stash.load_binaries_in_messages(stashed_messages))

        # Verify round-trip integrity
        assert isinstance(loaded_messages[0].parts[0].content, BinaryContent)
        assert loaded_messages[0].parts[0].content.data == b"single"

        assert len(loaded_messages[0].parts[1].content) == 2
        assert isinstance(loaded_messages[0].parts[1].content[0], TextPart)
        assert isinstance(loaded_messages[0].parts[1].content[1], BinaryContent)
        assert loaded_messages[0].parts[1].content[1].data == b"list_item"

        assert isinstance(loaded_messages[0].parts[2].content, TextPart)
        assert loaded_messages[0].parts[2].content.content == "Just text"

    def test_response_with_single_content(self, fs_adapter):
        """Test that ModelResponse also handles single content correctly."""
        stash = BinaryStash(fs_adapter)

        # ModelResponse with single content (usually TextPart, but could be other types)
        response = ModelResponse(parts=[TextPart(content="AI response")])

        # Should handle gracefully (no changes expected for text)
        stashed_messages = list(stash.stash_binaries_in_messages([response]))
        loaded_messages = list(stash.load_binaries_in_messages(stashed_messages))

        assert isinstance(stashed_messages[0].parts[0], TextPart)
        assert isinstance(loaded_messages[0].parts[0], TextPart)
        assert loaded_messages[0].parts[0].content == "AI response"

    def test_message_part_without_content_attribute(self, fs_adapter):
        """Test handling of message parts that don't have content attribute."""
        stash = BinaryStash(fs_adapter)

        # Create a mock part without content attribute
        from unittest.mock import Mock

        mock_part = Mock(spec=[])  # No content attribute
        message = ModelRequest(parts=[mock_part])

        # Should handle gracefully without errors
        stashed_messages = list(stash.stash_binaries_in_messages([message]))
        loaded_messages = list(stash.load_binaries_in_messages(stashed_messages))

        # Mock part should remain unchanged
        assert stashed_messages[0].parts[0] is not mock_part  # Deep copied
        assert loaded_messages[0].parts[0] is not mock_part  # Deep copied
