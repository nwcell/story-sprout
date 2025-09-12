#!/usr/bin/env python3
"""Minimal test for BinaryStash functionality."""

from pathlib import Path

from pydantic_ai import BinaryContent

from pydantic_ai_stash import BinaryStash
from pydantic_ai_stash.adapters import FSAdapter


def test_binary_stash_cycle():
    """Test complete stash/load cycle with real binary data."""
    # Create test binary content
    png_data = b"\x89PNG\r\n\x1a\n" + b"fake_image_data" * 100
    jpg_data = b"\xff\xd8\xff\xe0" + b"fake_jpeg_data" * 50

    binaries = [
        BinaryContent(data=png_data, media_type="image/png"),
        BinaryContent(data=jpg_data, media_type="image/jpeg"),
    ]

    # Setup stash with test directory
    test_dir = Path(__file__).parent / "test_stash"
    stash = BinaryStash(FSAdapter(str(test_dir)))

    # Clean test directory
    if test_dir.exists():
        for file in test_dir.iterdir():
            if file.is_file():
                file.unlink()

    # Stash and load
    stashed_urls = [stash.stash_binary(bc) for bc in binaries]
    loaded_binaries = [stash.load_binary(url) for url in stashed_urls]

    # Verify integrity
    orig_sizes = [len(bc.data) for bc in binaries]
    loaded_sizes = [len(bc.data) for bc in loaded_binaries]
    files = list(test_dir.glob("*"))

    assert len(binaries) == len(loaded_binaries) == len(files)
    assert orig_sizes == loaded_sizes
    assert all(
        bc.media_type == lbc.media_type for bc, lbc in zip(binaries, loaded_binaries, strict=False)
    )


if __name__ == "__main__":
    test_binary_stash_cycle()
    print("✅ Binary stash test passed")
