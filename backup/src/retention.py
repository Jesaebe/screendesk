"""Pure retention decisions; deletion is intentionally handled elsewhere."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BackupFile:
    path: str
    source: str
    size_bytes: int
    modified_at: float


def select_local_deletions(
    files: list[BackupFile],
    used_bytes: int,
    total_bytes: int,
    high_watermark: int = 85,
    low_watermark: int = 75,
) -> list[BackupFile]:
    """Select oldest files while preserving the newest file per source."""
    if total_bytes <= 0:
        raise ValueError("total_bytes must be positive")
    if not 0 <= low_watermark < high_watermark <= 100:
        raise ValueError("watermarks must satisfy 0 <= low < high <= 100")
    if used_bytes * 100 < total_bytes * high_watermark:
        return []

    newest: dict[str, BackupFile] = {}
    for item in files:
        if item.source not in newest or item.modified_at > newest[item.source].modified_at:
            newest[item.source] = item

    target_used = total_bytes * low_watermark // 100
    projected_used = used_bytes
    selected: list[BackupFile] = []
    for item in sorted(files, key=lambda candidate: candidate.modified_at):
        if newest.get(item.source) == item:
            continue
        selected.append(item)
        projected_used = max(0, projected_used - item.size_bytes)
        if projected_used <= target_used:
            break
    return selected
