import datetime
import unittest
from pathlib import Path

from semantic_backup_explorer.utils.index_utils import get_index_metadata


class TestIndexMetadata(unittest.TestCase):
    def setUp(self):
        self.test_index = Path("test_index.md")

    def tearDown(self):
        if self.test_index.exists():
            self.test_index.unlink()

    def test_get_index_metadata_basic(self):
        content = "# Backup Index\n\nRoot: J:\\data\n\n## J:\\data\n"
        self.test_index.write_text(content, encoding="utf-8")

        metadata = get_index_metadata(self.test_index)
        self.assertEqual(metadata.root_path, Path("J:\\data"))
        self.assertIsNone(metadata.label)
        self.assertIsInstance(metadata.mtime, datetime.datetime)

    def test_get_index_metadata_with_label(self):
        content = "# Backup Index\n\nRoot: J:\\data (Label: MyDrive)\n\n## J:\\data\n"
        self.test_index.write_text(content, encoding="utf-8")

        metadata = get_index_metadata(self.test_index)
        self.assertEqual(metadata.root_path, Path("J:\\data"))
        self.assertEqual(metadata.label, "MyDrive")

    def test_get_index_metadata_missing_file(self):
        metadata = get_index_metadata("non_existent.md")
        self.assertIsNone(metadata.root_path)
        self.assertEqual(metadata.age_days, 0)


if __name__ == "__main__":
    unittest.main()
