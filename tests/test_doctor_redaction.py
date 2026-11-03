import unittest
from unittest.mock import patch

from click.testing import CliRunner
from obsad.cli import main


class DoctorRedactionTests(unittest.TestCase):
    def test_url_and_exception_are_not_reported(self):
        url = "https://user:fake-secret@example.invalid/?token=other-fake-secret"
        with patch("obsad.cli.shutil.which", return_value="/mock"), patch("obsad.cli.requests.get", side_effect=RuntimeError("request to " + url)):
            result = CliRunner().invoke(main, ["doctor", "--url", url])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("request failed (RuntimeError)", result.output)
        for secret in (url, "fake-secret", "other-fake-secret"):
            self.assertNotIn(secret, result.output)

    def test_success_reports_status_without_url(self):
        class Response:
            ok = True
            status_code = 200
        with patch("obsad.cli.shutil.which", return_value="/mock"), patch("obsad.cli.requests.get", return_value=Response()):
            result = CliRunner().invoke(main, ["doctor", "--url", "https://private.invalid"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("PASS  comfyui (HTTP 200)", result.output)
        self.assertNotIn("private.invalid", result.output)


if __name__ == "__main__":
    unittest.main()
