import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "backup"))

from src.main import (
    DisabledNotifier,
    _notifier_from_environment,
    _positive_integer,
    _retention_watermarks,
    main,
)
from src.notifications import NotificationError, SMTPNotifier


class MainTests(unittest.TestCase):
    def test_positive_integer_rejects_invalid_values(self):
        with patch.dict(os.environ, {"TEST_INTERVAL": "0"}):
            with self.assertRaises(ValueError):
                _positive_integer("TEST_INTERVAL", 30)
        with patch.dict(os.environ, {"TEST_INTERVAL": "not-a-number"}):
            with self.assertRaises(ValueError):
                _positive_integer("TEST_INTERVAL", 30)

    def test_notifier_stays_disabled_without_complete_addressing(self):
        with patch.dict(os.environ, {}, clear=True):
            notifier = _notifier_from_environment()
        self.assertIsInstance(notifier, DisabledNotifier)
        with self.assertRaises(NotificationError):
            notifier.notify(None)

    def test_retention_watermarks_require_a_safe_order(self):
        environment = {
            "BACKUP_LOCAL_HIGH_WATERMARK": "75",
            "BACKUP_LOCAL_LOW_WATERMARK": "85",
        }
        with patch.dict(os.environ, environment, clear=True):
            with self.assertRaises(ValueError):
                _retention_watermarks()

    def test_notifier_uses_smtp_when_required_fields_exist(self):
        environment = {
            "SMTP_HOST": "smtp.example.internal",
            "SMTP_PORT": "2525",
            "ALERT_EMAIL_FROM": "from@example.com",
            "ALERT_EMAIL_TO": "to@example.com",
        }
        with patch.dict(os.environ, environment, clear=True):
            notifier = _notifier_from_environment()
        self.assertIsInstance(notifier, SMTPNotifier)
        self.assertEqual(notifier.settings.port, 2525)

    def test_scheduler_configuration_error_returns_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            missing = Path(temporary) / "missing.toml"
            with patch.dict(os.environ, {"BACKUP_CONFIG": str(missing)}, clear=True):
                self.assertEqual(main(["main", "scheduler"]), 1)

    def test_unknown_command_returns_usage_error(self):
        self.assertEqual(main(["main", "unknown"]), 2)


if __name__ == "__main__":
    unittest.main()
