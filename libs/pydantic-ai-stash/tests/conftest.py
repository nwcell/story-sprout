"""Test configuration and fixtures for pydantic-ai-stash."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from pydantic_ai.messages import BinaryContent

from pydantic_ai_stash.adapters import FSAdapter


@pytest.fixture
def temp_storage_dir() -> Iterator[Path]:
    """Provide a directory for testing storage."""
    storage_dir = Path(__file__).parent / "test_stash"

    # Create directory if it doesn't exist
    storage_dir.mkdir(exist_ok=True)

    # Do NOT clean directory - let binaries persist for viewing
    yield storage_dir


@pytest.fixture
def fs_adapter(temp_storage_dir: Path) -> FSAdapter:
    """Provide a filesystem adapter for testing."""
    return FSAdapter(str(temp_storage_dir))


@pytest.fixture
def sample_image_binary() -> BinaryContent:
    """Provide sample image binary content for testing."""
    return BinaryContent(
        data=b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01",
        media_type="image/png",
    )


@pytest.fixture
def sample_audio_binary() -> BinaryContent:
    """Provide sample audio binary content for testing."""
    return BinaryContent(data=b"RIFF\x24\x00\x00\x00WAVE", media_type="audio/wav")


@pytest.fixture
def sample_video_binary() -> BinaryContent:
    """Provide sample video binary content for testing."""
    return BinaryContent(data=b"\x00\x00\x00\x20ftypmp41", media_type="video/mp4")


@pytest.fixture
def sample_document_binary() -> BinaryContent:
    """Provide sample document binary content for testing."""
    return BinaryContent(data=b"%PDF-1.4\n1 0 obj", media_type="application/pdf")


@pytest.fixture
def sample_binary_with_metadata() -> BinaryContent:
    """Provide binary content with metadata for testing."""
    return BinaryContent(
        data=b"test content",
        media_type="image/jpeg",
        identifier="test-image-123",
        vendor_metadata={"source": "test", "quality": "high"},
    )
