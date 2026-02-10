"""Reusable path operations."""

from pathlib import Path


def normalize_path(path: str | Path) -> str:
    """
    Normalizes path to use forward slashes for internal comparison.

    Args:
        path: The path to normalize.

    Returns:
        The normalized path as a string.
    """
    if not path:
        return ""
    return str(path).replace("\\", "/").rstrip("/")


def get_relative_path(path: Path, root: Path) -> str:
    """
    Safely calculates relative path.

    Args:
        path: The full path.
        root: The root path to be relative to.

    Returns:
        The relative path string.
    """
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
