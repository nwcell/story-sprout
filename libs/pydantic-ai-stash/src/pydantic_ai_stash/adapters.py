import mimetypes
import pathlib
import uuid
from abc import ABC, abstractmethod
from typing import BinaryIO, Protocol

from pydantic_ai import BinaryContent


class StorageAdapter(Protocol):
    def exists(self, key: str) -> bool: ...
    def put(self, key: str, data: bytes) -> None: ...
    def open(self, key: str) -> BinaryIO: ...
    def key_for(self, bc: BinaryContent) -> str: ...
    def stash_content(self, bc: BinaryContent) -> str: ...
    def stash_filter(self, item: object) -> bool: ...
    def load_filter(self, item: object) -> bool: ...


class BaseStorageAdapter(StorageAdapter, ABC):
    def __init__(self):
        pass

    def stash_filter(self, item: object) -> bool:
        """Return True if this adapter can stash the given item."""
        from pydantic_ai.messages import BinaryContent

        return isinstance(item, BinaryContent)

    def load_filter(self, item: object) -> bool:
        """Return True if this adapter can load the given item."""
        from pydantic_ai.messages import AudioUrl, DocumentUrl, ImageUrl, VideoUrl

        return isinstance(item, AudioUrl | DocumentUrl | ImageUrl | VideoUrl)

    def key_for(self, bc: BinaryContent) -> str:
        """Generate a unique key for binary content, preserving original format when possible."""
        base_key = str(uuid.uuid4())

        # Try to get extension from media type using standard mimetypes
        if bc.media_type:
            extension = mimetypes.guess_extension(bc.media_type)
            if extension:
                return f"{base_key}{extension}"

        # If no extension can be determined, just return the UUID
        # The file will be stored as-is without format conversion
        return base_key

    def stash_content(self, bc: BinaryContent) -> str:
        """Stash binary content and return the storage key, handling UUID reuse."""
        # Check if BinaryContent has a previously stashed UUID
        existing_uuid = None
        if bc.vendor_metadata:
            existing_uuid = bc.vendor_metadata.get("_stash_uuid")
        # If we have an existing UUID, check if the file still exists
        if existing_uuid and self.exists(existing_uuid):
            return existing_uuid

        # Generate new key and store if needed
        key = self.key_for(bc)
        if not self.exists(key):
            self.put(key, bc.data)
        return key

    # I/O to be provided by concrete adapters
    @abstractmethod
    def exists(self, key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def put(self, key: str, data: bytes) -> None:
        raise NotImplementedError

    @abstractmethod
    def open(self, key: str) -> BinaryIO:
        raise NotImplementedError


class FSAdapter(BaseStorageAdapter):
    """Minimal local filesystem adapter for quick starts."""

    def __init__(self, root: str | None = None):
        super().__init__()
        if root is None:
            # Default to stashing relative to this module
            module_dir = pathlib.Path(__file__).parent
            self.root = module_dir / "stash"
        else:
            self.root = pathlib.Path(root)

    def exists(self, key: str) -> bool:
        try:
            return (self.root / key).exists()
        except OSError as e:
            raise RuntimeError(f"Failed to check if key '{key}' exists: {e}") from e

    def put(self, key: str, data: bytes) -> None:
        try:
            p = self.root / key
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        except OSError as e:
            raise RuntimeError(f"Failed to store data for key '{key}': {e}") from e

    def open(self, key: str) -> BinaryIO:
        try:
            return (self.root / key).open("rb")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found for key '{key}': {e}") from e
        except OSError as e:
            raise RuntimeError(f"Failed to open file for key '{key}': {e}") from e
