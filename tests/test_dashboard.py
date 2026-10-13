import json
import os
from pathlib import Path
import importlib.util
import types
import sys
import tempfile
import unittest
from unittest.mock import patch

SERVER_PATH = Path(__file__).parents[1] / "dashboard" / "src" / "server.py"
PACKAGE = "screendeck_dashboard_test"
package = types.ModuleType(PACKAGE)
package.__path__ = [str(SERVER_PATH.parent)]
sys.modules[PACKAGE] = package
SPEC = importlib.util.spec_from_file_location(f"{PACKAGE}.server", SERVER_PATH)
server = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = server
SPEC.loader.exec_module(server)


class DashboardTests(unittest.TestCase):
    def test_json_round_trip_is_private(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            server.write_json(path, {"city": "Salvador"})
            self.assertEqual(server.read_json(path, {}), {"city": "Salvador"})
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_missing_json_uses_default(self):
        self.assertEqual(server.read_json(Path("/missing/screendeck.json"), {"ok": True}), {"ok": True})

    def test_weather_uses_geocoding_and_forecast(self):
        responses = [
            {"results": [{"name": "Salvador", "latitude": -12.9, "longitude": -38.5, "country": "Brasil"}]},
            {"current": {"temperature_2m": 27}, "daily": {}},
        ]
        server.WEATHER_CACHE.clear()
        with patch.object(server, "request_json", side_effect=responses):
            result = server.weather("Salvador")
        self.assertEqual(result["place"]["name"], "Salvador")
        self.assertEqual(result["current"]["temperature_2m"], 27)

    def test_weather_rejects_unknown_city(self):
        server.WEATHER_CACHE.clear()
        with patch.object(server, "request_json", return_value={"results": []}):
            with self.assertRaisesRegex(ValueError, "Cidade não encontrada"):
                server.weather("Lugar inexistente")

    def test_google_data_requests_complete_selected_month(self):
        requested = []

        def fake_google_api(url, **_kwargs):
            requested.append(url)
            if url.endswith("calendarList"):
                return {"items": [{"id": "primary"}]}
            if url.endswith("users/@me/lists"):
                return {"items": []}
            if "/events?" in url:
                return {"items": [{"id": "event-1", "summary": "Consulta", "start": {"date": "2026-11-12"}}]}
            return {"items": []}

        with patch.object(server, "google_api", side_effect=fake_google_api):
            result = server.google_data("2026-11")

        self.assertEqual(result["month"], "2026-11")
        self.assertEqual(result["events"][0]["summary"], "Consulta")
        events_url = next(url for url in requested if "/events?" in url)
        self.assertIn("timeMin=2026-11-01", events_url)
        self.assertIn("timeMax=2026-12-01", events_url)

    def test_backup_registry_forces_shared_existing_credential(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sources.toml"
            path.write_text("""[[source]]
id = "maker"
display_name = "Maker"
engine = "postgresql"
host = "db.local"
port = 5432
database = "janus"
username = "ignored"
password_file = "/run/secrets/other"
sslmode = "require"
schedule = ["00:00"]
timezone = "America/Bahia"
enabled = false
""", encoding="utf-8")
            original = server.BACKUP_CONFIG_PATH
            original_data_root = server.DATA_ROOT
            server.BACKUP_CONFIG_PATH = path
            server.DATA_ROOT = Path(directory)
            try:
                sources = server.load_backup_sources()
                sources[0]["display_name"] = "Maker atualizado"
                server.save_backup_sources(sources)
                saved = server.load_backup_sources()[0]
            finally:
                server.BACKUP_CONFIG_PATH = original
                server.DATA_ROOT = original_data_root
            self.assertEqual(saved["username"], "cyriusBackup")
            self.assertEqual(saved["password_file"], "/run/secrets/maker-password")
            self.assertEqual(saved["display_name"], "Maker atualizado")


if __name__ == "__main__":
    unittest.main()
