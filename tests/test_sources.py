from datetime import datetime, timezone
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "backup"))

from src.config import load_sources
from src.schedule import is_due


class SourceConfigurationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = load_sources(ROOT / "backup/config/sources.example.toml")

    def test_maker_matches_supplied_database_details(self):
        maker = self.sources[0]
        self.assertEqual(maker.identifier, "maker")
        self.assertEqual(maker.engine, "postgresql")
        self.assertEqual(maker.version, "14")
        self.assertEqual(maker.host, "151.243.236.61")
        self.assertEqual(maker.port, 5433)
        self.assertEqual(maker.database, "janus")
        self.assertEqual(maker.estimated_size_mb, 15)
        self.assertEqual(maker.schedule, ("00:00", "06:00", "12:00", "18:00"))

    def test_maker_is_safely_disabled_until_secrets_and_cloud_are_ready(self):
        maker = self.sources[0]
        self.assertEqual(maker.username, "cyriusBackup")
        self.assertEqual(maker.password_file, "/run/secrets/maker-password")
        self.assertFalse(maker.enabled)
        self.assertIn("instalar segredo", maker.readiness_note)

    def test_disabled_source_is_never_due(self):
        maker = self.sources[0]
        instant = datetime(2026, 10, 9, 9, 0, tzinfo=timezone.utc)
        self.assertFalse(is_due(maker, instant))

    def test_bahia_timezone_matches_six_oclock(self):
        maker = self.sources[0]
        enabled_maker = type(maker)(**{**maker.__dict__, "enabled": True})
        instant = datetime(2026, 10, 9, 9, 0, tzinfo=timezone.utc)
        self.assertTrue(is_due(enabled_maker, instant))


if __name__ == "__main__":
    unittest.main()
