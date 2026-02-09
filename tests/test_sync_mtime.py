import os
import time

from semantic_backup_explorer.compare.folder_diff import compare_folders
from semantic_backup_explorer.indexer.scan_backup import scan_backup
from semantic_backup_explorer.utils.index_utils import get_all_files_from_index


def test_compare_folders_with_mtime(tmp_path):
    # Setup local folder
    local_dir = tmp_path / "local"
    local_dir.mkdir()
    file1 = local_dir / "file1.txt"
    file1.write_text("content1")

    # Setup backup folder
    backup_dir = tmp_path / "backup"
    backup_dir.mkdir()
    backup_file1 = backup_dir / "file1.txt"
    backup_file1.write_text("content1_old")

    # Set backup file mtime to be old
    old_time = time.time() - 100
    os.utime(backup_file1, (old_time, old_time))

    # Set local file mtime to be new
    new_time = time.time()
    os.utime(file1, (new_time, new_time))

    # Create index for backup
    index_file = tmp_path / "backup_index.md"
    scan_backup(backup_dir, index_file)

    # Get files from index
    backup_files = get_all_files_from_index(backup_dir, index_file)

    # Compare
    diff = compare_folders(local_dir, backup_files)

    assert "file1.txt" in diff["only_local"]
    assert "file1.txt" not in diff["in_both"]


def test_compare_folders_equal_mtime(tmp_path):
    # Setup local folder
    local_dir = tmp_path / "local"
    local_dir.mkdir()
    file1 = local_dir / "file1.txt"
    file1.write_text("content1")

    # Setup backup folder
    backup_dir = tmp_path / "backup"
    backup_dir.mkdir()
    backup_file1 = backup_dir / "file1.txt"
    backup_file1.write_text("content1")

    # Set same mtime
    now = time.time()
    os.utime(file1, (now, now))
    os.utime(backup_file1, (now, now))

    # Create index for backup
    index_file = tmp_path / "backup_index.md"
    scan_backup(backup_dir, index_file)

    # Get files from index
    backup_files = get_all_files_from_index(backup_dir, index_file)

    # Compare
    diff = compare_folders(local_dir, backup_files)

    assert "file1.txt" not in diff["only_local"]
    assert "file1.txt" in diff["in_both"]
