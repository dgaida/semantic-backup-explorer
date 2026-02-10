"""Tests for logging utilities."""

import logging

from semantic_backup_explorer.utils.logging_utils import setup_logging


def test_setup_logging(tmp_path):
    log_file = tmp_path / "test.log"
    setup_logging(level=logging.DEBUG, log_file=log_file)

    logger = logging.getLogger("test_logger")
    logger.debug("test message")

    assert log_file.exists()
    content = log_file.read_text()
    assert "test message" in content
    assert "DEBUG" in content
