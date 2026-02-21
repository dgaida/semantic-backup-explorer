"""Tests for configuration validation."""

import pytest

from semantic_backup_explorer.utils.config import BackupConfig


def test_validate_backup_drive_success(tmp_path):
    config = BackupConfig(backup_drive=tmp_path)
    # Should not raise
    config.validate_backup_drive()


def test_validate_backup_drive_not_exists(tmp_path):
    config = BackupConfig(backup_drive=tmp_path / "nonexistent")
    with pytest.raises(ValueError, match="Backup drive not found"):
        config.validate_backup_drive()


def test_validate_backup_drive_no_longer_checks_writable(tmp_path):
    # We relaxed the check to avoid false positives on Windows roots.
    # It should succeed even if read-only, as long as it exists.
    drive = tmp_path / "readonly"
    drive.mkdir()
    drive.chmod(0o555)  # Read and execute only

    config = BackupConfig(backup_drive=drive)
    try:
        # Should not raise PermissionError anymore
        config.validate_backup_drive()
    finally:
        drive.chmod(0o777)
