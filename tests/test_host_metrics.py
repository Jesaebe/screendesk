import json
from pathlib import Path
import importlib.util
import tempfile
import unittest


ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "dashboard" / "src" / "host_metrics.py"
SPEC = importlib.util.spec_from_file_location("dashboard_host_metrics", MODULE_PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(module)
HostMetrics = module.HostMetrics


class HostMetricsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.proc = root / "proc"
        self.proc.mkdir()
        (self.proc / "meminfo").write_text(
            "MemTotal: 1000 kB\nMemAvailable: 250 kB\nSwapTotal: 200 kB\nSwapFree: 50 kB\n",
            encoding="utf-8",
        )
        (self.proc / "loadavg").write_text("0.25 0.50 0.75 1/100 1\n", encoding="utf-8")
        (self.proc / "uptime").write_text("172800.00 0.00\n", encoding="utf-8")
        self.status = root / "service-status.json"
        self.status.write_text(json.dumps({"updated_at": "2999-01-01T00:00:00+00:00"}), encoding="utf-8")
        self.metrics = HostMetrics(self.proc, root, root, root / "history.jsonl", self.status)

    def tearDown(self):
        self.temporary.cleanup()

    def _stat(self, idle: int, total_work: int) -> None:
        (self.proc / "stat").write_text(
            f"cpu {total_work} 0 0 {idle} 0 0 0 0\ncpu0 1 0 0 1\ncpu1 1 0 0 1\n",
            encoding="utf-8",
        )

    def test_collects_host_memory_load_disks_and_services(self):
        self._stat(80, 20)
        first = self.metrics.collect()
        self._stat(120, 80)
        result = self.metrics.collect()
        self.assertEqual(first["cpu_percent"], None)
        self.assertEqual(result["cpu_percent"], 60.0)
        self.assertEqual(result["memory"]["used_percent"], 75.0)
        self.assertEqual(result["memory"]["total_bytes"], 1000 * 1024)
        self.assertEqual(result["memory"]["swap_used_percent"], 75.0)
        self.assertGreater(result["root_disk"]["total_bytes"], 0)
        self.assertGreater(result["backup_disk"]["total_bytes"], 0)
        self.assertEqual(result["load"]["fifteen"], 0.75)
        self.assertEqual(result["load"]["cpu_count"], 2)
        self.assertEqual(result["uptime_seconds"], 172800.0)
        self.assertTrue(result["services"]["backup"])

    def test_record_persists_bounded_private_history(self):
        self.metrics.history_limit = 2
        self.metrics._history = __import__("collections").deque(maxlen=2)
        for value in (80, 90, 100):
            self._stat(value, 20)
            self.metrics.record()
        self.assertEqual(len(self.metrics.history(10)), 2)
        self.assertEqual(self.metrics.history_path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(len(self.metrics.history_path.read_text().splitlines()), 2)


if __name__ == "__main__":
    unittest.main()
