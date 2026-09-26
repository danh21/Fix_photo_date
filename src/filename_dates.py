"""Parse supported photo filename formats into Python datetime values."""

import re
from datetime import datetime
from typing import Callable


# Keep each filename format in its own parser so new formats do not alter
# the behavior of formats that are already supported.
FilenameDateParser = Callable[[str], datetime | None]


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


# Add a parser here when introducing another filename format.
FILENAME_DATE_PARSERS: tuple[FilenameDateParser, ...] = (_parse_compact_date_time,)


def parse_filename_datetime(filename: str) -> datetime | None:
    """Return the first valid date found by the registered format parsers."""
    for parser in FILENAME_DATE_PARSERS:
        parsed_datetime = parser(filename)
        if parsed_datetime is not None:
            return parsed_datetime
    return None