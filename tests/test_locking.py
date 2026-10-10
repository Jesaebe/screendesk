import os
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "backup"))

from src.executor import diagnose_lock


class LockDiagnosisTests(unittest.TestCase):
    def test_missing_lock_is_not_stale(self):
        with tempfile.TemporaryDirectory() as directory:
            diagnosis = diagnose_lock(Path(directory) / "missing.lock")
        self.assertFalse(diagnosis.exists)
        self.assertFalse(diagnosis.stale_candidate)

    def test_old_lock_with_dead_process_is_stale_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            lock = Path(directory) / "maker.lock"
            lock.write_text("pid=999999\ncreated_unix=1\n")
            os.utime(lock, (1, 1))
            with patch("src.executor.os.kill", side_effect=ProcessLookupError):
                diagnosis = diagnose_lock(lock, now=21602, stale_after=21600)
        self.assertFalse(diagnosis.process_alive)
        self.assertTrue(diagnosis.stale_candidate)

    def test_malformed_lock_is_not_automatically_stale(self):
        with tempfile.TemporaryDirectory() as directory:
            lock = Path(directory) / "maker.lock"
            lock.write_text("unknown")
            os.utime(lock, (1, 1))
            diagnosis = diagnose_lock(lock, now=999999)
        self.assertIsNone(diagnosis.pid)
        self.assertFalse(diagnosis.stale_candidate)


if __name__ == "__main__":
    unittest.main()
