import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "backup"))

from src.redaction import redact


class RedactionTests(unittest.TestCase):
    def test_redacts_all_known_nonempty_values(self):
        message = "password=alpha token=alphabet empty remains"
        result = redact(message, ["alpha", "alphabet", ""])
        self.assertNotIn("alpha", result)
        self.assertEqual(result.count("[REDACTED]"), 2)


if __name__ == "__main__":
    unittest.main()
