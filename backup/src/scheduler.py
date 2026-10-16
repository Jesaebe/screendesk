"""Testable scheduling loop; it does not start automatically in phase one."""

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Callable
from zoneinfo import ZoneInfo

from .dump import Source
from .notifications import FailureNotifier
from .reporting import RunReport, append_history, write_latest
from .redaction import redact
from .schedule import is_due


Pipeline = Callable[[Source, str, datetime], RunReport]
SourceLoader = Callable[[], list[Source]]


@dataclass(frozen=True)
class ScheduledResult:
    source: str
    slot: str
    report: RunReport


class BackupScheduler:
    def __init__(
        self,
        sources: list[Source],
        pipeline: Pipeline,
        status_root: Path,
        notifier: FailureNotifier,
        source_loader: SourceLoader | None = None,
        now: Callable[[], datetime] | None = None,
    ):
        self.sources = sources
        self.pipeline = pipeline
        self.status_root = status_root
        self.notifier = notifier
        self.source_loader = source_loader
        self._now = now or (lambda: datetime.now(timezone.utc))
        self._state_path = status_root / "scheduler-state.json"
        self._notification_path = status_root / "notification-status.json"
        self._service_status_path = status_root / "service-status.json"
        self._active_path = status_root / "active-backup.json"
        self._active_path.unlink(missing_ok=True)
        self._completed_slots = self._load_slots()

    def _load_slots(self) -> set[tuple[str, str]]:
        try:
            payload = json.loads(self._state_path.read_text(encoding="utf-8"))
            return {
                (str(item["source"]), str(item["slot"]))
                for item in payload.get("completed_slots", [])
            }
        except (OSError, ValueError, TypeError, KeyError):
            return set()

    @staticmethod
    def _write_json_atomic(path: Path, payload: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)

    def _save_slots(self) -> None:
        bounded = sorted(self._completed_slots, key=lambda item: (item[1], item[0]))[-512:]
        self._completed_slots = set(bounded)
        self._write_json_atomic(
            self._state_path,
            {"completed_slots": [{"source": source, "slot": slot} for source, slot in bounded]},
        )

    def _notify_safely(self, report: RunReport, instant: datetime) -> None:
        try:
            self.notifier.notify(report)
            payload = {
                "run_id": report.run_id,
                "status": "sent",
                "updated_at": instant.astimezone(timezone.utc).isoformat(),
                "error": "",
            }
        except Exception as error:
            payload = {
                "run_id": report.run_id,
                "status": "failed",
                "updated_at": instant.astimezone(timezone.utc).isoformat(),
                "error": f"notification channel failed ({type(error).__name__})",
            }
        self._write_json_atomic(self._notification_path, payload)

    @staticmethod
    def slot(source: Source, instant: datetime) -> str:
        local = instant.astimezone(ZoneInfo(source.timezone))
        return local.strftime("%Y-%m-%dT%H:%M")

    def _failure_report(
        self,
        source: Source,
        instant: datetime,
        error: str,
        status: str,
    ) -> RunReport:
        slot = self.slot(source, instant)
        report = RunReport(
            run_id=f"{source.identifier}-{slot.replace(':', '').replace('-', '')}-config",
            source=source.identifier,
            started_at=instant.astimezone(timezone.utc).isoformat(),
            finished_at=instant.astimezone(timezone.utc).isoformat(),
            duration_seconds=0,
            status=status,
            size_bytes=0,
            local_destination="",
            cloud_destination="",
            error=error,
            log_file="",
        )
        write_latest(report, self.status_root / "latest.json")
        append_history(report, self.status_root / "history.jsonl")
        return report

    def run_due(self, instant: datetime | None = None) -> list[ScheduledResult]:
        if self.source_loader is not None:
            try:
                self.sources = self.source_loader()
            except (OSError, ValueError) as error:
                print(f"backup source reload failed: {type(error).__name__}", flush=True)
        current = instant or datetime.now(timezone.utc)
        results: list[ScheduledResult] = []
        for source in self.sources:
            if not is_due(source, current):
                continue
            slot = self.slot(source, current)
            slot_key = (source.identifier, slot)
            if slot_key in self._completed_slots:
                continue
            self._completed_slots.add(slot_key)
            self._save_slots()
            try:
                password = Path(source.password_file).read_text(encoding="utf-8").rstrip("\r\n")
            except OSError:
                password = ""
            if not password:
                report = self._failure_report(
                    source,
                    current,
                    f"required password file is missing or empty: {source.password_file}",
                    "configuration_failed",
                )
            else:
                # ``current`` identifies the scheduled minute and is shared by every
                # source due in this pass.  Duration, however, must start when this
                # particular source actually begins (after any previous source).
                execution_started = self._now()
                self._write_json_atomic(
                    self._active_path,
                    {
                        "status": "running",
                        "source": source.identifier,
                        "display_name": source.display_name,
                        "started_at": execution_started.astimezone(timezone.utc).isoformat(),
                    },
                )
                try:
                    try:
                        report = self.pipeline(source, password, execution_started)
                    except Exception as error:
                        report = self._failure_report(
                            source,
                            current,
                            redact(f"pipeline raised an unexpected error: {error}", [password]),
                            "internal_failed",
                        )
                finally:
                    self._active_path.unlink(missing_ok=True)
            if report.status != "success":
                self._notify_safely(report, current)
            results.append(ScheduledResult(source.identifier, slot, report))
        return results

    def run_forever(
        self,
        interval_seconds: int = 30,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if interval_seconds < 1:
            raise ValueError("scheduler interval must be positive")
        while True:
            self.run_due()
            self._write_json_atomic(
                self._service_status_path,
                {"status": "running", "updated_at": datetime.now(timezone.utc).isoformat()},
            )
            sleep(interval_seconds)
