from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "backup"))

from src.control import test_connection
from src.executor import CommandResult


class FakeRunner:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def run(self, argv, environment):
        self.calls.append((argv, environment))
        return self.result


class ConnectionTestTests(unittest.TestCase):
    def payload(self, engine="postgresql"):
        return {"id": "financeiro", "engine": engine, "host": "db.internal", "port": 5432,
                "database": "financeiro", "sslmode": "require" if engine == "postgresql" else "required"}

    def test_postgres_uses_select_without_password_in_arguments(self):
        runner = FakeRunner(CommandResult(0, "16.4\n", ""))
        result = test_connection(self.payload(), "super-secret", runner)
        argv, environment = runner.calls[0]
        self.assertTrue(result["ok"])
        self.assertEqual(result["version"], "16.4")
        self.assertIn("SHOW server_version", argv)
        self.assertNotIn("super-secret", argv)
        self.assertEqual(environment["PGPASSWORD"], "super-secret")
        self.assertEqual(environment["PGCONNECT_TIMEOUT"], "10")

    def test_authentication_failure_is_sanitized(self):
        runner = FakeRunner(CommandResult(2, "", "password authentication failed for secret-user"))
        result = test_connection(self.payload(), "super-secret", runner)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "Falha de autenticação")
        self.assertNotIn("secret-user", str(result))


if __name__ == "__main__":
    unittest.main()
