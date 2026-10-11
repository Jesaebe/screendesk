from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]
SCRIPTS = ROOT / "scripts"


class DeploymentArtifactTests(unittest.TestCase):
    def test_preflight_is_read_only_and_checks_target(self):
        content = (SCRIPTS / "preflight-deploy.sh").read_text(encoding="utf-8")
        self.assertIn("192.168.25.249", content)
        self.assertIn("sport = :8123", content)
        self.assertIn('backup_owner" == "$backup_uid"', content)
        self.assertIn("/home/cyrius/.config/rclone", content)
        self.assertIn('rclone_config_host="$rclone_config_dir_host/rclone.conf"', content)
        self.assertIn("/home/cyrius/.config/screendeck-home/maker-password", content)
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

    def test_rclone_config_is_mounted_read_only_from_server(self):
        compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
        dockerfile = (ROOT / "backup" / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("RCLONE_CONFIG_DIR_HOST", compose)
        self.assertIn("BACKUP_CLOUD_REMOTE", compose)
        self.assertNotIn("RCLONE_CRYPT_REMOTE", compose)
        self.assertIn("/home/cyrius/.config/rclone", compose)
        self.assertIn(":/run/rclone:rw", compose)
        self.assertIn(":/run/secrets/maker-password:ro", compose)
        self.assertIn('${BACKUP_UID:-1000}:${BACKUP_GID:-1000}', compose)
        self.assertIn("--uid 1000 screendeck", dockerfile)


if __name__ == "__main__":
    unittest.main()
