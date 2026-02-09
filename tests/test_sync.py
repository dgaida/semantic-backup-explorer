import shutil
import unittest
from pathlib import Path

from semantic_backup_explorer.compare.folder_diff import compare_folders
from semantic_backup_explorer.sync.sync_missing import sync_files


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

    def test_sync_with_callback_and_error(self):
        files_to_sync = ["file2.txt", "non_existent.txt"]
        callback_results = []

        def callback(current, total, rel_path, error=None):
            callback_results.append((current, total, rel_path, error))

        synced, errors = sync_files(files_to_sync, self.local_dir, self.backup_dir, callback=callback)

        # file2.txt should succeed, non_existent.txt should fail
        self.assertEqual(len(synced), 1)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], "non_existent.txt")

        self.assertEqual(len(callback_results), 2)
        # First call: success
        self.assertEqual(callback_results[0][2], "file2.txt")
        self.assertIsNone(callback_results[0][3])
        # Second call: error
        self.assertEqual(callback_results[1][2], "non_existent.txt")
        self.assertIsNotNone(callback_results[1][3])
        self.assertTrue("does not exist" in callback_results[1][3].lower() or "no such file" in callback_results[1][3].lower())


if __name__ == "__main__":
    unittest.main()
