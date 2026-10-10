"""Rclone command adapter; callers inject the command runner in tests."""

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Protocol

from .executor import CommandResult
from .redaction import redact


class CloudError(RuntimeError):
    pass


class CloudRunner(Protocol):
    def run(self, argv: list[str], environment: dict[str, str]) -> CommandResult: ...


@dataclass(frozen=True)
class CloudResult:
    destination: str
    output: str


def validate_remote(remote: str) -> None:
    if not remote or ":" not in remote:
        raise ValueError("rclone remote must use the form remote:path")
    remote_name, path = remote.split(":", 1)
    if not remote_name or not path or path.startswith("/") or ".." in PurePosixPath(path).parts:
        raise ValueError("rclone remote path must be relative and cannot contain '..'")


def cloud_destination(remote: str, source_id: str, local_file: Path) -> str:
    validate_remote(remote)
    if "/" in source_id or source_id in {"", ".", ".."}:
        raise ValueError("invalid source id for cloud destination")
    return f"{remote.rstrip('/')}/{source_id}/{local_file.name}"


def upload_encrypted(
    local_file: Path,
    source_id: str,
    remote: str,
    config_path: Path,
    runner: CloudRunner,
    known_secrets: list[str] | None = None,
) -> CloudResult:
    if not local_file.is_file() or local_file.stat().st_size <= 0:
        raise ValueError("local backup must be a non-empty file")
    destination = cloud_destination(remote, source_id, local_file)
    argv = [
        "rclone",
        "copyto",
        "--config",
        str(config_path),
        "--checksum",
        str(local_file),
        destination,
    ]
    result = runner.run(argv, {})
    output = redact(result.stdout + result.stderr, known_secrets or [])
    if result.returncode != 0:
        raise CloudError(f"rclone upload exited with code {result.returncode}: {output}")
    return CloudResult(destination, output)


def prune_cloud(
    source_id: str,
    remote: str,
    config_path: Path,
    retention_days: int,
    runner: CloudRunner,
    known_secrets: list[str] | None = None,
) -> str:
    if retention_days < 1:
        raise ValueError("cloud retention must be at least one day")
    source_remote = cloud_destination(remote, source_id, Path("placeholder")).rsplit("/", 1)[0]
    argv = [
        "rclone",
        "delete",
        "--config",
        str(config_path),
        "--min-age",
        f"{retention_days}d",
        source_remote,
    ]
    result = runner.run(argv, {})
    output = redact(result.stdout + result.stderr, known_secrets or [])
    if result.returncode != 0:
        raise CloudError(f"rclone retention exited with code {result.returncode}: {output}")
    return output
