"""Safe orchestration of one logical dump without scheduling or cloud upload."""

from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import subprocess
import time
from typing import Callable, Protocol

from .dump import Source, build_dump_command, build_dump_environment
from .redaction import redact
from .reporting import RunReport, append_history, write_latest
from .storage import DiskUsage, prepare_storage


class BackupBusyError(RuntimeError):
    """Raised when another execution already holds the source lock."""


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


class CommandRunner(Protocol):
    def run(self, argv: list[str], environment: dict[str, str]) -> CommandResult: ...


class SubprocessRunner:
    """Production adapter. Tests inject a fake and never call subprocesses."""

    def run(self, argv: list[str], environment: dict[str, str]) -> CommandResult:
        completed = subprocess.run(
            argv,
            check=False,
            capture_output=True,
            text=True,
            env={**os.environ, **environment},
        )
        return CommandResult(completed.returncode, completed.stdout, completed.stderr)


class SourceLock:
    def __init__(self, path: Path):
        self.path = path
        self._descriptor: int | None = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as error:
            raise BackupBusyError(f"backup already running for {self.path.stem}") from error
        os.write(
            self._descriptor,
            f"pid={os.getpid()}\ncreated_unix={int(time.time())}\n".encode(),
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._descriptor is not None:
            os.close(self._descriptor)
        self.path.unlink(missing_ok=True)


@dataclass(frozen=True)
class LockDiagnosis:
    exists: bool
    pid: int | None
    age_seconds: float | None
    process_alive: bool | None
    stale_candidate: bool


def diagnose_lock(path: Path, now: float | None = None, stale_after: int = 21600) -> LockDiagnosis:
    """Classify a lock without deleting it or sending signals."""
    if not path.exists():
        return LockDiagnosis(False, None, None, None, False)
    values: dict[str, str] = {}
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            key, value = line.split("=", 1)
            values[key] = value
        pid = int(values["pid"])
    except (OSError, ValueError, KeyError):
        pid = None
    current_time = time.time() if now is None else now
    age = max(0.0, current_time - path.stat().st_mtime)
    alive: bool | None = None
    if pid is not None:
        try:
            os.kill(pid, 0)
            alive = True
        except ProcessLookupError:
            alive = False
        except PermissionError:
            alive = True
    stale = age >= stale_after and alive is False
    return LockDiagnosis(True, pid, age, alive, stale)


def _timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def execute_backup(
    source: Source,
    password: str,
    backup_root: Path,
    status_root: Path,
    runner: CommandRunner,
    started_at: datetime | None = None,
    usage_provider: Callable[[Path], DiskUsage] | None = None,
    publish_report: bool = True,
) -> RunReport:
    """Execute one local dump and always publish a sanitized report.

    This function deliberately does not upload, apply retention, or send e-mail.
    Those steps are separate so a failed downstream operation cannot corrupt a
    successfully completed local dump.
    """
    if not source.enabled:
        raise ValueError(f"source {source.identifier} is disabled")
    if not password:
        raise ValueError(f"password is missing for {source.identifier}")

    started = started_at or datetime.now(timezone.utc)
    run_id = f"{source.identifier}-{_timestamp(started)}"
    source_root = backup_root / source.identifier
    incoming_root = backup_root / ".incoming"
    log_root = backup_root / "logs" / source.identifier
    lock_path = backup_root / ".locks" / f"{source.identifier}.lock"
    suffix = ".dump" if source.engine == "postgresql" else ".sql"
    partial = incoming_root / f"{run_id}{suffix}.partial"
    final = source_root / f"{run_id}{suffix}"
    log_path = log_root / f"{run_id}.log"
    status_path = status_root / "latest.json"
    history_path = status_root / "history.jsonl"

    incoming_root.mkdir(parents=True, exist_ok=True)
    source_root.mkdir(parents=True, exist_ok=True)
    log_root.mkdir(parents=True, exist_ok=True)

    status = "failed"
    error_message = ""
    size_bytes = 0
    with SourceLock(lock_path):
        try:
            storage = prepare_storage(
                backup_root,
                source,
                usage_provider=usage_provider or shutil.disk_usage,
            )
            command = build_dump_command(source, str(partial))
            environment = build_dump_environment(source, password)
            result = runner.run(command, environment)
            retention_note = ""
            if storage.deleted:
                retention_note = "retention_deleted=" + ",".join(storage.deleted) + "\n"
            sanitized_output = retention_note + redact(result.stdout + result.stderr, [password])
            log_path.write_text(sanitized_output, encoding="utf-8")
            if result.returncode != 0:
                raise RuntimeError(f"dump command exited with code {result.returncode}")
            if not partial.is_file() or partial.stat().st_size <= 0:
                raise RuntimeError("dump command did not produce a non-empty file")
            partial.replace(final)
            size_bytes = final.stat().st_size
            status = "success"
        except Exception as error:
            partial.unlink(missing_ok=True)
            error_message = redact(str(error), [password])
            if not log_path.exists():
                log_path.write_text(error_message + "\n", encoding="utf-8")

        finished = datetime.now(timezone.utc)
        report = RunReport(
            run_id=run_id,
            source=source.identifier,
            started_at=started.astimezone(timezone.utc).isoformat(),
            finished_at=finished.isoformat(),
            duration_seconds=max(0.0, (finished - started).total_seconds()),
            status=status,
            size_bytes=size_bytes,
            local_destination=str(final) if status == "success" else "",
            cloud_destination="",
            error=error_message,
            log_file=str(log_path),
        )
        if publish_report:
            write_latest(report, status_path)
            append_history(report, history_path)
        return report
