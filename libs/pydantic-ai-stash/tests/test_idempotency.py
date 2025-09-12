"""Tests for idempotency of stash/load operations."""

from pydantic_ai.messages import (
    BinaryContent,
    ImageUrl,
    ModelRequest,
    TextPart,
    UserPromptPart,
)

from pydantic_ai_stash.core import BinaryStash


class TestIdempotency:
    """Test that stash/load operations are idempotent."""

    def test_multiple_stash_cycles_idempotent(self, fs_adapter):
        """Test that stashing multiple times produces the same result."""
        stash = BinaryStash(fs_adapter)

        # Create message with binary content
        binary_content = BinaryContent(
            data=b"test_data",
            media_type="image/jpeg",
            identifier="test-id",
            vendor_metadata={"key": "value"},
        )
        original_message = ModelRequest(
            parts=[
                UserPromptPart(
                    content=[
                        TextPart(content="Before"),
                        binary_content,
                        TextPart(content="After"),
                    ]
                )
            ]
        )

        # First stash
        stashed_1 = next(iter(stash.stash_binaries_in_messages([original_message])))

        # Second stash (should be no-op since already stashed)
        stashed_2 = next(iter(stash.stash_binaries_in_messages([stashed_1])))

        # Third stash
        stashed_3 = next(iter(stash.stash_binaries_in_messages([stashed_2])))

        # All stashed versions should be identical
        assert stashed_1.parts[0].content[1].url == stashed_2.parts[0].content[1].url
        assert stashed_2.parts[0].content[1].url == stashed_3.parts[0].content[1].url

        # Should all be ImageUrl objects
        assert isinstance(stashed_1.parts[0].content[1], ImageUrl)
        assert isinstance(stashed_2.parts[0].content[1], ImageUrl)
        assert isinstance(stashed_3.parts[0].content[1], ImageUrl)

    def test_multiple_load_cycles_idempotent(self, fs_adapter):
        """Test that loading multiple times produces the same result."""
        stash = BinaryStash(fs_adapter)

        # Create and stash message first
        binary_content = BinaryContent(
            data=b"test_data",
            media_type="image/jpeg",
            identifier="test-id",
            vendor_metadata={"key": "value"},
        )
        original_message = ModelRequest(
            parts=[UserPromptPart(content=[TextPart(content="Test"), binary_content])]
        )
        stashed_message = next(iter(stash.stash_binaries_in_messages([original_message])))

        # Multiple load cycles
        loaded_1 = next(iter(stash.load_binaries_in_messages([stashed_message])))
        loaded_2 = next(iter(stash.load_binaries_in_messages([loaded_1])))
        loaded_3 = next(iter(stash.load_binaries_in_messages([loaded_2])))

        # All should have identical binary content
        bc_1 = loaded_1.parts[0].content[1]
        bc_2 = loaded_2.parts[0].content[1]
        bc_3 = loaded_3.parts[0].content[1]

        assert isinstance(bc_1, BinaryContent)
        assert isinstance(bc_2, BinaryContent)
        assert isinstance(bc_3, BinaryContent)

        assert bc_1.data == bc_2.data == bc_3.data
        assert bc_1.media_type == bc_2.media_type == bc_3.media_type
        assert bc_1.identifier == bc_2.identifier == bc_3.identifier
        assert bc_1.vendor_metadata == bc_2.vendor_metadata == bc_3.vendor_metadata

    def test_stash_load_stash_load_cycles(self, fs_adapter):
        """Test alternating stash/load cycles maintain consistency."""
        stash = BinaryStash(fs_adapter)

        # Original message
        binary_content = BinaryContent(
            data=b"cycle_test",
            media_type="image/png",
            identifier="cycle-id",
            vendor_metadata={"test": "cycle"},
        )
        original = ModelRequest(
            parts=[UserPromptPart(content=[binary_content, TextPart(content="Text")])]
        )

        # Cycle 1: stash -> load
        stashed_1 = next(iter(stash.stash_binaries_in_messages([original])))
        loaded_1 = next(iter(stash.load_binaries_in_messages([stashed_1])))

        # Cycle 2: stash -> load
        stashed_2 = next(iter(stash.stash_binaries_in_messages([loaded_1])))
        loaded_2 = next(iter(stash.load_binaries_in_messages([stashed_2])))

        # Cycle 3: stash -> load
        stashed_3 = next(iter(stash.stash_binaries_in_messages([loaded_2])))
        loaded_3 = next(iter(stash.load_binaries_in_messages([stashed_3])))

        # All loaded results should be equivalent to original (plus stash UUID)
        for loaded in [loaded_1, loaded_2, loaded_3]:
            bc = loaded.parts[0].content[0]
            assert isinstance(bc, BinaryContent)
            assert bc.data == binary_content.data
            assert bc.media_type == binary_content.media_type
            assert bc.identifier == binary_content.identifier

            # Vendor metadata should contain original data plus the stash UUID
            dict(binary_content.vendor_metadata) if binary_content.vendor_metadata else {}
            assert "_stash_uuid" in bc.vendor_metadata
            assert bc.vendor_metadata["test"] == "cycle"  # Original metadata preserved

        # All stashed results should have valid media:// URLs
        url_1 = stashed_1.parts[0].content[0].url
        url_2 = stashed_2.parts[0].content[0].url
        url_3 = stashed_3.parts[0].content[0].url

        # URLs should all be valid media:// URLs (UUIDs may differ)
        assert url_1.startswith("media://")
        assert url_2.startswith("media://")
        assert url_3.startswith("media://")

        # Now that we have UUID reuse, URLs should be the same after first cycle
        assert url_2 == url_1  # Should reuse UUID from loaded_1
        assert url_3 == url_1  # Should reuse UUID from loaded_2

    def test_mixed_content_cycles_idempotent(self, fs_adapter):
        """Test cycles with mixed content types remain consistent."""
        stash = BinaryStash(fs_adapter)

        # Message with mixed content
        image = BinaryContent(data=b"image", media_type="image/jpeg")
        audio = BinaryContent(data=b"audio", media_type="audio/wav")

        original = ModelRequest(
            parts=[
                UserPromptPart(content=TextPart(content="Single text")),
                UserPromptPart(
                    content=[
                        TextPart(content="List start"),
                        image,
                        TextPart(content="Between"),
                        audio,
                        TextPart(content="List end"),
                    ]
                ),
            ]
        )

        # Perform multiple cycles
        current = original
        for _cycle in range(3):
            # Stash
            current = next(iter(stash.stash_binaries_in_messages([current])))
            # Load
            current = next(iter(stash.load_binaries_in_messages([current])))

        # Verify final result matches original structure and content
        assert len(current.parts) == 2

        # First part should be unchanged text
        assert isinstance(current.parts[0].content, TextPart)
        assert current.parts[0].content.content == "Single text"

        # Second part should have restored binary content
        content_list = current.parts[1].content
        assert len(content_list) == 5
        assert isinstance(content_list[1], BinaryContent)  # image
        assert isinstance(content_list[3], BinaryContent)  # audio
        assert content_list[1].data == b"image"
        assert content_list[3].data == b"audio"

    def test_empty_and_edge_case_cycles(self, fs_adapter):
        """Test idempotency with edge cases."""
        stash = BinaryStash(fs_adapter)

        # Empty content list
        empty_message = ModelRequest(parts=[UserPromptPart(content=[])])

        # Multiple cycles should not change anything
        result = empty_message
        for _ in range(3):
            result = next(iter(stash.stash_binaries_in_messages([result])))
            result = next(iter(stash.load_binaries_in_messages([result])))

        assert len(result.parts[0].content) == 0

        # Text-only message
        text_only = ModelRequest(parts=[UserPromptPart(content=[TextPart(content="Only text")])])

        result = text_only
        for _ in range(3):
            result = next(iter(stash.stash_binaries_in_messages([result])))
            result = next(iter(stash.load_binaries_in_messages([result])))

        assert len(result.parts[0].content) == 1
        assert isinstance(result.parts[0].content[0], TextPart)
        assert result.parts[0].content[0].content == "Only text"
