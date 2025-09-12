"""Tests for BinaryStash core functionality."""

import copy
from unittest.mock import Mock

import pytest
from pydantic_ai.messages import (
    AudioUrl,
    BinaryContent,
    DocumentUrl,
    ImageUrl,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
    VideoUrl,
)

from pydantic_ai_stash.core import BinaryStash


class TestBinaryStash:
    """Test the BinaryStash class."""

    def test_init(self, fs_adapter):
        """Test BinaryStash initialization."""
        stash = BinaryStash(fs_adapter)
        assert stash.storage is fs_adapter

    def test_bc_to_typed_url_image(self, fs_adapter):
        """Test conversion of image BinaryContent to ImageUrl."""
        stash = BinaryStash(fs_adapter)
        bc = BinaryContent(
            data=b"image data",
            media_type="image/jpeg",
            identifier="img-123",
            vendor_metadata={"source": "test"},
        )

        result = stash._bc_to_typed_url(bc, "media://test-key")

        assert isinstance(result, ImageUrl)
        assert result.url == "media://test-key"
        assert result.media_type == "image/jpeg"
        assert result.identifier == "img-123"
        assert result.vendor_metadata == {"source": "test"}

    def test_bc_to_typed_url_audio(self, fs_adapter):
        """Test conversion of audio BinaryContent to AudioUrl."""
        stash = BinaryStash(fs_adapter)
        bc = BinaryContent(data=b"audio data", media_type="audio/wav", identifier="audio-456")

        result = stash._bc_to_typed_url(bc, "media://audio-key")

        assert isinstance(result, AudioUrl)
        assert result.url == "media://audio-key"
        assert result.media_type == "audio/wav"
        assert result.identifier == "audio-456"

    def test_bc_to_typed_url_video(self, fs_adapter):
        """Test conversion of video BinaryContent to VideoUrl."""
        stash = BinaryStash(fs_adapter)
        bc = BinaryContent(data=b"video data", media_type="video/mp4")

        result = stash._bc_to_typed_url(bc, "media://video-key")

        assert isinstance(result, VideoUrl)
        assert result.url == "media://video-key"
        assert result.media_type == "video/mp4"

    def test_bc_to_typed_url_document(self, fs_adapter):
        """Test conversion of document BinaryContent to DocumentUrl."""
        stash = BinaryStash(fs_adapter)
        bc = BinaryContent(data=b"document data", media_type="application/pdf")

        result = stash._bc_to_typed_url(bc, "media://doc-key")

        assert isinstance(result, DocumentUrl)
        assert result.url == "media://doc-key"
        assert result.media_type == "application/pdf"

    def test_bc_to_typed_url_unknown_fallback(self, fs_adapter):
        """Test that unknown media types fallback to DocumentUrl."""
        stash = BinaryStash(fs_adapter)
        bc = BinaryContent(data=b"unknown data", media_type="application/unknown")

        result = stash._bc_to_typed_url(bc, "media://unknown-key")

        assert isinstance(result, DocumentUrl)
        assert result.url == "media://unknown-key"
        assert result.media_type == "application/unknown"

    @pytest.mark.parametrize(
        "media_type, expected_type",
        [
            ("image/png", ImageUrl),
            ("image/jpeg", ImageUrl),
            ("audio/wav", AudioUrl),
            ("audio/mpeg", AudioUrl),
            ("video/mp4", VideoUrl),
            ("video/webm", VideoUrl),
            ("application/pdf", DocumentUrl),
            ("text/plain", DocumentUrl),
            ("application/custom", DocumentUrl),  # Unknown type
        ],
    )
    def test_bc_to_typed_url_media_type_mapping(self, fs_adapter, media_type, expected_type):
        """Test media type to URL type mapping."""
        stash = BinaryStash(fs_adapter)
        bc = BinaryContent(data=b"test data", media_type=media_type)

        result = stash._bc_to_typed_url(bc, "media://test-key")

        assert isinstance(result, expected_type)
        assert result.media_type == media_type

    def test_stash_binary_new_file(self, fs_adapter, sample_image_binary):
        """Test stashing binary content creates new file."""
        stash = BinaryStash(fs_adapter)

        result = stash.stash_binary(sample_image_binary)

        assert isinstance(result, ImageUrl)
        assert result.url.startswith("media://")
        assert result.media_type == "image/png"

        # Verify file was created
        key = result.url.removeprefix("media://")
        assert fs_adapter.exists(key)

    def test_stash_binary_multiple_calls(self, fs_adapter, sample_image_binary):
        """Test stashing binary content multiple times creates separate entries."""
        stash = BinaryStash(fs_adapter)

        # First stash
        result1 = stash.stash_binary(sample_image_binary)

        # Second stash of same content
        result2 = stash.stash_binary(sample_image_binary)

        # Should return different URLs (UUID-based, no deduplication)
        assert result1.url != result2.url
        assert result1.url.startswith("media://")
        assert result2.url.startswith("media://")

        # Both files should exist in storage
        key1 = result1.url.removeprefix("media://")
        key2 = result2.url.removeprefix("media://")
        assert fs_adapter.exists(key1)
        assert fs_adapter.exists(key2)

    def test_stash_binary_storage_error(self, fs_adapter, sample_image_binary):
        """Test stash_binary handles storage errors."""
        stash = BinaryStash(fs_adapter)

        # Mock storage to raise exception
        fs_adapter.put = Mock(side_effect=Exception("Storage error"))

        with pytest.raises(RuntimeError, match="Failed to stash binary content"):
            stash.stash_binary(sample_image_binary)

    def test_load_binary_success(self, fs_adapter, sample_image_binary):
        """Test loading binary content successfully."""
        stash = BinaryStash(fs_adapter)

        # First stash the content
        stashed_url = stash.stash_binary(sample_image_binary)

        # Then load it back
        result = stash.load_binary(stashed_url)

        assert isinstance(result, BinaryContent)
        assert result.data == sample_image_binary.data
        assert result.media_type == sample_image_binary.media_type

    def test_load_binary_with_metadata(self, fs_adapter, sample_binary_with_metadata):
        """Test loading binary content preserves metadata."""
        stash = BinaryStash(fs_adapter)

        # Stash content with metadata
        stashed_url = stash.stash_binary(sample_binary_with_metadata)

        # Load it back
        result = stash.load_binary(stashed_url)

        assert isinstance(result, BinaryContent)
        assert result.data == sample_binary_with_metadata.data
        assert result.media_type == sample_binary_with_metadata.media_type
        assert result.identifier == sample_binary_with_metadata.identifier
        assert result.vendor_metadata == sample_binary_with_metadata.vendor_metadata

    def test_load_binary_non_media_url(self, fs_adapter):
        """Test load_binary returns None for non-media URLs."""
        stash = BinaryStash(fs_adapter)

        regular_url = ImageUrl(url="https://example.com/image.jpg")
        result = stash.load_binary(regular_url)

        assert result is None

    def test_load_binary_no_url_attribute(self, fs_adapter):
        """Test load_binary handles objects without url attribute."""
        stash = BinaryStash(fs_adapter)

        # Create an object without url attribute
        fake_url = Mock(spec=[])  # No url attribute
        result = stash.load_binary(fake_url)

        assert result is None

    def test_load_binary_file_not_found(self, fs_adapter):
        """Test load_binary handles missing files."""
        stash = BinaryStash(fs_adapter)

        # Create URL for non-existent file
        missing_url = ImageUrl(url="media://nonexistent-key")

        with pytest.raises(RuntimeError, match="Binary content not found"):
            stash.load_binary(missing_url)

    def test_load_binary_storage_error(self, fs_adapter, sample_image_binary):
        """Test load_binary handles storage errors."""
        stash = BinaryStash(fs_adapter)

        # Stash content first
        stashed_url = stash.stash_binary(sample_image_binary)

        # Mock storage to raise exception
        fs_adapter.open = Mock(side_effect=Exception("Storage error"))

        with pytest.raises(RuntimeError, match="Failed to load binary content"):
            stash.load_binary(stashed_url)

    def test_transform_message_content_simple_list(self, fs_adapter):
        """Test _transform_message_content with simple list content."""
        stash = BinaryStash(fs_adapter)

        # Create a message with BinaryContent in list
        bc = BinaryContent(data=b"test", media_type="image/jpeg")
        msg = ModelRequest(
            parts=[
                UserPromptPart(content=[TextPart(content="Hello"), bc, TextPart(content="World")])
            ]
        )

        # Transform function that doubles the data
        def transform_fn(item):
            if isinstance(item, BinaryContent):
                return BinaryContent(data=item.data * 2, media_type=item.media_type)
            return None

        stash._transform_message_content(msg, [BinaryContent], transform_fn)

        # Check that BinaryContent was transformed
        content = msg.parts[0].content
        assert isinstance(content[1], BinaryContent)
        assert content[1].data == b"testtest"

    def test_transform_message_content_single_content(self, fs_adapter):
        """Test _transform_message_content with single content item."""
        stash = BinaryStash(fs_adapter)

        # Create a message with single BinaryContent
        bc = BinaryContent(data=b"test", media_type="image/jpeg")
        msg = ModelRequest(parts=[UserPromptPart(content=bc)])

        def transform_fn(item):
            if isinstance(item, BinaryContent):
                return BinaryContent(data=item.data.upper(), media_type=item.media_type)
            return None

        stash._transform_message_content(msg, [BinaryContent], transform_fn)

        # Check that BinaryContent was transformed
        assert isinstance(msg.parts[0].content, BinaryContent)
        assert msg.parts[0].content.data == b"TEST"

    def test_transform_message_content_no_matching_types(self, fs_adapter):
        """Test _transform_message_content with no matching types."""
        stash = BinaryStash(fs_adapter)

        # Create a message with only text content
        msg = ModelRequest(
            parts=[UserPromptPart(content=[TextPart(content="Hello"), TextPart(content="World")])]
        )

        original_content = copy.deepcopy(msg.parts[0].content)

        def transform_fn(item):
            return BinaryContent(data=b"transformed")

        stash._transform_message_content(msg, [BinaryContent], transform_fn)

        # Content should be unchanged
        assert msg.parts[0].content == original_content

    def test_transform_message_content_transform_returns_none(self, fs_adapter):
        """Test _transform_message_content when transform function returns None."""
        stash = BinaryStash(fs_adapter)

        bc = BinaryContent(data=b"test", media_type="image/jpeg")
        msg = ModelRequest(parts=[UserPromptPart(content=[bc])])

        original_bc = copy.deepcopy(bc)

        def transform_fn(item):
            return None  # Always return None

        stash._transform_message_content(msg, [BinaryContent], transform_fn)

        # Content should be unchanged when transform returns None
        assert msg.parts[0].content[0] == original_bc

    def test_stash_binaries_in_messages(self, fs_adapter):
        """Test stashing binaries in a list of messages."""
        stash = BinaryStash(fs_adapter)

        bc1 = BinaryContent(data=b"image1", media_type="image/jpeg")
        bc2 = BinaryContent(data=b"image2", media_type="image/png")

        messages = [
            ModelRequest(
                parts=[UserPromptPart(content=[TextPart(content="Here are images:"), bc1, bc2])]
            ),
            ModelResponse(parts=[TextPart(content="I see the images.")]),
        ]

        # Stash binaries
        result_messages = list(stash.stash_binaries_in_messages(messages))

        assert len(result_messages) == 2

        # Check first message
        content = result_messages[0].parts[0].content
        assert isinstance(content[0], TextPart)
        assert isinstance(content[1], ImageUrl)
        assert isinstance(content[2], ImageUrl)
        assert content[1].url.startswith("media://")
        assert content[2].url.startswith("media://")

        # Check second message unchanged
        assert isinstance(result_messages[1].parts[0], TextPart)

    def test_load_binaries_in_messages(self, fs_adapter):
        """Test loading binaries back from messages."""
        stash = BinaryStash(fs_adapter)

        # First create messages with stashed binaries
        bc = BinaryContent(data=b"test image", media_type="image/jpeg")
        stashed_url = stash.stash_binary(bc)

        messages = [
            ModelRequest(
                parts=[UserPromptPart(content=[TextPart(content="Here is an image:"), stashed_url])]
            )
        ]

        # Load binaries back
        result_messages = list(stash.load_binaries_in_messages(messages))

        assert len(result_messages) == 1
        content = result_messages[0].parts[0].content
        assert isinstance(content[0], TextPart)
        assert isinstance(content[1], BinaryContent)
        assert content[1].data == b"test image"
        assert content[1].media_type == "image/jpeg"

    def test_round_trip_stash_and_load(self, fs_adapter):
        """Test complete round trip: stash then load messages."""
        stash = BinaryStash(fs_adapter)

        original_bc = BinaryContent(
            data=b"test content",
            media_type="image/jpeg",
            identifier="test-123",
            vendor_metadata={"source": "test"},
        )

        original_messages = [
            ModelRequest(
                parts=[
                    UserPromptPart(
                        content=[
                            TextPart(content="Text before"),
                            original_bc,
                            TextPart(content="Text after"),
                        ]
                    )
                ]
            )
        ]

        # Stash binaries
        stashed_messages = list(stash.stash_binaries_in_messages(original_messages))

        # Load binaries back
        loaded_messages = list(stash.load_binaries_in_messages(stashed_messages))

        # Check that we got back equivalent content
        loaded_content = loaded_messages[0].parts[0].content
        assert isinstance(loaded_content[0], TextPart)
        assert loaded_content[0].content == "Text before"

        assert isinstance(loaded_content[1], BinaryContent)
        assert loaded_content[1].data == original_bc.data
        assert loaded_content[1].media_type == original_bc.media_type
        assert loaded_content[1].identifier == original_bc.identifier
        assert loaded_content[1].vendor_metadata == original_bc.vendor_metadata

        assert isinstance(loaded_content[2], TextPart)
        assert loaded_content[2].content == "Text after"

    def test_stash_binaries_deep_copy(self, fs_adapter):
        """Test that stashing creates deep copies of messages."""
        stash = BinaryStash(fs_adapter)

        bc = BinaryContent(data=b"test", media_type="image/jpeg")
        original_message = ModelRequest(parts=[UserPromptPart(content=[bc])])

        # Stash binaries
        stashed_messages = list(stash.stash_binaries_in_messages([original_message]))

        # Original message should be unchanged
        assert isinstance(original_message.parts[0].content[0], BinaryContent)

        # Stashed message should have URL
        assert isinstance(stashed_messages[0].parts[0].content[0], ImageUrl)

    def test_load_binaries_deep_copy(self, fs_adapter):
        """Test that loading creates deep copies of messages."""
        stash = BinaryStash(fs_adapter)

        # Create message with stashed URL (must provide media_type for media:// URLs)
        url = ImageUrl(url="media://test-key", media_type="image/jpeg")
        fs_adapter.put("test-key", b"test data")

        original_message = ModelRequest(parts=[UserPromptPart(content=[url])])

        # Load binaries
        loaded_messages = list(stash.load_binaries_in_messages([original_message]))

        # Original message should be unchanged
        assert isinstance(original_message.parts[0].content[0], ImageUrl)

        # Loaded message should have BinaryContent
        assert isinstance(loaded_messages[0].parts[0].content[0], BinaryContent)

    def test_stash_multiple_binary_types(self, fs_adapter):
        """Test stashing different types of binary content."""
        stash = BinaryStash(fs_adapter)

        image_bc = BinaryContent(data=b"image", media_type="image/jpeg")
        audio_bc = BinaryContent(data=b"audio", media_type="audio/wav")
        video_bc = BinaryContent(data=b"video", media_type="video/mp4")
        doc_bc = BinaryContent(data=b"document", media_type="application/pdf")

        messages = [
            ModelRequest(parts=[UserPromptPart(content=[image_bc, audio_bc, video_bc, doc_bc])])
        ]

        stashed_messages = list(stash.stash_binaries_in_messages(messages))
        content = stashed_messages[0].parts[0].content

        assert isinstance(content[0], ImageUrl)
        assert isinstance(content[1], AudioUrl)
        assert isinstance(content[2], VideoUrl)
        assert isinstance(content[3], DocumentUrl)

    def test_load_mixed_url_types(self, fs_adapter):
        """Test loading different types of URLs back to BinaryContent."""
        stash = BinaryStash(fs_adapter)

        # Store different types of content
        fs_adapter.put("img-key", b"image data")
        fs_adapter.put("audio-key", b"audio data")
        fs_adapter.put("video-key", b"video data")
        fs_adapter.put("doc-key", b"doc data")

        messages = [
            ModelRequest(
                parts=[
                    UserPromptPart(
                        content=[
                            ImageUrl(url="media://img-key", media_type="image/jpeg"),
                            AudioUrl(url="media://audio-key", media_type="audio/wav"),
                            VideoUrl(url="media://video-key", media_type="video/mp4"),
                            DocumentUrl(url="media://doc-key", media_type="application/pdf"),
                            ImageUrl(
                                url="https://example.com/external.jpg"
                            ),  # External URL, should not load
                        ]
                    )
                ]
            )
        ]

        loaded_messages = list(stash.load_binaries_in_messages(messages))
        content = loaded_messages[0].parts[0].content

        # First 4 should be converted to BinaryContent
        assert isinstance(content[0], BinaryContent)
        assert content[0].data == b"image data"
        assert content[0].media_type == "image/jpeg"

        assert isinstance(content[1], BinaryContent)
        assert content[1].data == b"audio data"
        assert content[1].media_type == "audio/wav"

        assert isinstance(content[2], BinaryContent)
        assert content[2].data == b"video data"
        assert content[2].media_type == "video/mp4"

        assert isinstance(content[3], BinaryContent)
        assert content[3].data == b"doc data"
        assert content[3].media_type == "application/pdf"

        # Last one should remain as ImageUrl (external)
        assert isinstance(content[4], ImageUrl)
        assert content[4].url == "https://example.com/external.jpg"
