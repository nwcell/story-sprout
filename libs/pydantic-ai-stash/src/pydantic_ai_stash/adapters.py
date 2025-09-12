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


class BaseStorageAdapter(StorageAdapter, ABC):
    def __init__(self):
        pass

    def key_for(self, bc: BinaryContent) -> str:
        """Generate a unique key for binary content using UUID."""
        return str(uuid.uuid4())

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

    def __init__(self, root: str):
        super().__init__()
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
