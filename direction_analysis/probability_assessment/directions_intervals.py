"""
Combines the action intervals of the directions and determines
y = {0,1} — whether the event occurred on the direction or not

Requires the proprietary ``calc`` computation engine, which is not
distributed with this repository; without it this module cannot be used.
"""
from datetime import datetime, timedelta

from calc.sphere import Sphere

from direction_analysis.helpers.common_functions import extract_date, make_datetime
from direction_analysis.simplified_astro_model.directions_calc import all_directions
from direction_analysis.simplified_astro_model.params import ALLOWANCES


def get_intervals(sphere: Sphere) -> list[list[datetime]]:
    """Returns the action intervals of the directions"""
    intervals = []
    for direction in all_directions(sphere):
        year, month, day = extract_date(direction['date'])

        intervals.append([
            datetime(year, month, day) +
            timedelta(days=30 * ALLOWANCES[0]),
            datetime(year, month, day) +
            timedelta(days=30 * ALLOWANCES[1]),
        ])
    intervals.sort(key=lambda x: x[0])

    return intervals


def merge_intervals(sphere: Sphere) -> list[list[datetime]]:
    """Unites the action intervals of the directions"""
    intervals = get_intervals(sphere)
    if not intervals:
        return []
    merged = []
    current_start, current_end = intervals[0]

    for start, end in intervals[1:]:
        if start <= current_end:
            # The intervals overlap; we merge them.
            current_end = max(current_end, end)
        else:
            # The intervals do not overlap; we keep the current one and start a new one
            merged.append([current_start, current_end])
            current_start, current_end = start, end

    merged.append([current_start, current_end])
    return merged


def shorten_intervals(sphere: Sphere,
                      birth_date: str,
                      death_date: str) -> list[list[datetime]]:
    """
    Reduces the number of action intervals of the directions,
    taking life duration into account.
    """
    intervals = merge_intervals(sphere)
    b_date = make_datetime(birth_date)
    d_date = make_datetime(death_date)

    # We limit the list of intervals to the duration of life.
    shortened_list = []
    for item in intervals:
        if item[0] > d_date:
            continue

        if item[0] < b_date:
            item[0] = b_date
        if item[1] > d_date:
            item[1] = d_date

        shortened_list.append(item)

    return shortened_list


# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# Usage example:
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
if __name__ == '__main__':
    from direction_analysis.probability_assessment import person_data
    from direction_analysis.simplified_astro_model.example_chart import (
        build_sphere,
        load_person,
    )

    person = load_person()
    sphere = build_sphere(person)

    intervals = shorten_intervals(
        sphere,
        person['chartData']['date'],
        person['death']
    )
    for interval in intervals:
        print(interval)

    print(
        'Total action length',
        person_data.total_action_length(intervals),
        'of', person_data.life_len(person)
    )

    print('event date', person_data.extract_event_date(person['events']))
    print(
        'Is event in interval:',
        person_data.is_event_in_interval(person['events'], intervals)
    )
