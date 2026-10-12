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


if __name__ == "__main__":
    unittest.main()
