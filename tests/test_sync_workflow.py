"""Integration tests for the full backup and sync workflow."""

import os
import time

from semantic_backup_explorer.compare.folder_diff import compare_folders
from semantic_backup_explorer.indexer.scan_backup import scan_backup
from semantic_backup_explorer.sync.sync_missing import sync_files
from semantic_backup_explorer.utils.index_utils import get_all_files_from_index


class TestBackupWorkflow:
    def test_full_sync_cycle(self, tmp_path):
        # 1. Setup mock backup and local environments
        backup_dir = tmp_path / "backup"
        backup_dir.mkdir()
        local_dir = tmp_path / "local"
        local_dir.mkdir()

        # Initial local files
        file1_local = local_dir / "file1.txt"
        file1_local.write_text("content1")
        (local_dir / "subdir").mkdir()
        (local_dir / "subdir" / "file2.txt").write_text("content2")

        # 2. Initial Backup (simulate initial sync)
        (backup_dir / "my_stuff").mkdir()
        file1_backup = backup_dir / "my_stuff" / "file1.txt"
        file1_backup.write_text("content1")
        (backup_dir / "my_stuff" / "subdir").mkdir()
        (backup_dir / "my_stuff" / "subdir" / "file2.txt").write_text("content2")

        # Ensure backup mtime is older than what we will set for local later
        old_time = time.time() - 10
        os.utime(file1_backup, (old_time, old_time))

        # 3. Create Index
        index_file = tmp_path / "index.md"
        scan_backup(backup_dir, index_file)
        assert index_file.exists()

        # 4. Modify Local
        (local_dir / "file3.txt").write_text("content3")  # New file
        file1_local.write_text("content1 updated")  # Updated file
        # Ensure it has a significantly newer mtime
        new_time = time.time() + 10
        os.utime(file1_local, (new_time, new_time))

        # 5. Compare via Index
        backup_files = get_all_files_from_index(backup_dir / "my_stuff", index_file)
        diff = compare_folders(local_dir, backup_files)

        assert "file3.txt" in diff["only_local"]
        assert "file1.txt" in diff["only_local"]  # Should be here due to newer mtime

        # 6. Sync Missing
        synced, errors = sync_files(diff["only_local"], local_dir, backup_dir / "my_stuff")

        assert len(synced) == 2
        assert len(errors) == 0
        assert (backup_dir / "my_stuff" / "file3.txt").exists()
        assert (backup_dir / "my_stuff" / "file1.txt").read_text() == "content1 updated"
