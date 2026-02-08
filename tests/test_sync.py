import unittest
import os
import shutil
from pathlib import Path
from src.compare.folder_diff import compare_folders
from src.sync.sync_missing import sync_files

class TestSyncCompare(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("tests/sync_test")
        self.local_dir = self.test_dir / "local"
        self.backup_dir = self.test_dir / "backup"

        self.local_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Create some files
        (self.local_dir / "file1.txt").write_text("content1")
        (self.local_dir / "file2.txt").write_text("content2")
        (self.backup_dir / "file1.txt").write_text("content1")
        (self.backup_dir / "file3.txt").write_text("content3")

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_compare(self):
        # We simulate that the backup folder has file1.txt and file3.txt
        backup_files_list = ["file1.txt", "file3.txt"]
        diff = compare_folders(self.local_dir, backup_files_list)

        self.assertIn("file2.txt", diff["only_local"])
        self.assertIn("file3.txt", diff["only_backup"])
        self.assertIn("file1.txt", diff["in_both"])

    def test_sync(self):
        files_to_sync = ["file2.txt"]
        synced, errors = sync_files(files_to_sync, self.local_dir, self.backup_dir)

        self.assertEqual(len(synced), 1)
        self.assertEqual(synced[0], "file2.txt")
        self.assertTrue((self.backup_dir / "file2.txt").exists())

if __name__ == "__main__":
    unittest.main()
