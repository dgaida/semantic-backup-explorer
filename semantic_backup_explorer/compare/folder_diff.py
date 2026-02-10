"""Module for comparing local folders with backup contents."""

import os
from pathlib import Path
from typing import TypedDict, Union


class FolderDiffResult(TypedDict):
    """Result of folder comparison."""

    only_local: list[str]
    only_backup: list[str]
    in_both: list[str]


def get_folder_content(folder_path: str | Path) -> dict[str, float]:
    """
    Returns a dictionary of relative file paths and their modification times.

    Args:
        folder_path: Path to the folder to scan.

    Returns:
        Dictionary mapping relative file paths to their modification timestamps.
    """
    folder_path = Path(folder_path)
    if not folder_path.exists():
        return {}

    files: dict[str, float] = {}
    for root, _, filenames in os.walk(folder_path):
        for f in filenames:
            full_path = Path(root) / f
            rel_path = str(full_path.relative_to(folder_path))
            try:
                files[rel_path] = os.path.getmtime(full_path)
            except Exception:
                files[rel_path] = 0.0
    return files


def compare_folders(local_path: str | Path, backup_files: Union[list[str], dict[str, float]]) -> FolderDiffResult:
    """
    Compares local folder content with backup files.

    Files with newer local modification times are included in 'only_local' to trigger sync.

    Args:
        local_path: Path to the local folder.
        backup_files: Either a list of relative paths or a dictionary mapping
                     relative paths to modification timestamps.

    Returns:
        A TypedDict containing lists of files 'only_local', 'only_backup', and 'in_both'.

    Raises:
        FileNotFoundError: If local_path does not exist.
        NotADirectoryError: If local_path is not a directory.
    """
    local_path = Path(local_path)
    if not local_path.exists():
        raise FileNotFoundError(f"Local path does not exist: {local_path}")
    if not local_path.is_dir():
        raise NotADirectoryError(f"Local path is not a directory: {local_path}")

    local_files_dict = get_folder_content(local_path)
    local_paths = set(local_files_dict.keys())

    if isinstance(backup_files, dict):
        backup_paths = set(backup_files.keys())
    else:
        backup_paths = set(backup_files)

    only_local = local_paths - backup_paths
    only_backup = backup_paths - local_paths
    in_both = local_paths & backup_paths

    # Check for newer files in local
    newer_locally = set()
    if isinstance(backup_files, dict):
        for path in in_both:
            local_mtime = local_files_dict.get(path, 0.0)
            backup_mtime = backup_files.get(path, 0.0)
            # Use a small epsilon for float comparison (0.1 seconds)
            if local_mtime > backup_mtime + 0.1:
                newer_locally.add(path)

    only_local.update(newer_locally)
    in_both = in_both - newer_locally

    return {"only_local": sorted(list(only_local)), "only_backup": sorted(list(only_backup)), "in_both": sorted(list(in_both))}
