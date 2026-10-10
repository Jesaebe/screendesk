from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]


class ConfigurationTests(unittest.TestCase):
    def test_required_foundation_files_exist(self):
        required = [
            ".env.example",
            ".gitignore",
            "compose.yaml",
            "home-assistant/configuration.yaml",
            "backup/config/sources.example.toml",
        ]
        for relative in required:
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file())

    def test_example_environment_has_no_assigned_password(self):
        lines = (ROOT / ".env.example").read_text(encoding="utf-8").splitlines()
        sensitive = (line for line in lines if "PASSWORD=" in line)
        self.assertTrue(all(line.endswith("=") for line in sensitive))


if __name__ == "__main__":
    unittest.main()
