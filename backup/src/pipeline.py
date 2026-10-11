"""Transactional orchestration of local dump, cloud upload and cloud retention."""

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from .cloud import CloudError, CloudRunner, prune_cloud, upload_encrypted
from .dump import Source
from .executor import CommandRunner, RunReport, execute_backup
from .reporting import append_history, write_latest


def _finish(report: RunReport, status_root: Path) -> RunReport:
    write_latest(report, status_root / "latest.json")
    append_history(report, status_root / "history.jsonl")
    return report


def _final_fields(report: RunReport) -> dict[str, object]:
    finished = datetime.now(timezone.utc)
    started = datetime.fromisoformat(report.started_at)
    return {
        "finished_at": finished.isoformat(),
        "duration_seconds": max(0.0, (finished - started).total_seconds()),
    }


def run_pipeline(
    source: Source,
    password: str,
    backup_root: Path,
    status_root: Path,
    rclone_remote: str,
    rclone_config: Path,
    retention_days: int,
    runner: CommandRunner | CloudRunner,
    started_at: datetime | None = None,
    usage_provider=None,
    known_cloud_secrets: list[str] | None = None,
    high_watermark: int = 85,
    low_watermark: int = 75,
) -> RunReport:
    """Run all stages and publish exactly one final history record."""
    report = execute_backup(
        source,
        password,
        backup_root,
        status_root,
        runner,
        started_at=started_at,
        usage_provider=usage_provider,
        publish_report=False,
        high_watermark=high_watermark,
        low_watermark=low_watermark,
    )
    if report.status != "success":
        return _finish(report, status_root)

    local_file = Path(report.local_destination)
    try:
        uploaded = upload_encrypted(
            local_file,
            source.identifier,
            rclone_remote,
            rclone_config,
            runner,
            known_cloud_secrets,
        )
    except CloudError as error:
        failed = replace(
            report,
            **_final_fields(report),
            status="cloud_failed",
            error=str(error),
        )
        return _finish(failed, status_root)

    try:
        prune_cloud(
            source.identifier,
            rclone_remote,
            rclone_config,
            retention_days,
            runner,
            known_cloud_secrets,
        )
    except CloudError as error:
        failed = replace(
            report,
            **_final_fields(report),
            status="cloud_retention_failed",
            cloud_destination=uploaded.destination,
            error=str(error),
        )
        return _finish(failed, status_root)

    completed = replace(
        report,
        **_final_fields(report),
        cloud_destination=uploaded.destination,
        error="",
    )
    return _finish(completed, status_root)
