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
from src.reporting import RunReport
from src.scheduler import BackupScheduler


class RecordingNotifier:
    def __init__(self):
        self.reports = []

    def notify(self, report):
        self.reports.append(report)


class ExplodingNotifier:
    def notify(self, report):
        raise RuntimeError("smtp-secret must never be persisted")


class RecordingPipeline:
    def __init__(self, status="success"):
        self.status = status
        self.calls = []

    def __call__(self, source, password, instant):
        self.calls.append((source, password, instant))
        timestamp = instant.astimezone(timezone.utc).isoformat()
        return RunReport(
            run_id="maker-scheduled",
            source=source.identifier,
            started_at=timestamp,
            finished_at=timestamp,
            duration_seconds=0,
            status=self.status,
            size_bytes=1 if self.status == "success" else 0,
            local_destination="/backups/maker.dump" if self.status == "success" else "",
            cloud_destination="gdrive-crypt:maker.dump" if self.status == "success" else "",
            error="" if self.status == "success" else "simulated failure",
            log_file="/backups/maker.log",
        )


class ExplodingPipeline:
    def __call__(self, source, password, instant):
        raise RuntimeError(f"connection rejected {password}")


class SchedulerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        maker = load_sources(ROOT / "backup/config/sources.example.toml")[0]
        cls.maker = replace(maker, enabled=True, username="backup_reader")
        cls.due = datetime(2026, 10, 9, 9, 0, tzinfo=timezone.utc)

    def test_runs_due_source_once_per_local_minute(self):
        pipeline = RecordingPipeline()
        notifier = RecordingNotifier()
        with tempfile.TemporaryDirectory() as directory:
            password_file = Path(directory) / "password"
            password_file.write_text("secret\n")
            maker = replace(self.maker, password_file=str(password_file))
            scheduler = BackupScheduler(
                [maker], pipeline, Path(directory), notifier
            )
            first = scheduler.run_due(self.due)
            second = scheduler.run_due(self.due)
        self.assertEqual(len(first), 1)
        self.assertEqual(second, [])
        self.assertEqual(len(pipeline.calls), 1)
        self.assertEqual(notifier.reports, [])

    def test_deduplication_survives_scheduler_restart(self):
        first_pipeline = RecordingPipeline()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            password_file = root / "password"
            password_file.write_text("secret")
            maker = replace(self.maker, password_file=str(password_file))
            first = BackupScheduler(
                [maker],
                first_pipeline,
                root,
                RecordingNotifier(),
            )
            first.run_due(self.due)
            second_pipeline = RecordingPipeline()
            restarted = BackupScheduler(
                [maker],
                second_pipeline,
                root,
                RecordingNotifier(),
            )
            result = restarted.run_due(self.due)
        self.assertEqual(result, [])
        self.assertEqual(second_pipeline.calls, [])

    def test_persisted_state_is_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scheduler = BackupScheduler(
                [self.maker], RecordingPipeline(), root, RecordingNotifier()
            )
            scheduler._completed_slots = {
                ("maker", f"2026-10-{index // 1440 + 1:02d}T{(index // 60) % 24:02d}:{index % 60:02d}")
                for index in range(600)
            }
            scheduler._save_slots()
            payload = json.loads((root / "scheduler-state.json").read_text())
        self.assertEqual(len(payload["completed_slots"]), 512)

    def test_missing_password_reports_and_notifies_without_pipeline(self):
        pipeline = RecordingPipeline()
        notifier = RecordingNotifier()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scheduler = BackupScheduler([self.maker], pipeline, root, notifier)
            result = scheduler.run_due(self.due)[0]
            latest = json.loads((root / "latest.json").read_text())
        self.assertEqual(result.report.status, "configuration_failed")
        self.assertEqual(latest["status"], "configuration_failed")
        self.assertEqual(pipeline.calls, [])
        self.assertEqual(len(notifier.reports), 1)

    def test_pipeline_failure_is_notified(self):
        notifier = RecordingNotifier()
        with tempfile.TemporaryDirectory() as directory:
            password_file = Path(directory) / "password"
            password_file.write_text("secret")
            scheduler = BackupScheduler(
                [replace(self.maker, password_file=str(password_file))],
                RecordingPipeline("cloud_failed"),
                Path(directory),
                notifier,
            )
            scheduler.run_due(self.due)
        self.assertEqual(notifier.reports[0].status, "cloud_failed")

    def test_unexpected_error_is_sanitized_and_notified(self):
        notifier = RecordingNotifier()
        with tempfile.TemporaryDirectory() as directory:
            password_file = Path(directory) / "password"
            password_file.write_text("secret")
            scheduler = BackupScheduler(
                [replace(self.maker, password_file=str(password_file))],
                ExplodingPipeline(),
                Path(directory),
                notifier,
            )
            report = scheduler.run_due(self.due)[0].report
        self.assertEqual(report.status, "internal_failed")
        self.assertNotIn("secret", report.error)
        self.assertIn("[REDACTED]", report.error)

    def test_notification_failure_is_recorded_without_raising(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            password_file = root / "password"
            password_file.write_text("secret")
            scheduler = BackupScheduler(
                [replace(self.maker, password_file=str(password_file))],
                RecordingPipeline("cloud_failed"),
                root,
                ExplodingNotifier(),
            )
            result = scheduler.run_due(self.due)
            notification = json.loads((root / "notification-status.json").read_text())
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].report.status, "cloud_failed")
        self.assertEqual(notification["status"], "failed")
        self.assertNotIn("smtp-secret", json.dumps(notification))


if __name__ == "__main__":
    unittest.main()
