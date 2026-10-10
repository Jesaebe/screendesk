import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "backup"))

from src.notifications import NotificationError, SMTPNotifier, SMTPSettings, failure_message
from src.reporting import RunReport


def failed_report():
    return RunReport(
        run_id="maker-1",
        source="maker",
        started_at="2026-10-09T09:00:00+00:00",
        finished_at="2026-10-09T09:01:00+00:00",
        duration_seconds=60,
        status="cloud_failed",
        size_bytes=100,
        local_destination="/backups/maker.dump",
        cloud_destination="",
        error="simulated sanitized error",
        log_file="/backups/maker.log",
    )


class FakeSMTP:
    def __init__(self, host, port, timeout):
        self.connection = (host, port, timeout)
        self.started_tls = False
        self.login_values = None
        self.message = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def starttls(self):
        self.started_tls = True

    def login(self, username, password):
        self.login_values = (username, password)

    def send_message(self, message):
        self.message = message


class SMTPFactory:
    def __init__(self):
        self.client = None

    def __call__(self, host, port, timeout):
        self.client = FakeSMTP(host, port, timeout)
        return self.client


class FailingSMTPFactory:
    def __call__(self, host, port, timeout):
        raise RuntimeError("smtp-secret leaked by provider")


class NotificationTests(unittest.TestCase):
    def test_message_contains_operational_fields(self):
        content = failure_message(failed_report()).get_content()
        self.assertIn("maker-1", content)
        self.assertIn("cloud_failed", content)
        self.assertIn("simulated sanitized error", content)

    def test_smtp_adapter_uses_tls_and_login(self):
        factory = SMTPFactory()
        settings = SMTPSettings(
            "smtp.example.internal", 587, "sender-user", "smtp-secret", "from@example.com", "to@example.com"
        )
        SMTPNotifier(settings, factory).notify(failed_report())
        self.assertTrue(factory.client.started_tls)
        self.assertEqual(factory.client.login_values, ("sender-user", "smtp-secret"))
        self.assertEqual(factory.client.message["To"], "to@example.com")

    def test_smtp_failure_is_sanitized(self):
        settings = SMTPSettings(
            "smtp.example.internal", 587, "sender-user", "smtp-secret", "from@example.com", "to@example.com"
        )
        with self.assertRaises(NotificationError) as raised:
            SMTPNotifier(settings, FailingSMTPFactory()).notify(failed_report())
        self.assertNotIn("smtp-secret", str(raised.exception))
        self.assertIn("RuntimeError", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
