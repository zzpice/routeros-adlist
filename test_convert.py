"""Regression checks for interrupted downloads using only the standard library."""

import tempfile
import unittest
from http.client import IncompleteRead
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import convert


class DownloadRecoveryTests(unittest.TestCase):
    @staticmethod
    def configure_response(opener):
        response = opener.return_value.__enter__.return_value
        response.status = 200
        response.headers.get_content_type.return_value = "text/plain"
        return response

    def test_interrupted_body_is_retried(self):
        errors = (
            IncompleteRead(b"partial", 100),
            ConnectionResetError("connection reset while reading"),
        )
        for error in errors:
            with self.subTest(error=type(error).__name__):
                with patch("convert.urlopen") as opener, patch("convert.time.sleep"):
                    response = self.configure_response(opener)
                    response.read.side_effect = [error, b"example.com\n"]

                    self.assertEqual(convert.download("https://example.test/list"), "example.com\n")
                    self.assertEqual(opener.call_count, 2)

    def test_connection_and_http_failures_still_retry(self):
        errors = (
            HTTPError("https://example.test/list", 503, "Unavailable", {}, None),
            URLError("temporary connection failure"),
            TimeoutError("connection timed out"),
        )
        for error in errors:
            with self.subTest(error=type(error).__name__):
                with patch("convert.urlopen") as opener, patch("convert.time.sleep"):
                    self.configure_response(opener).read.return_value = b"example.com\n"
                    opener.side_effect = [error, opener.return_value]

                    self.assertEqual(convert.download("https://example.test/list"), "example.com\n")
                    self.assertEqual(opener.call_count, 2)

    def test_retry_exhaustion_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "adlist.txt"
            previous = "0.0.0.0 previous.example\n"
            output.write_text(previous, encoding="utf-8")

            with patch("convert.urlopen") as opener, patch("convert.time.sleep"):
                self.configure_response(opener).read.side_effect = IncompleteRead(b"partial", 100)

                with self.assertRaises(RuntimeError):
                    convert.build("https://example.test/list", output, min_domains=1)

                self.assertEqual(opener.call_count, 3)
                self.assertEqual(output.read_text(encoding="utf-8"), previous)


if __name__ == "__main__":
    unittest.main()
