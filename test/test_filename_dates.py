"""Verify filename date parsing independently of the GUI and image libraries."""

import unittest
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from filename_dates import parse_filename_datetime


class FilenameDateParserTests(unittest.TestCase):
    """Cover supported filename formats and invalid timestamp inputs."""

    def test_parses_underscore_format(self):
        self.assertEqual(
            parse_filename_datetime("IMG_UPLOAD_20230422_103446.jpg"),
            datetime(2023, 4, 22, 10, 34, 46),
        )

    def test_parses_hyphen_format(self):
        self.assertEqual(
            parse_filename_datetime("IMG_UPLOAD_20230422-103446.jpg"),
            datetime(2023, 4, 22, 10, 34, 46),
        )

    def test_parses_facebook_unix_milliseconds_format(self):
        self.assertEqual(
            parse_filename_datetime("FB_IMG_1488170740397.jpg"),
            datetime.fromtimestamp(1488170740397 / 1000),
        )

    def test_parses_received_unix_microseconds_format(self):
        self.assertEqual(
            parse_filename_datetime("received_1638770899781207.jpeg"),
            datetime.fromtimestamp(1638770899781207 / 1_000_000),
        )

    def test_parses_android_screenshot_millisecond_format(self):
        self.assertEqual(
            parse_filename_datetime(
                "Screenshot_2026-07-24-12-02-19-849_com.google.android.apps.docs.jpg"
            ),
            datetime(2026, 7, 24, 12, 2, 19, 849000),
        )

    def test_rejects_invalid_calendar_date(self):
        self.assertIsNone(parse_filename_datetime("IMG_UPLOAD_20230230_103446.jpg"))

    def test_rejects_unrecognized_format(self):
        self.assertIsNone(parse_filename_datetime("IMG_UPLOAD_20230422.jpg"))

    def test_rejects_timestamp_embedded_in_longer_number(self):
        self.assertIsNone(parse_filename_datetime("120230422_1034467.jpg"))

    def test_rejects_millisecond_timestamp_with_wrong_length(self):
        self.assertIsNone(parse_filename_datetime("FB_IMG_148817074039.jpg"))


if __name__ == "__main__":
    unittest.main()