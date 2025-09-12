from __future__ import annotations

import copy
from collections.abc import Callable, Iterable
from typing import NamedTuple

from pydantic_ai.messages import (
    AudioUrl,
    BinaryContent,
    DocumentUrl,
    ImageUrl,
    ModelMessage,
    ModelRequest,
    ModelResponse,
    VideoUrl,
)

from .adapters import StorageAdapter

UrlPart = AudioUrl | BinaryContent | DocumentUrl | ImageUrl | VideoUrl


class TraversalItem(NamedTuple):
    item: object
    should_change: bool


class BinaryStash:
    """Simple binary content stashing for Pydantic AI messages."""

    def __init__(self, storage: StorageAdapter):
        self.storage = storage

    def _bc_to_typed_url(self, bc: BinaryContent, uri: str) -> UrlPart:
        """Convert BinaryContent to appropriate typed URL part."""
        kw = {
            "url": uri,
            "media_type": bc.media_type,
            "identifier": bc.identifier,
            "vendor_metadata": bc.vendor_metadata,
        }

        if bc.is_image:
            return ImageUrl(**kw)
        if bc.is_audio:
            return AudioUrl(**kw)
        if bc.is_video:
            return VideoUrl(**kw)
        if bc.is_document:
            return DocumentUrl(**kw)
        # Fallback to DocumentUrl for unknown types
        return DocumentUrl(**kw)

    def stash_binary(self, bc: BinaryContent) -> UrlPart:
        """Stash a single BinaryContent object and return the typed URL."""
        try:
            key = self.storage.stash_content(bc)
            return self._bc_to_typed_url(bc, f"media://{key}")
        except Exception as e:
            raise RuntimeError(f"Failed to stash binary content: {e}") from e

    def load_binary(self, url_part: UrlPart) -> BinaryContent | None:
        """Load a single URL part back to BinaryContent. Returns None if not a media:// URL."""
        if not hasattr(url_part, "url") or not url_part.url.startswith("media://"):
            return None

        try:
            # Load binary data from storage
            key = url_part.url.removeprefix("media://")
            with self.storage.open(key) as f:
                data = f.read()

            # Preserve existing vendor_metadata and add the UUID for future stashing
            vendor_metadata = dict(url_part.vendor_metadata) if url_part.vendor_metadata else {}
            vendor_metadata["_stash_uuid"] = key

            # Reconstruct BinaryContent with preserved metadata + stored UUID
            return BinaryContent(
                data=data,
                media_type=url_part.media_type,
                identifier=url_part.identifier,
                vendor_metadata=vendor_metadata,
            )
        except FileNotFoundError as e:
            raise RuntimeError(f"Binary content not found for key '{key}': {e}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to load binary content: {e}") from e

    def _transform_message_content(
        self,
        msg: ModelMessage,
        filter_fn: Callable[[object], bool],
        transform_fn: Callable[[object], object],
    ) -> None:
        """Traverse message content and apply transform_fn to items matching filter_fn."""
        # Handle parts that are directly filterable (e.g., BinaryContent as parts)
        for i, part in enumerate(msg.parts):
            if filter_fn(part):
                result = transform_fn(part)
                if result is not None:
                    msg.parts[i] = result
            elif hasattr(part, "content"):
                if isinstance(part.content, list):
                    for j, item in enumerate(part.content):
                        if filter_fn(item):
                            result = transform_fn(item)
                            if result is not None:
                                part.content[j] = result
                elif filter_fn(part.content):
                    result = transform_fn(part.content)
                    if result is not None:
                        part.content = result

    def stash_binaries_in_messages(self, messages: ModelMessage | Iterable[ModelMessage]):
        """Replace all BinaryContent in messages with media:// URLs."""
        if isinstance(messages, ModelRequest | ModelResponse):
            messages = [messages]
        result = []
        for msg in messages:
            new_msg = copy.deepcopy(msg)
            self._transform_message_content(new_msg, self.storage.stash_filter, self.stash_binary)
            result.append(new_msg)
        return result

    def load_binaries_in_messages(self, messages: ModelMessage | Iterable[ModelMessage]):
        """Replace media:// URLs with BinaryContent."""
        if isinstance(messages, ModelRequest | ModelResponse):
            messages = [messages]
        result = []
        for msg in messages:
            new_msg = copy.deepcopy(msg)
            self._transform_message_content(new_msg, self.storage.load_filter, self.load_binary)
            result.append(new_msg)
        return result
