import sys
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "backup"))

from src.cloud import CloudError, cloud_destination, prune_cloud, upload_encrypted
from src.executor import CommandResult


class FakeCloudRunner:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.result = CommandResult(returncode, stdout, stderr)
        self.calls = []

    def run(self, argv, environment):
        self.calls.append((argv, environment))
        return self.result


class CloudAdapterTests(unittest.TestCase):
    def test_builds_copyto_for_source_directory(self):
        runner = FakeCloudRunner(stdout="uploaded")
        with tempfile.TemporaryDirectory() as directory:
            backup = Path(directory) / "maker.dump"
            backup.write_bytes(b"backup")
            result = upload_encrypted(
                backup,
                "maker",
                "gdrive-crypt:screendeck-home",
                Path("/run/secrets/rclone.conf"),
                runner,
            )
        argv, environment = runner.calls[0]
        self.assertEqual(argv[0:2], ["rclone", "copyto"])
        self.assertEqual(argv[-1], "gdrive-crypt:screendeck-home/maker/maker.dump")
        self.assertEqual(result.destination, argv[-1])
        self.assertEqual(environment, {})

    def test_retention_is_scoped_and_uses_fifteen_days(self):
        runner = FakeCloudRunner()
        prune_cloud(
            "maker",
            "gdrive-crypt:screendeck-home",
            Path("/run/secrets/rclone.conf"),
            15,
            runner,
        )
        argv, _ = runner.calls[0]
        self.assertEqual(argv[0:2], ["rclone", "delete"])
        self.assertEqual(argv[argv.index("--min-age") + 1], "15d")
        self.assertEqual(argv[-1], "gdrive-crypt:screendeck-home/maker")

    def test_failure_redacts_known_secret(self):
        runner = FakeCloudRunner(returncode=1, stderr="token cloud-secret rejected")
        with tempfile.TemporaryDirectory() as directory:
            backup = Path(directory) / "maker.dump"
            backup.write_bytes(b"backup")
            with self.assertRaises(CloudError) as raised:
                upload_encrypted(
                    backup,
                    "maker",
                    "gdrive-crypt:screendeck-home",
                    Path("/run/secrets/rclone.conf"),
                    runner,
                    ["cloud-secret"],
                )
        self.assertNotIn("cloud-secret", str(raised.exception))
        self.assertIn("[REDACTED]", str(raised.exception))

    def test_rejects_remote_path_traversal(self):
        with self.assertRaises(ValueError):
            cloud_destination("gdrive-crypt:../outside", "maker", Path("maker.dump"))

    def test_rejects_empty_local_file(self):
        with tempfile.TemporaryDirectory() as directory:
            backup = Path(directory) / "empty.dump"
            backup.touch()
            with self.assertRaises(ValueError):
                upload_encrypted(
                    backup,
                    "maker",
                    "gdrive-crypt:screendeck-home",
                    Path("/run/secrets/rclone.conf"),
                    FakeCloudRunner(),
                )


if __name__ == "__main__":
    unittest.main()
