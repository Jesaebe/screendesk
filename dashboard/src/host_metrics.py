"""Read host health from explicitly mounted, read-only Linux paths."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import threading
import time
from typing import Any


class HostMetrics:
    def __init__(
        self,
        proc_root: Path,
        root_path: Path,
        backup_path: Path,
        history_path: Path,
        backup_status_path: Path,
        *,
        interval_seconds: int = 1,
        history_interval_seconds: int = 60,
        history_limit: int = 1440,
    ) -> None:
        self.proc_root = proc_root
        self.root_path = root_path
        self.backup_path = backup_path
        self.history_path = history_path
        self.backup_status_path = backup_status_path
        self.interval_seconds = interval_seconds
        self.history_interval_seconds = history_interval_seconds
        self.history_limit = history_limit
        self._previous_cpu: tuple[int, int] | None = None
        self._latest: dict[str, Any] | None = None
        self._history: deque[dict[str, Any]] = deque(maxlen=history_limit)
        self._lock = threading.Lock()
        self._load_history()

    def _load_history(self) -> None:
        try:
            lines = self.history_path.read_text(encoding="utf-8").splitlines()
            for line in lines[-self.history_limit:]:
                self._history.append(json.loads(line))
        except (OSError, ValueError, TypeError):
            self._history.clear()

    def _cpu_percent(self) -> float | None:
        fields = (self.proc_root / "stat").read_text(encoding="utf-8").splitlines()[0].split()[1:]
        values = [int(value) for value in fields]
        idle = values[3] + (values[4] if len(values) > 4 else 0)
        total = sum(values)
        current = (total, idle)
        previous, self._previous_cpu = self._previous_cpu, current
        if previous is None or total <= previous[0]:
            return None
        delta_total = total - previous[0]
        return round(100 * (1 - (idle - previous[1]) / delta_total), 1)

    def _memory(self) -> dict[str, float]:
        values: dict[str, int] = {}
        for line in (self.proc_root / "meminfo").read_text(encoding="utf-8").splitlines():
            key, raw = line.split(":", 1)
            values[key] = int(raw.strip().split()[0]) * 1024
        total = values["MemTotal"]
        available = values.get("MemAvailable", values.get("MemFree", 0))
        swap_total = values.get("SwapTotal", 0)
        swap_free = values.get("SwapFree", 0)
        return {
            "used_percent": round(100 * (total - available) / total, 1),
            "available_bytes": available,
            "total_bytes": total,
            "swap_used_percent": round(100 * (swap_total - swap_free) / swap_total, 1) if swap_total else 0,
        }

    @staticmethod
    def _disk(path: Path) -> dict[str, float]:
        usage = shutil.disk_usage(path)
        return {
            "used_percent": round(100 * usage.used / usage.total, 1),
            "free_bytes": usage.free,
            "total_bytes": usage.total,
        }

    def _backup_available(self, now: float) -> bool:
        try:
            payload = json.loads(self.backup_status_path.read_text(encoding="utf-8"))
            updated = datetime.fromisoformat(payload["updated_at"]).timestamp()
            return now - updated <= max(120, self.interval_seconds * 3)
        except (OSError, ValueError, TypeError, KeyError):
            return False

    def collect(self) -> dict[str, Any]:
        now = time.time()
        load = [float(value) for value in (self.proc_root / "loadavg").read_text().split()[:3]]
        cpu_count = sum(1 for line in (self.proc_root / "stat").read_text(encoding="utf-8").splitlines() if line.startswith("cpu") and line[3:4].isdigit()) or 1
        result = {
            "recorded_at": datetime.fromtimestamp(now, timezone.utc).isoformat(),
            "cpu_percent": self._cpu_percent(),
            "load": {"one": load[0], "five": load[1], "fifteen": load[2], "cpu_count": cpu_count},
            "memory": self._memory(),
            "root_disk": self._disk(self.root_path),
            "backup_disk": self._disk(self.backup_path),
            "uptime_seconds": float((self.proc_root / "uptime").read_text().split()[0]),
            "services": {"dashboard": True, "backup": self._backup_available(now)},
        }
        with self._lock:
            self._latest = result
        return result

    def record(self, result: dict[str, Any] | None = None) -> dict[str, Any]:
        result = result or self.collect()
        with self._lock:
            self._history.append(result)
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.history_path.with_suffix(".tmp")
            temporary.write_text("".join(json.dumps(item, separators=(",", ":")) + "\n" for item in self._history), encoding="utf-8")
            os.chmod(temporary, 0o600)
            temporary.replace(self.history_path)
        return result

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            latest = self._latest
        return latest or self.collect()

    def history(self, limit: int = 60) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._history)[-max(1, min(limit, self.history_limit)):]

    def run_forever(self) -> None:
        next_history_sample = 0.0
        while True:
            try:
                result = self.collect()
                current = time.monotonic()
                if current >= next_history_sample:
                    self.record(result)
                    next_history_sample = current + self.history_interval_seconds
            except (OSError, ValueError, ZeroDivisionError) as error:
                print(f"host metrics collection failed: {type(error).__name__}", flush=True)
            time.sleep(self.interval_seconds)

    def start(self) -> None:
        threading.Thread(target=self.run_forever, name="host-metrics", daemon=True).start()
