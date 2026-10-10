"""Structured and atomic backup status reporting."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RunReport:
    run_id: str
    source: str
    started_at: str
    finished_at: str
    duration_seconds: float
    status: str
    size_bytes: int
    local_destination: str
    cloud_destination: str
    error: str
    log_file: str
    restore_validated_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_latest(report: RunReport, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(destination)


def append_history(report: RunReport, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(report.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
