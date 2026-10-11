"""Production entrypoint for the backup scheduler and its healthcheck."""

import os
from pathlib import Path
import sys

from .config import load_sources
from .executor import SubprocessRunner
from .notifications import FailureNotifier, NotificationError, SMTPNotifier, SMTPSettings
from .pipeline import run_pipeline
from .scheduler import BackupScheduler


class DisabledNotifier:
    """Make an unconfigured notification channel visible in scheduler state."""

    def notify(self, report) -> None:
        raise NotificationError("SMTP notification is not configured")


def _positive_integer(name: str, default: int) -> int:
    raw = os.environ.get(name, str(default))
    try:
        value = int(raw)
    except ValueError as error:
        raise ValueError(f"{name} must be an integer") from error
    if value < 1:
        raise ValueError(f"{name} must be positive")
    return value


def _retention_watermarks() -> tuple[int, int]:
    high = _positive_integer("BACKUP_LOCAL_HIGH_WATERMARK", 85)
    low = _positive_integer("BACKUP_LOCAL_LOW_WATERMARK", 75)
    if high > 100 or low >= high:
        raise ValueError(
            "BACKUP_LOCAL_LOW_WATERMARK must be lower than "
            "BACKUP_LOCAL_HIGH_WATERMARK, which cannot exceed 100"
        )
    return high, low


def _notifier_from_environment() -> FailureNotifier:
    host = os.environ.get("SMTP_HOST", "").strip()
    sender = os.environ.get("ALERT_EMAIL_FROM", "").strip()
    recipient = os.environ.get("ALERT_EMAIL_TO", "").strip()
    if not host or not sender or not recipient:
        return DisabledNotifier()
    return SMTPNotifier(
        SMTPSettings(
            host=host,
            port=_positive_integer("SMTP_PORT", 587),
            username=os.environ.get("SMTP_USERNAME", ""),
            password=os.environ.get("SMTP_PASSWORD", ""),
            sender=sender,
            recipient=recipient,
        )
    )


def healthcheck() -> int:
    root = Path(os.environ.get("BACKUP_ROOT", "/backups"))
    status = Path("/status")
    return 0 if root.is_dir() and status.is_dir() else 1


def scheduler() -> int:
    backup_root = Path(os.environ.get("BACKUP_ROOT", "/backups"))
    status_root = Path(os.environ.get("BACKUP_STATUS_ROOT", "/status"))
    config_path = Path(os.environ.get("BACKUP_CONFIG", "/run/secrets/sources.toml"))
    rclone_config = Path(os.environ.get("RCLONE_CONFIG", "/run/secrets/rclone.conf"))
    rclone_remote = os.environ.get("RCLONE_CRYPT_REMOTE", "gdrive-crypt:screendeck-home")
    retention_days = _positive_integer("BACKUP_CLOUD_RETENTION_DAYS", 15)
    interval_seconds = _positive_integer("BACKUP_SCHEDULER_INTERVAL_SECONDS", 30)
    high_watermark, low_watermark = _retention_watermarks()

    sources = load_sources(config_path)
    runner = SubprocessRunner()

    def pipeline(source, password, started_at):
        return run_pipeline(
            source=source,
            password=password,
            backup_root=backup_root,
            status_root=status_root,
            rclone_remote=rclone_remote,
            rclone_config=rclone_config,
            retention_days=retention_days,
            runner=runner,
            started_at=started_at,
            high_watermark=high_watermark,
            low_watermark=low_watermark,
        )

    service = BackupScheduler(
        sources=sources,
        pipeline=pipeline,
        status_root=status_root,
        notifier=_notifier_from_environment(),
    )
    service.run_forever(interval_seconds=interval_seconds)
    return 0


def main(arguments: list[str]) -> int:
    command = arguments[1] if len(arguments) > 1 else "scheduler"
    if command == "healthcheck":
        return healthcheck()
    if command == "scheduler":
        try:
            return scheduler()
        except (OSError, ValueError) as error:
            print(f"configuration error: {error}", file=sys.stderr)
            return 1
        except KeyboardInterrupt:
            return 0
    print(f"unknown command: {command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
