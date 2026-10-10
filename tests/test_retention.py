import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "backup"))

from src.retention import BackupFile, select_local_deletions


class RetentionTests(unittest.TestCase):
    def setUp(self):
        self.files = [
            BackupFile("a-old", "a", 10, 1),
            BackupFile("b-old", "b", 10, 2),
            BackupFile("a-new", "a", 10, 3),
            BackupFile("b-new", "b", 10, 4),
        ]

    def test_does_nothing_below_high_watermark(self):
        self.assertEqual(select_local_deletions(self.files, 84, 100), [])

    def test_removes_oldest_and_preserves_latest_per_source(self):
        selected = select_local_deletions(self.files, 95, 100)
        self.assertEqual([item.path for item in selected], ["a-old", "b-old"])
        self.assertNotIn("a-new", [item.path for item in selected])
        self.assertNotIn("b-new", [item.path for item in selected])

    def test_rejects_invalid_watermarks(self):
        with self.assertRaises(ValueError):
            select_local_deletions(self.files, 90, 100, 75, 85)


if __name__ == "__main__":
    unittest.main()
