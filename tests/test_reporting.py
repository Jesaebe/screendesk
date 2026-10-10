import json
import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "backup"))

from src.reporting import RunReport, write_latest


class ReportingTests(unittest.TestCase):
    def test_writes_complete_latest_report(self):
        report = RunReport(
            run_id="run-1",
            source="main",
            started_at="2026-10-09T02:00:00+00:00",
            finished_at="2026-10-09T02:01:00+00:00",
            duration_seconds=60.0,
            status="success",
            size_bytes=1024,
            local_destination="/backups/main.dump",
            cloud_destination="gdrive-crypt:main.dump",
            error="",
            log_file="/backups/logs/run-1.log",
        )
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "status" / "latest.json"
            write_latest(report, destination)
            payload = json.loads(destination.read_text(encoding="utf-8"))
        self.assertEqual(payload["run_id"], "run-1")
        self.assertEqual(payload["status"], "success")
        self.assertFalse(destination.with_suffix(".json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
