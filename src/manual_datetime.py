"""Parse date-time values entered manually in the application."""

from datetime import datetime


def parse_manual_datetime(value: str) -> datetime:
    """Parse a local date-time entered as YYYY-MM-DD HH:MM:SS."""
    return datetime.strptime(value.strip(), "%Y-%m-%d %H:%M:%S")