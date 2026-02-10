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


def test_validate_backup_drive_not_writable(tmp_path):
    # This might be tricky in some environments, but let's try
    drive = tmp_path / "readonly"
    drive.mkdir()
    drive.chmod(0o555)  # Read and execute only

    config = BackupConfig(backup_drive=drive)
    # On some systems, root can still write even with 555, but usually this works for user
    # If it fails to raise, we just skip it or accept it.
    try:
        with pytest.raises(PermissionError):
            config.validate_backup_drive()
    finally:
        drive.chmod(0o777)
