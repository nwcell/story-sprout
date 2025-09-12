"""Tests for pydantic-ai-stash with pickled agent result data."""

import pickle
from pathlib import Path

import pytest
from pydantic_ai import BinaryContent

from pydantic_ai_stash import BinaryStash, FSAdapter


class TestPickleData:
    """Test pydantic-ai-stash with real agent result pickle data."""

    def _count_binaries(self, messages):
        """Count BinaryContent objects in messages."""
        count = 0
        for msg in messages:
            if hasattr(msg, "parts"):
                for part in msg.parts:
                    if isinstance(part, BinaryContent):
                        count += 1
                    elif hasattr(part, "content"):
                        if isinstance(part.content, list):
                            count += sum(
                                1 for item in part.content if isinstance(item, BinaryContent)
                            )
                        elif isinstance(part.content, BinaryContent):
                            count += 1
        return count

    def test_pickled_agent_result_stash_cycle(self, temp_storage_dir):
        """Test stash/load cycle with real pickled agent result data."""
        pickle_file = Path(__file__).parent / "test_data" / "agent_result_with_images.pkl"

        # Load pickle data
        with open(pickle_file, "rb") as f:
            agent_result = pickle.load(f)

        # Extract messages from agent result
        messages = agent_result.all_messages()
        orig_count = self._count_binaries(messages)

        if orig_count == 0:
            pytest.skip("No binary content found in pickle data")

        # Setup stash with FSAdapter
        adapter = FSAdapter(str(temp_storage_dir))
        stash = BinaryStash(adapter)

        # Stash binaries in messages
        stashed_messages = stash.stash_binaries_in_messages(messages)

        # Test stashing worked
        files = list(temp_storage_dir.glob("*"))
        assert len(files) > 0, "No files were created during stashing"
        assert len(messages) == len(stashed_messages), "Message count changed during stashing"

        # Load binaries back from stash
        loaded_messages = stash.load_binaries_in_messages(stashed_messages)

        # Test loading worked
        loaded_count = self._count_binaries(loaded_messages)
        assert orig_count == loaded_count, f"Binary count mismatch: {orig_count} -> {loaded_count}"
        assert len(messages) == len(loaded_messages), "Message count changed during loading"

        print(
            f"\n✅ Successfully processed {len(messages)} messages with {orig_count} binary items"
        )
        print(f"📁 Created {len(files)} files in {temp_storage_dir}")
