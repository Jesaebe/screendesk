from dataclasses import replace
import os
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "backup"))

from src.config import load_sources
from src.storage import (
    DiskUsage,
    InsufficientSpaceError,
    MIB,
    managed_backup_files,
    prepare_storage,
    required_space,
)


def sparse_file(path: Path, size: int, timestamp: int):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as stream:
        stream.truncate(size)
    os.utime(path, (timestamp, timestamp))


class StorageTests(unittest.TestCase):
    def test_ignores_filesystem_and_inaccessible_directories(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lost_found = root / "lost+found"
            lost_found.mkdir()
            (lost_found / "filesystem-metadata").write_text("not a backup")
            inaccessible = root / "unrelated"
            inaccessible.mkdir()
            with patch.object(Path, "iterdir", autospec=True) as iterdir:
                def list_directory(path):
                    if path == root:
                        return iter([lost_found, inaccessible])
                    if path == inaccessible:
                        raise PermissionError("simulated")
                    return iter([])

                iterdir.side_effect = list_directory
                self.assertEqual(managed_backup_files(root), [])

    @classmethod
    def setUpClass(cls):
        cls.maker = load_sources(ROOT / "backup/config/sources.example.toml")[0]

    def test_reserves_twice_estimate_with_minimum_margin(self):
        self.assertEqual(required_space(self.maker), 64 * MIB)
        large = replace(self.maker, estimated_size_mb=100)
        self.assertEqual(required_space(large), 200 * MIB)

    def test_retention_cleans_to_low_watermark_and_preserves_newest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sparse_file(root / "a/a-old.dump", 30 * MIB, 1)
            sparse_file(root / "b/b-old.dump", 30 * MIB, 2)
            sparse_file(root / "a/a-new.dump", 30 * MIB, 3)
            sparse_file(root / "b/b-new.dump", 30 * MIB, 4)
            usage = lambda _: DiskUsage(400 * MIB, 360 * MIB, 40 * MIB)
            result = prepare_storage(root, self.maker, usage_provider=usage)
            self.assertEqual(len(result.deleted), 2)
            self.assertFalse((root / "a/a-old.dump").exists())
            self.assertFalse((root / "b/b-old.dump").exists())
            self.assertTrue((root / "a/a-new.dump").exists())
            self.assertTrue((root / "b/b-new.dump").exists())

    def test_fails_when_safe_margin_cannot_be_recovered(self):
        with tempfile.TemporaryDirectory() as directory:
            usage = lambda _: DiskUsage(100 * MIB, 95 * MIB, 5 * MIB)
            with self.assertRaises(InsufficientSpaceError):
                prepare_storage(Path(directory), self.maker, usage_provider=usage)

    def test_refuses_dump_if_protected_latest_prevents_low_watermark(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sparse_file(root / "maker/latest.dump", 10 * MIB, 1)
            usage = lambda _: DiskUsage(1000 * MIB, 900 * MIB, 100 * MIB)
            with self.assertRaisesRegex(InsufficientSpaceError, "low watermark"):
                prepare_storage(root, self.maker, usage_provider=usage)


if __name__ == "__main__":
    unittest.main()
