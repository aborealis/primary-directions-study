"""Tests of the calc-free person-data helpers."""

from datetime import datetime

import pytest

from direction_analysis.helpers.common_functions import make_datetime
from direction_analysis.probability_assessment.person_data import (
    extract_event_date,
    is_event_in_interval,
    life_len,
    total_action_length,
)


def test_make_datetime() -> None:
    assert make_datetime('2020/01/05') == datetime(2020, 1, 5)


def test_make_datetime_day_zero_becomes_fifteenth() -> None:
    """Dates lacking the day are recorded as /00 and mapped to 15."""
    assert make_datetime('1900/02/00') == datetime(1900, 2, 15)


def test_life_len() -> None:
    person = {
        'chartData': {'date': '1946/03/09'},
        'death': '1984/11/15',
    }

    assert life_len(person) == pytest.approx(38.689628737268649)


def test_total_action_length() -> None:
    intervals = [[datetime(2000, 1, 1), datetime(2000, 1, 11)]]

    # 10 days expressed in years of 365.24 days
    assert total_action_length(intervals) == pytest.approx(0.027379257474537292)

    assert total_action_length([]) == 0.0


def test_extract_event_date_returns_earliest() -> None:
    events = [
        {'date': '2001/05/06'},
        {'date': '2000/03/01'},
    ]

    assert extract_event_date(events) == datetime(2000, 3, 1)


def test_is_event_in_interval() -> None:
    intervals = [[datetime(2000, 1, 1), datetime(2000, 1, 11)]]

    assert is_event_in_interval(
        [{'date': '2000/01/05'}], intervals) is True
    assert is_event_in_interval(
        [{'date': '2000/02/01'}], intervals) is False
    assert is_event_in_interval([{'date': '2000/01/05'}], []) is False
