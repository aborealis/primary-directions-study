"""Common helper functions for date and time parsing."""
from datetime import datetime

SECONDS_IN_YEAR = 60 * 60 * 24 * 365.24


def extract_date(string: str) -> list[int]:
    """Extracts the year, month, and day from a string like 1900/02/10"""
    year, month, day = string.split('/')
    return [int(year), int(month), int(day)]


def extract_time(string: str) -> list[int]:
    """Extracts the hour and minute from a string like 07:48"""
    hour, minute = string.split(':')
    return [int(hour), int(minute)]


def make_datetime(date_str: str) -> datetime:
    """Converts a string in the format YYYY/MM/DD into a datetime object"""
    year, month, day = extract_date(date_str)
    if day == 0:  # Some recorded dates lack the day (YYYY/MM/00)
        day = 15
    return datetime(year, month, day)
