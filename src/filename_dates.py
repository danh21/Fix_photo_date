"""Parse supported photo filename formats into Python datetime values."""

import re
from datetime import datetime
from typing import Callable


# Keep each filename format in its own parser so new formats do not alter
# the behavior of formats that are already supported.
FilenameDateParser = Callable[[str], datetime | None]

# e.g. IMG_UPLOAD_20230422_103446.jpg or IMG_UPLOAD_20230422-103446.jpg
def _parse_compact_date_time(filename: str) -> datetime | None:
    """Parse YYYYMMDD_HHMMSS and YYYYMMDD-HHMMSS timestamps."""
    pattern = re.compile(
        r"(?<!\d)(20\d{2})(\d{2})(\d{2})[_-](\d{2})(\d{2})(\d{2})(?!\d)"
    )
    match = pattern.search(filename)
    if match is None:
        return None

    try:
        year, month, day, hour, minute, second = map(int, match.groups())
        return datetime(year, month, day, hour, minute, second)
    except ValueError:
        return None


# e.g. FB_IMG_1488170740397.jpg is a 13-digit Unix timestamp in milliseconds.
def _parse_unix_milliseconds(filename: str) -> datetime | None:
    """Parse a 13-digit Unix timestamp in milliseconds from a filename."""
    match = re.search(r"(?<!\d)(\d{13})(?!\d)", filename)
    if match is None:
        return None

    try:
        timestamp_seconds = int(match.group(1)) / 1000
        return datetime.fromtimestamp(timestamp_seconds)
    except (OverflowError, OSError, ValueError):
        return None


# Add new filename format parsers here without changing existing handlers.
FILENAME_DATE_PARSERS: tuple[FilenameDateParser, ...] = (
    _parse_compact_date_time,
    _parse_unix_milliseconds,
)


def parse_filename_datetime(filename: str) -> datetime | None:
    """Return the first valid date found by the registered format parsers."""
    for parser in FILENAME_DATE_PARSERS:
        parsed_datetime = parser(filename)
        if parsed_datetime is not None:
            return parsed_datetime
    return None