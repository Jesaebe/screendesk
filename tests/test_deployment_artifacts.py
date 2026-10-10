from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]
SCRIPTS = ROOT / "scripts"


class DeploymentArtifactTests(unittest.TestCase):
    def test_preflight_is_read_only_and_checks_target(self):
        content = (SCRIPTS / "preflight-deploy.sh").read_text(encoding="utf-8")
        self.assertIn("192.168.25.249", content)
        self.assertIn("sport = :8123", content)
        self.assertIn('backup_owner" == "10001"', content)
        self.assertIn("docker compose", content)
        self.assertNotIn("docker compose up", content)
        self.assertNotIn("sudo ", content)
        self.assertNotIn("rm -", content)
        self.assertNotIn("chmod ", content)
        self.assertNotIn("chown ", content)

    def test_mutating_scripts_keep_explicit_guards(self):
        deploy = (SCRIPTS / "deploy.sh").read_text(encoding="utf-8")
        rollback = (SCRIPTS / "rollback.sh").read_text(encoding="utf-8")
        self.assertIn("SCREENDECK_DEPLOY_AUTHORIZED", deploy)
        self.assertIn("SCREENDECK_ROLLBACK_AUTHORIZED", rollback)


if __name__ == "__main__":
    unittest.main()
