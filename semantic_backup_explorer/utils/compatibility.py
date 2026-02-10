"""Compatibility checks and utilities for different Python versions and environments."""

import sys


def check_python_version() -> None:
    """
    Checks if the current Python version is supported.

    Raises:
        RuntimeError: If the Python version is unsupported.
    """
    if sys.version_info < (3, 10):
        raise RuntimeError("Python 3.10 or higher is required.")
    if sys.version_info >= (3, 14):
        raise RuntimeError("Python 3.14+ is not supported due to Pydantic v1 incompatibilities in dependencies.")
