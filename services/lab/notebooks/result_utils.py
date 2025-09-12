"""
Utilities for saving and loading agent results as pickle files.
"""

import pickle
from datetime import datetime
from pathlib import Path
from typing import Any


def save_result(result: Any, filename: str = None, directory: str = "results") -> Path:
    """
    Save a result object as a pickle file.

    Args:
        result: The object to save (agent result, messages, etc.)
        filename: Optional filename. If None, uses timestamp.
        directory: Directory to save in (relative to current working dir)

    Returns:
        Path to the saved pickle file
    """
    # Create results directory if it doesn't exist
    results_dir = Path(directory)
    results_dir.mkdir(exist_ok=True)

    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"agent_result_{timestamp}.pkl"

    # Ensure .pkl extension
    if not filename.endswith(".pkl"):
        filename = f"{filename}.pkl"

    # Save the pickle
    filepath = results_dir / filename
    with open(filepath, "wb") as f:
        pickle.dump(result, f, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"💾 Saved result to: {filepath}")
    print(f"📊 File size: {filepath.stat().st_size} bytes")

    return filepath


def load_result(filepath: str | Path) -> Any:
    """
    Load a result object from a pickle file.

    Args:
        filepath: Path to the pickle file

    Returns:
        The loaded object
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Pickle file not found: {filepath}")

    try:
        with open(filepath, "rb") as f:
            result = pickle.load(f)
    except FileNotFoundError as e:
        print(f"Failed to load pickle file: {e}")
        return None

    print(f"📤 Loaded result from: {filepath}")
    return result


def list_saved_results(directory: str = "results") -> list[Path]:
    """
    List all saved pickle files in the results directory.

    Args:
        directory: Directory to search for pickle files

    Returns:
        List of pickle file paths
    """
    results_dir = Path(directory)
    if not results_dir.exists():
        print(f"Results directory '{directory}' doesn't exist yet")
        return []

    pkl_files = list(results_dir.glob("*.pkl"))
    pkl_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)  # Sort by modification time

    print(f"📁 Found {len(pkl_files)} pickle files in '{directory}':")
    for pkl_file in pkl_files:
        size = pkl_file.stat().st_size
        mtime = datetime.fromtimestamp(pkl_file.stat().st_mtime)
        print(f"  - {pkl_file.name} ({size} bytes, {mtime.strftime('%Y-%m-%d %H:%M:%S')})")

    return pkl_files


def save_agent_result(result, include_messages: bool = True, filename: str = None) -> Path:
    """
    Save an agent result with optional message extraction.

    Args:
        result: Pydantic AI agent result
        include_messages: Whether to save all messages
        filename: Optional custom filename

    Returns:
        Path to saved pickle file
    """
    save_data = {
        "result": result,
        "output": result.output,
        "timestamp": datetime.now().isoformat(),
    }

    if include_messages:
        save_data["all_messages"] = result.all_messages()
        save_data["new_messages"] = result.new_messages()

    return save_result(save_data, filename, directory="agent_results")
