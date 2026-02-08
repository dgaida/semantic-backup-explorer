import os
import unittest
from semantic_backup_explorer.utils.index_utils import find_backup_folder, get_all_files_from_index

class TestIndexUtils(unittest.TestCase):
    def setUp(self):
        self.test_index = "tests/test_index_temp.md"
        with open(self.test_index, 'w', encoding='utf-8') as f:
            f.write("## J:\\data\\Multimedia\\MP3 Archiv\n")
            f.write("- J:\\data\\Multimedia\\MP3 Archiv\\Artist1/\n")
            f.write("- J:\\data\\Multimedia\\MP3 Archiv\\song1.mp3\n")
            f.write("\n")
            f.write("## J:\\data\\Multimedia\\MP3 Archiv\\Artist1\n")
            f.write("- J:\\data\\Multimedia\\MP3 Archiv\\Artist1\\song2.mp3\n")
            f.write("\n")
            f.write("## J:\\data\\Other\n")
            f.write("- J:\\data\\Other\\file.txt\n")

    def tearDown(self):
        if os.path.exists(self.test_index):
            os.remove(self.test_index)

    def test_find_backup_folder(self):
        # Match by exact name at end
        folder = find_backup_folder("MP3 Archiv", self.test_index)
        self.assertEqual(folder, "J:\\data\\Multimedia\\MP3 Archiv")

        # Match subfolder
        folder = find_backup_folder("Artist1", self.test_index)
        self.assertEqual(folder, "J:\\data\\Multimedia\\MP3 Archiv\\Artist1")

        # No match
        folder = find_backup_folder("NonExistent", self.test_index)
        self.assertIsNone(folder)

    def test_get_all_files_from_index(self):
        backup_root = "J:\\data\\Multimedia\\MP3 Archiv"
        files = get_all_files_from_index(backup_root, self.test_index)

        # Normalize paths for comparison (all will be normalized to forward slash in normalize_path call in test comparison)
        norm_files = [f.replace('\\', '/') for f in files]

        self.assertIn("song1.mp3", norm_files)
        self.assertIn("Artist1/song2.mp3", norm_files)
        self.assertEqual(len(norm_files), 2)
        self.assertNotIn("Other/file.txt", norm_files)

if __name__ == "__main__":
    unittest.main()
