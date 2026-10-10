from dataclasses import replace
from datetime import datetime, timezone
import json
import sys
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "backup"))

from src.config import load_sources
from src.executor import CommandResult
from src.pipeline import run_pipeline


class PipelineRunner:
    def __init__(self, dump_code=0, upload_code=0, retention_code=0):
        self.dump_code = dump_code
        self.upload_code = upload_code
        self.retention_code = retention_code
        self.calls = []

    def run(self, argv, environment):
        self.calls.append((argv, environment))
        if argv[0] == "pg_dump":
            if self.dump_code == 0:
                destination = Path(argv[argv.index("--file") + 1])
                destination.write_bytes(b"maker logical dump")
            return CommandResult(self.dump_code, "", "dump failed" if self.dump_code else "")
        if argv[0:2] == ["rclone", "copyto"]:
            return CommandResult(self.upload_code, "", "upload failed" if self.upload_code else "")
        if argv[0:2] == ["rclone", "delete"]:
            return CommandResult(
                self.retention_code,
                "",
                "retention failed" if self.retention_code else "",
            )
        raise AssertionError(f"unexpected command: {argv}")


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        maker = load_sources(ROOT / "backup/config/sources.example.toml")[0]
        cls.maker = replace(maker, enabled=True, username="backup_reader")

    def run_in_temporary_directory(self, runner):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        report = run_pipeline(
            self.maker,
            "test-password",
            root / "backups",
            root / "status",
            "gdrive-crypt:screendeck-home",
            Path("/run/secrets/rclone.conf"),
            15,
            runner,
            started_at=datetime(2026, 10, 9, 3, 0, tzinfo=timezone.utc),
        )
        return temporary, root, report

    def test_success_runs_dump_upload_and_retention_once(self):
        runner = PipelineRunner()
        temporary, root, report = self.run_in_temporary_directory(runner)
        try:
            self.assertEqual(report.status, "success")
            self.assertGreaterEqual(report.duration_seconds, 0)
            self.assertTrue(Path(report.local_destination).is_file())
            self.assertEqual(
                report.cloud_destination,
                "gdrive-crypt:screendeck-home/maker/" + Path(report.local_destination).name,
            )
            self.assertEqual([call[0][0] for call in runner.calls], ["pg_dump", "rclone", "rclone"])
            history = (root / "status/history.jsonl").read_text().splitlines()
            self.assertEqual(len(history), 1)
            self.assertEqual(json.loads(history[0])["status"], "success")
        finally:
            temporary.cleanup()

    def test_local_failure_does_not_call_rclone(self):
        runner = PipelineRunner(dump_code=1)
        temporary, _, report = self.run_in_temporary_directory(runner)
        try:
            self.assertEqual(report.status, "failed")
            self.assertEqual(len(runner.calls), 1)
        finally:
            temporary.cleanup()

    def test_upload_failure_preserves_local_dump_and_skips_retention(self):
        runner = PipelineRunner(upload_code=1)
        temporary, root, report = self.run_in_temporary_directory(runner)
        try:
            self.assertEqual(report.status, "cloud_failed")
            self.assertTrue(Path(report.local_destination).is_file())
            self.assertEqual(len(runner.calls), 2)
            latest = json.loads((root / "status/latest.json").read_text())
            self.assertEqual(latest["status"], "cloud_failed")
        finally:
            temporary.cleanup()

    def test_retention_failure_records_uploaded_destination(self):
        runner = PipelineRunner(retention_code=1)
        temporary, _, report = self.run_in_temporary_directory(runner)
        try:
            self.assertEqual(report.status, "cloud_retention_failed")
            self.assertTrue(report.cloud_destination.startswith("gdrive-crypt:"))
            self.assertTrue(Path(report.local_destination).is_file())
            self.assertEqual(len(runner.calls), 3)
        finally:
            temporary.cleanup()


if __name__ == "__main__":
    unittest.main()
