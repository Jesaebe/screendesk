"""Entrypoint with explicit phase-one safety boundaries."""

import json
import os
from pathlib import Path
import sys


def healthcheck() -> int:
    root = Path(os.environ.get("BACKUP_ROOT", "/backups"))
    status = Path("/status")
    return 0 if root.is_dir() and status.is_dir() else 1


def scheduler() -> int:
    message = {
        "status": "not_configured",
        "message": "Executor local disponível, mas o agendador e as origens permanecem desabilitados.",
    }
    status = Path("/status/latest.json")
    status.parent.mkdir(parents=True, exist_ok=True)
    status.write_text(json.dumps(message) + "\n", encoding="utf-8")
    return 0


def main(arguments: list[str]) -> int:
    command = arguments[1] if len(arguments) > 1 else "scheduler"
    if command == "healthcheck":
        return healthcheck()
    if command == "scheduler":
        return scheduler()
    print(f"unknown command: {command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
