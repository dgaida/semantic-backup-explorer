"""Module for synchronizing files between local and backup directories."""

import shutil
from pathlib import Path
from typing import Optional, Protocol


class SyncProgressCallback(Protocol):
    """Protocol for sync progress callbacks."""

    def __call__(self, current: int, total: int, filename: str, error: Optional[str] = None) -> None:
        """
        Called for each file processed.

        Args:
            current: Current file number (1-indexed).
            total: Total number of files.
            filename: Relative path of current file.
            error: Error message if sync failed, None if successful.
        """
        ...


def sync_files(
    files_to_sync: list[str], source_root: str | Path, target_root: str | Path, callback: Optional[SyncProgressCallback] = None
) -> tuple[list[str], list[tuple[str, str]]]:
    """
    Copies files from source_root to target_root.

    Args:
        files_to_sync: List of relative file paths to copy.
        source_root: Source directory.
        target_root: Target directory.
        callback: Optional progress callback.

    Returns:
        Tuple of (synced_files, errors) where errors is a list of (filename, error_msg).

    Raises:
        FileNotFoundError: If source_root does not exist.
    """
    source_root = Path(source_root)
    target_root = Path(target_root)

    if not source_root.exists():
        raise FileNotFoundError(f"Source root does not exist: {source_root}")

    synced = []
    errors = []
    total = len(files_to_sync)

    for i, rel_path in enumerate(files_to_sync):
        src = source_root / rel_path
        dst = target_root / rel_path

        error_msg = None
        try:
            # Create target directory if it doesn't exist
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            synced.append(rel_path)
        except Exception as e:
            error_msg = str(e)
            errors.append((rel_path, error_msg))

        if callback:
            callback(i + 1, total, rel_path, error_msg)

    return synced, errors
