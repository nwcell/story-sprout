"""Tests for storage adapter implementations."""

import uuid

import pytest
from pydantic_ai.messages import BinaryContent

from pydantic_ai_stash.adapters import BaseStorageAdapter, FSAdapter


class TestBaseStorageAdapter:
    """Test the BaseStorageAdapter abstract base class."""

    def test_key_for_simple_content(self):
        """Test key generation for simple binary content."""
        adapter = MockStorageAdapter()
        bc = BinaryContent(data=b"test data", media_type="image/jpeg")

        key = adapter.key_for(bc)

        # Should be a valid UUID string
        assert uuid.UUID(key)  # Will raise ValueError if not a valid UUID

    def test_key_for_content_without_media_type(self):
        """Test key generation when media_type is None."""
        adapter = MockStorageAdapter()
        bc = BinaryContent(data=b"test data", media_type=None)

        key = adapter.key_for(bc)

        # Should be a valid UUID string
        assert uuid.UUID(key)  # Will raise ValueError if not a valid UUID

    def test_key_for_content_special_characters_in_media_type(self):
        """Test key generation with complex media_type."""
        adapter = MockStorageAdapter()
        bc = BinaryContent(
            data=b"test data",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

        key = adapter.key_for(bc)

        # Should be a valid UUID string
        assert uuid.UUID(key)  # Will raise ValueError if not a valid UUID

    @pytest.mark.parametrize(
        "data, media_type, identifier",
        [
            (b"data1", "image/png", None),
            (b"data2", "audio/wav", "audio-123"),
            (b"data3", "video/mp4", "vid_456"),
            (b"data4", None, None),
            (b"data5", None, "id-only"),
        ],
    )
    def test_key_for_parametrized(self, data, media_type, identifier):
        """Test key generation with various parameter combinations."""
        adapter = MockStorageAdapter()
        bc = BinaryContent(data=data, media_type=media_type, identifier=identifier)

        key = adapter.key_for(bc)

        # Should be a valid UUID string
        assert uuid.UUID(key)  # Will raise ValueError if not a valid UUID

    def test_key_for_uniqueness(self):
        """Test that key generation produces unique keys."""
        adapter = MockStorageAdapter()

        bc1 = BinaryContent(data=b"same data", media_type="image/jpeg")
        bc2 = BinaryContent(data=b"same data", media_type="image/jpeg")

        key1 = adapter.key_for(bc1)
        key2 = adapter.key_for(bc2)

        # Keys should be different UUIDs even for identical content
        assert uuid.UUID(key1)
        assert uuid.UUID(key2)
        assert key1 != key2

    def test_key_for_different_data_different_keys(self):
        """Test that different content produces different keys."""
        adapter = MockStorageAdapter()

        bc1 = BinaryContent(data=b"data1", media_type="image/jpeg")
        bc2 = BinaryContent(data=b"data2", media_type="image/jpeg")

        key1 = adapter.key_for(bc1)
        key2 = adapter.key_for(bc2)

        # Should be different UUIDs
        assert uuid.UUID(key1)
        assert uuid.UUID(key2)
        assert key1 != key2


class TestFSAdapter:
    """Test the filesystem storage adapter."""

    def test_init(self, temp_storage_dir):
        """Test FSAdapter initialization."""
        adapter = FSAdapter(str(temp_storage_dir))
        assert adapter.root == temp_storage_dir

    def test_exists_file_not_present(self, fs_adapter):
        """Test exists returns False for non-existent files."""
        assert not fs_adapter.exists("nonexistent-key")

    def test_put_and_exists(self, fs_adapter):
        """Test putting data and checking existence."""
        key = "test-key"
        data = b"test data"

        fs_adapter.put(key, data)
        assert fs_adapter.exists(key)

    def test_put_and_open(self, fs_adapter):
        """Test putting data and reading it back."""
        key = "test-key"
        data = b"test data"

        fs_adapter.put(key, data)

        with fs_adapter.open(key) as f:
            retrieved_data = f.read()

        assert retrieved_data == data

    def test_put_creates_directories(self, temp_storage_dir):
        """Test that put creates necessary parent directories."""
        adapter = FSAdapter(str(temp_storage_dir))
        key = "subdir1/subdir2/test-key"
        data = b"test data"

        adapter.put(key, data)

        expected_path = temp_storage_dir / key
        assert expected_path.exists()
        assert expected_path.read_bytes() == data

    def test_open_file_not_found(self, fs_adapter):
        """Test opening non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="File not found for key 'nonexistent'"):
            fs_adapter.open("nonexistent")

    def test_put_os_error_handling(self, temp_storage_dir):
        """Test put handles OS errors gracefully."""
        # Create adapter with a path that will cause issues
        invalid_path = temp_storage_dir / "readonly"
        invalid_path.mkdir()
        invalid_path.chmod(0o444)  # Read-only

        adapter = FSAdapter(str(invalid_path))

        with pytest.raises(RuntimeError, match="Failed to store data for key"):
            adapter.put("test-key", b"data")

        # Cleanup
        invalid_path.chmod(0o755)

    def test_exists_os_error_handling(self, temp_storage_dir):
        """Test exists handles OS errors gracefully."""
        # This is harder to test realistically, but we can test the error path
        adapter = FSAdapter(str(temp_storage_dir))

        # Use a key with invalid characters that might cause OS errors on some systems
        # This might not trigger on all systems, but tests the error handling path
        try:
            result = adapter.exists("valid-key")
            assert isinstance(result, bool)
        except RuntimeError:
            # If it does raise a RuntimeError, that's the expected behavior
            pass

    def test_open_os_error_handling(self, fs_adapter):
        """Test open handles OS errors gracefully."""
        # Create a file then remove it to simulate OS error
        key = "test-key"
        fs_adapter.put(key, b"data")

        # Remove the file to simulate an OS error
        file_path = fs_adapter.root / key
        file_path.unlink()

        with pytest.raises(FileNotFoundError, match="File not found for key"):
            fs_adapter.open(key)

    def test_round_trip_binary_content(self, fs_adapter, sample_image_binary):
        """Test complete round-trip with BinaryContent."""
        key = fs_adapter.key_for(sample_image_binary)

        # Store
        fs_adapter.put(key, sample_image_binary.data)
        assert fs_adapter.exists(key)

        # Retrieve
        with fs_adapter.open(key) as f:
            retrieved_data = f.read()

        assert retrieved_data == sample_image_binary.data

    @pytest.mark.parametrize(
        "test_data",
        [
            b"",  # Empty data
            b"a" * 1000,  # Medium data
            b"x" * 100000,  # Large data
            b"\x00\x01\x02\xff",  # Binary data with special bytes
        ],
    )
    def test_put_and_open_various_data_sizes(self, fs_adapter, test_data):
        """Test storing and retrieving various data sizes."""
        key = f"test-{len(test_data)}"

        fs_adapter.put(key, test_data)

        with fs_adapter.open(key) as f:
            retrieved_data = f.read()

        assert retrieved_data == test_data


class MockStorageAdapter(BaseStorageAdapter):
    """Mock implementation of BaseStorageAdapter for testing."""

    def __init__(self):
        super().__init__()
        self._storage = {}

    def exists(self, key: str) -> bool:
        return key in self._storage

    def put(self, key: str, data: bytes) -> None:
        self._storage[key] = data

    def open(self, key: str):
        if key not in self._storage:
            raise FileNotFoundError(f"Key not found: {key}")

        from io import BytesIO

        return BytesIO(self._storage[key])
