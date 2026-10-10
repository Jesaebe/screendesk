from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]
TABLET = ROOT / "tablet"


class TabletArtifactTests(unittest.TestCase):
    def test_expected_artifacts_exist(self):
        for name in ["install.sh", "rollback.sh", "screendeck-kiosk", "screendeck-home.desktop"]:
            with self.subTest(name=name):
                self.assertTrue((TABLET / name).is_file())

    def test_installer_requires_authorization_before_apt(self):
        content = (TABLET / "install.sh").read_text(encoding="utf-8")
        guard = content.index("SCREENDECK_TABLET_AUTHORIZED")
        install = content.index("apt-get update")
        self.assertLess(guard, install)
        self.assertIn("dpkg --print-architecture", content)
        self.assertIn("SCREENDECK_HA_URL", content)

    def test_rollback_is_targeted_and_does_not_remove_chromium(self):
        content = (TABLET / "rollback.sh").read_text(encoding="utf-8")
        self.assertNotIn("rm -rf", content)
        self.assertNotIn("apt-get remove", content)
        self.assertIn("SCREENDECK_TABLET_ROLLBACK_AUTHORIZED", content)

    def test_launcher_has_no_fixed_server_or_credentials(self):
        content = (TABLET / "screendeck-kiosk").read_text(encoding="utf-8")
        self.assertNotIn("192.168.25.", content)
        self.assertNotIn("password", content.lower())
        self.assertIn("--kiosk", content)
        self.assertIn("xset -dpms", content)


if __name__ == "__main__":
    unittest.main()
