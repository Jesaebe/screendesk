"""Disk preflight and bounded local-retention operations."""

from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Callable, NamedTuple

from .dump import Source
from .retention import BackupFile, select_local_deletions


MIB = 1024 * 1024


class DiskUsage(NamedTuple):
    total: int
    used: int
    free: int


class InsufficientSpaceError(RuntimeError):
    pass


@dataclass(frozen=True)
class StorageResult:
    required_bytes: int
    projected_free_bytes: int
    deleted: tuple[str, ...]


def required_space(source: Source) -> int:
    """Reserve twice the estimate, with a 64 MiB minimum working margin."""
    estimate = max(0, source.estimated_size_mb) * MIB
    return max(64 * MIB, estimate * 2)


def managed_backup_files(root: Path) -> list[BackupFile]:
    files: list[BackupFile] = []
    if not root.is_dir():
        return files
    for source_directory in root.iterdir():
        if not source_directory.is_dir() or source_directory.name.startswith("."):
            continue
        if source_directory.name in {"logs", "lost+found"}:
            continue
        try:
            candidates = source_directory.iterdir()
            candidates = list(candidates)
        except OSError:
            continue
        for candidate in candidates:
            if candidate.is_file() and not candidate.name.endswith(".partial"):
                metadata = candidate.stat()
                files.append(
                    BackupFile(
                        path=str(candidate),
                        source=source_directory.name,
                        size_bytes=metadata.st_size,
                        modified_at=metadata.st_mtime,
                    )
                )
    return files


def prepare_storage(
    root: Path,
    source: Source,
    high_watermark: int = 85,
    low_watermark: int = 75,
    usage_provider: Callable[[Path], DiskUsage] = shutil.disk_usage,
) -> StorageResult:
    """Apply bounded retention and verify room for the next logical dump."""
    root.mkdir(parents=True, exist_ok=True)
    usage = usage_provider(root)
    files = managed_backup_files(root)
    selected = select_local_deletions(
        files,
        usage.used,
        usage.total,
        high_watermark,
        low_watermark,
    )
    deleted: list[str] = []
    reclaimed = 0
    for item in selected:
        path = Path(item.path)
        path.unlink()
        deleted.append(str(path))
        reclaimed += item.size_bytes

    projected_free = usage.free + reclaimed
    projected_used = max(0, usage.used - reclaimed)
    required = required_space(source)
    started_above_high = usage.used * 100 >= usage.total * high_watermark
    remains_above_low = projected_used * 100 > usage.total * low_watermark
    if started_above_high and remains_above_low:
        raise InsufficientSpaceError(
            "retention could not restore the low watermark without deleting protected backups"
        )
    if projected_free < required:
        raise InsufficientSpaceError(
            f"insufficient space for {source.identifier}: "
            f"required={required} available={projected_free}"
        )
    return StorageResult(required, projected_free, tuple(deleted))
