import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "backup"))

from src.dump import Source, build_dump_command


def source_for(engine):
    return Source(
        identifier="main",
        display_name="Main",
        engine=engine,
        version="14",
        host="db.local",
        port=5432 if engine == "postgresql" else 3306,
        database="app",
        username="reader",
        password_env="BACKUP_DB_PASSWORD",
        sslmode="require",
        schedule=("00:00",),
        timezone="America/Bahia",
        estimated_size_mb=15,
        enabled=False,
        readiness_note="",
    )


class DumpCommandTests(unittest.TestCase):
    def test_postgres_command_does_not_contain_password(self):
        source = source_for("postgresql")
        command = build_dump_command(source, "/backups/app.dump")
        self.assertEqual(command[0], "pg_dump")
        self.assertNotIn("DB_PASSWORD", command)
        self.assertNotIn("secret", command)

    def test_mariadb_uses_consistent_dump_options(self):
        source = source_for("mariadb")
        command = build_dump_command(source, "/backups/app.sql")
        self.assertEqual(command[0], "mariadb-dump")
        self.assertIn("--single-transaction", command)

    def test_unknown_engine_is_rejected(self):
        source = source_for("unknown")
        with self.assertRaises(ValueError):
            build_dump_command(source, "/tmp/file")


if __name__ == "__main__":
    unittest.main()
