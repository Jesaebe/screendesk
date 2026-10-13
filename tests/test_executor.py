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
from src.executor import BackupBusyError, CommandResult, execute_backup


class FakeRunner:
    def __init__(self, returncode=0, content=b"logical backup", stderr=""):
        self.returncode = returncode
        self.content = content
        self.stderr = stderr
        self.calls = []

    def run(self, argv, environment):
        self.calls.append((argv, environment))
        if self.returncode == 0:
            option = "--file" if "--file" in argv else "--result-file"
            destination = Path(argv[argv.index(option) + 1])
            destination.write_bytes(self.content)
        return CommandResult(self.returncode, "", self.stderr)


class ExecutorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        maker = load_sources(ROOT / "backup/config/sources.example.toml")[0]
        cls.enabled_maker = replace(maker, enabled=True, username="backup_reader")

    def test_success_promotes_partial_and_writes_reports(self):
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = execute_backup(
                self.enabled_maker,
                "test-password",
                root / "backups",
                root / "status",
                runner,
                datetime(2026, 10, 9, 3, 0, tzinfo=timezone.utc),
            )
            self.assertEqual(report.status, "success")
            self.assertEqual(report.size_bytes, len(b"logical backup"))
            self.assertTrue(Path(report.local_destination).is_file())
            self.assertEqual(list((root / "backups/.incoming").iterdir()), [])
            latest = json.loads((root / "status/latest.json").read_text())
            history = (root / "status/history.jsonl").read_text().splitlines()
            self.assertEqual(latest["run_id"], report.run_id)
            self.assertEqual(len(history), 1)
            argv, environment = runner.calls[0]
            self.assertNotIn("test-password", argv)
            self.assertEqual(environment["PGPASSWORD"], "test-password")
            self.assertEqual(environment["PGSSLMODE"], "disable")

    def test_failure_removes_partial_and_redacts_log(self):
        runner = FakeRunner(returncode=2, stderr="authentication test-password failed")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = execute_backup(
                self.enabled_maker,
                "test-password",
                root / "backups",
                root / "status",
                runner,
            )
            self.assertEqual(report.status, "failed")
            self.assertEqual(report.local_destination, "")
            self.assertEqual(list((root / "backups/.incoming").iterdir()), [])
            log = Path(report.log_file).read_text()
            self.assertNotIn("test-password", log)
            self.assertIn("[REDACTED]", log)
            self.assertEqual(report.error, "dump command exited with code 2")

    def test_failure_report_uses_sanitized_dump_detail(self):
        runner = FakeRunner(
            returncode=1,
            stderr="pg_dump: error: permission denied for table invoices test-password\n",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = execute_backup(
                self.enabled_maker,
                "test-password",
                root / "backups",
                root / "status",
                runner,
            )
        self.assertEqual(
            report.error,
            "pg_dump: error: permission denied for table invoices [REDACTED]",
        )
        self.assertNotIn("test-password", report.error)

    def test_existing_lock_prevents_runner_call(self):
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lock = root / "backups/.locks/maker.lock"
            lock.parent.mkdir(parents=True)
            lock.write_text("existing")
            with self.assertRaises(BackupBusyError):
                execute_backup(
                    self.enabled_maker,
                    "test-password",
                    root / "backups",
                    root / "status",
                    runner,
                )
            self.assertEqual(runner.calls, [])

    def test_disabled_source_is_rejected(self):
        disabled = replace(self.enabled_maker, enabled=False)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                execute_backup(disabled, "test-password", Path(directory), Path(directory), FakeRunner())


if __name__ == "__main__":
    unittest.main()
