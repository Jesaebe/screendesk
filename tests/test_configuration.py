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

    def test_smtp_password_is_a_mounted_file_not_an_environment_secret(self):
        environment = (ROOT / ".env.example").read_text(encoding="utf-8")
        compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
        self.assertNotIn("SMTP_PASSWORD=", environment)
        self.assertNotIn("SMTP_PASSWORD:", compose)
        self.assertIn("SMTP_PASSWORD_FILE", environment)
        self.assertIn(":/run/secrets/smtp-password:ro", compose)

    def test_runtime_secrets_directory_is_ignored(self):
        content = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("/secrets/", content)


if __name__ == "__main__":
    unittest.main()
