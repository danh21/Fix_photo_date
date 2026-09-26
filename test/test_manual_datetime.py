"""Test parsing date-time values entered in the manual edit mode."""

import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from manual_datetime import parse_manual_datetime


class ManualDateTimeParserTests(unittest.TestCase):
    """Verify the manual date-time input format and validation."""

    def test_parses_expected_format(self):
        self.assertEqual(
            parse_manual_datetime("2021-12-06 06:08:19"),
            datetime(2021, 12, 6, 6, 8, 19),
        )

    def test_ignores_surrounding_whitespace(self):
        self.assertEqual(
            parse_manual_datetime(" 2021-12-06 06:08:19 "),
            datetime(2021, 12, 6, 6, 8, 19),
        )

    def test_rejects_invalid_calendar_date(self):
        with self.assertRaises(ValueError):
            parse_manual_datetime("2021-02-30 06:08:19")

    def test_rejects_other_formats(self):
        with self.assertRaises(ValueError):
            parse_manual_datetime("06/12/2021 06:08:19")


if __name__ == "__main__":
    unittest.main()