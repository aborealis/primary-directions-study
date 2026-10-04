"""
Calc-free helpers operating on the person records of the samples:
lifespan, total action length of the directions, and event dates.

These functions depend only on the sample data format, which makes
them testable without the proprietary astrological computation
engine (the ``calc`` package).
"""
from datetime import datetime
from typing import Any

from direction_analysis.helpers.common_functions import (
    SECONDS_IN_YEAR,
    make_datetime,
)


def life_len(person: dict[str, Any]) -> float:
    """Determines the lifespan of the native based on their data"""
    birth = make_datetime(person['chartData']['date'])
    death = make_datetime(person['death'])
    return (death - birth).total_seconds() / SECONDS_IN_YEAR


def total_action_length(intervals: list[list[datetime]]) -> float:
    """
    Returns the total duration of the directions’ influence (in years)
    over the course of life.
    """
    length = 0.0

    for item in intervals:
        duration = item[1] - item[0]
        years = duration.total_seconds() / SECONDS_IN_YEAR
        length += years

    return length


def extract_event_date(events: list[dict[str, Any]]) -> datetime:
    """Extracts the event date from the record about native"""
    event_dates = [make_datetime(item['date']) for item in events]
    return sorted(event_dates)[0]


def is_event_in_interval(events: list[dict[str, Any]],
                         intervals: list[list[datetime]]) -> bool:
    """Determines whether the event date falls within the specified interval"""
    event_date = extract_event_date(events)
    for interval in intervals:
        if interval[0] <= event_date <= interval[1]:
            return True

    return False
