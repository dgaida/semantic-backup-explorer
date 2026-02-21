"""Utilities for parsing and searching the markdown backup index."""

import datetime
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from semantic_backup_explorer.utils.path_utils import normalize_path


@dataclass
class IndexMetadata:
    """Metadata about the backup index."""

    root_path: Optional[Path]
    label: Optional[str]
    mtime: Optional[datetime.datetime]
    age_days: int


def get_index_metadata(index_path: str | Path) -> IndexMetadata:
    """
    Extracts metadata from the index file.

    Args:
        index_path: Path to the markdown index file.

    Returns:
        An IndexMetadata object.
    """
    index_path = Path(index_path)
    if not index_path.exists():
        return IndexMetadata(None, None, None, 0)

    root_path = None
    label = None
    mtime = datetime.datetime.fromtimestamp(index_path.stat().st_mtime)
    age_days = (datetime.datetime.now() - mtime).days

    with open(index_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("Root: "):
                content_after_root = line[6:].strip()
                if " (Label: " in content_after_root:
                    root_part, label_part = content_after_root.split(" (Label: ", 1)
                    root_path = Path(root_part.strip())
                    label = label_part.rstrip(")").strip()
                else:
                    root_path = Path(content_after_root)
                break

    return IndexMetadata(root_path, label, mtime, age_days)


def find_backup_folder(folder_name: str, index_path: str | Path) -> Optional[str]:
    """
    Searches the index file for a folder header (##) that contains folder_name.

    Args:
        folder_name: The name of the folder to search for.
        index_path: Path to the markdown index file.

    Returns:
        The first matching full path found, or None if no match is found.
    """
    if not os.path.exists(index_path):
        return None

    # folder_name might also contain backslashes if passed from a Windows path
    clean_folder_name = folder_name.replace("\\", "/").rstrip("/").split("/")[-1].lower()

    with open(index_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("## "):
                header_path = line[3:].strip()
                norm_header = header_path.replace("\\", "/").rstrip("/")
                header_folder_name = norm_header.split("/")[-1].lower()

                # Exact match or partial match (e.g. "Finanzen" in "Finanzen (Backup)")
                if clean_folder_name == header_folder_name or clean_folder_name in header_folder_name:
                    return header_path
    return None


def get_all_files_from_index(backup_root: str | Path, index_path: str | Path) -> dict[str, float]:
    """
    Extracts all file paths from the index that are sub-paths of backup_root.

    Args:
        backup_root: The root path in the index to filter by.
        index_path: Path to the markdown index file.

    Returns:
        A dictionary mapping relative paths to modification timestamps.
    """
    files: dict[str, float] = {}
    if not os.path.exists(index_path):
        return files

    norm_root = normalize_path(backup_root)

    with open(index_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("- "):
                line_content = line[2:].strip()

                # Check for mtime
                if " | mtime:" in line_content:
                    try:
                        file_path, mtime_str = line_content.rsplit(" | mtime:", 1)
                        mtime = float(mtime_str)
                    except ValueError:
                        file_path = line_content
                        mtime = 0.0
                else:
                    file_path = line_content
                    mtime = 0.0

                # Skip directories (which end in / or \ in our index format)
                if file_path.endswith("/") or file_path.endswith("\\"):
                    continue

                norm_file = file_path.replace("\\", "/")

                if norm_file.startswith(norm_root):
                    # Check if it's actually a subpath (not just a prefix match of a sibling folder)
                    remainder = norm_file[len(norm_root) :]
                    if not remainder or remainder.startswith("/"):
                        rel_path = remainder.lstrip("/")
                        if rel_path:
                            # Use current OS separator for the returned relative paths
                            # so they match what os.walk produces in compare_folders
                            files[rel_path.replace("/", os.sep)] = mtime
    return files
