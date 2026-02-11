"""Tests for utility modules."""

from pathlib import Path

import pytest

from semantic_backup_explorer.exceptions import BackupExplorerError, SyncError
from semantic_backup_explorer.utils.compatibility import check_python_version
from semantic_backup_explorer.utils.config import BackupConfig
from semantic_backup_explorer.utils.path_utils import get_relative_path, normalize_path


def test_normalize_path():
    assert normalize_path("C:\\foo\\bar") == "C:/foo/bar"
    assert normalize_path("/foo/bar/") == "/foo/bar"
    assert normalize_path("") == ""


def test_get_relative_path():
    root = Path("/home/user")
    path = Path("/home/user/docs/file.txt")
    assert get_relative_path(path, root) == "docs/file.txt"

    other_path = Path("/var/log/syslog")
    assert get_relative_path(other_path, root) == "/var/log/syslog"


def test_check_python_version():
    # Should not raise on current version (we are on 3.12)
    check_python_version()


def test_backup_config_defaults():
    config = BackupConfig()
    assert config.index_path == Path("data/backup_index.md")


def test_exceptions():
    with pytest.raises(BackupExplorerError):
        raise BackupExplorerError("test")

    e = SyncError([("file1", "err1")], "sync failed")
    assert e.failed_files == [("file1", "err1")]
