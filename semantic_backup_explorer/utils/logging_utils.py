"""Logging utilities for consistent logging across the application."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
) -> None:
    """
    Configure application-wide logging.

    Args:
        level: Logging level (default: INFO).
        log_file: Optional file path for logging. If None, logs only to console.
    """
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", handlers=handlers, force=True
    )
