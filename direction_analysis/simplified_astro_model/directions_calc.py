"""Calculates the directions of all promissors to all significators

Requires the proprietary ``calc`` computation engine, which is not
distributed with this repository; without it this module cannot be used.
"""
from datetime import timedelta

import calc.natal.directions as dirs
from calc.sphere import Sphere

import direction_analysis.helpers.type_annotations_runtime as tp
from direction_analysis.helpers.common_functions import make_datetime
from direction_analysis.simplified_astro_model.params import HOUSE
from direction_analysis.simplified_astro_model.promissors_significators import (
    all_promissors,
    all_significators,
)


def arc_to_years(arc: float) -> float:
    """
    Converts the directed arc (in degrees) to the age in years at which
    the direction perfects, rounded to one decimal place for display.

    The Naibod rate is used: one degree of the directed arc corresponds
    to one year of life. The float expression below is exactly the one
    used to generate the study data; it must not be rewritten
    algebraically.
    """
    return int(arc * 365.24 / 360 * 10) / 10


def arc_to_timeline(arc: float) -> timedelta:
    """
    Converts the directed arc (in degrees) to the time span between the
    birth moment and the perfection of the direction.

    The Naibod rate is used: one degree of the directed arc corresponds
    to one year of life. The float expression below is exactly the one
    used to generate the study data; it must not be rewritten
    algebraically.
    """
    return timedelta(days=365.24 * arc * 365.24 / 360)


def calc_single_direction(sphere: Sphere,
                          promissor: tp.PromissorDict,
                          significator: tp.SignificatorDict
                          ) -> tp.DirectionDict | None:
    """
    Calculates direction between the specified promissor
    and significator
    """

    # Directionsl arc
    arc_dict: tp.DirectionArcDict | None = dirs.directions_regio(
        sphere, promissor['vector'], significator['vector']
    )

    if arc_dict is None:
        return None

    arc: float = arc_dict['arc']
    time = (
        sphere.localtime.datetime_from_jday_utc(sphere.julian_day)
        + arc_to_timeline(arc)
    )

    return {
        'sign': significator['object'],
        'prom': promissor['object'],
        'year': arc_to_years(arc),
        'date': time.strftime("%Y/%m/%d"),
    }


def calc_directions(sphere: Sphere,
                    promissors: list[tp.PromissorDict],
                    significators: list[tp.SignificatorDict]
                    ) -> list[tp.DirectionDict]:
    """
    Calculates all directions between the specified promissors
    and significators
    """
    directions = []
    for proms in promissors:
        for signif in significators:
            direction_dict = calc_single_direction(
                sphere, proms, signif
            )

            if direction_dict is None:
                continue

            directions.append(direction_dict)

    return directions


def directions_to_house(sphere: Sphere) -> list[tp.DirectionDict]:
    """
    Returns the directions of the event’s promissors to
    the house significators
    """
    promissors = all_promissors(sphere, HOUSE)
    significators = all_significators(sphere, HOUSE)

    return calc_directions(sphere, promissors, significators)


def directions_to_life_and_activity(sphere: Sphere) -> list[tp.DirectionDict]:
    """
    Returns the directions of the event’s promissors to the significators
    of the 1st and 10th houses
    """
    promissors = all_promissors(sphere, HOUSE)
    signif_life = all_significators(sphere, house_num=0, natural_ruler=None)
    directions_to_life = calc_directions(sphere, promissors, signif_life)

    signif_activity = all_significators(
        sphere,
        house_num=9,
        natural_ruler=None
    )
    directions_to_activity = calc_directions(
        sphere,
        promissors,
        signif_activity
    )

    return directions_to_life + directions_to_activity


def directions_of_life_and_activity(sphere: Sphere) -> list[tp.DirectionDict]:
    """
    Returns the directions of the promissors of life and activity to the
    significators of the house in question
    """
    significators = all_significators(sphere, HOUSE)
    proms_life = all_promissors(
        sphere, 0, natural_ruler=None, of_life_and_activity=True
    )
    directions_of_life = calc_directions(
        sphere, proms_life, significators
    )

    proms_activity = all_promissors(
        sphere, 9, natural_ruler=None, of_life_and_activity=True
    )
    directions_of_activity = calc_directions(
        sphere, proms_activity, significators
    )

    return directions_of_life + directions_of_activity


def all_directions(sphere: Sphere) -> list[tp.DirectionDict]:
    """Returns all possible directions of all promissors to all significators"""
    directions = (
        directions_to_house(sphere)
        + directions_to_life_and_activity(sphere)
        + directions_of_life_and_activity(sphere)
    )

    uniques = []
    result = []
    for d in directions:
        if d['date'] in uniques:
            continue
        uniques.append(d['date'])
        result.append(d)

    return result


# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# Usage Examples:
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
if __name__ == '__main__':
    from direction_analysis.simplified_astro_model.example_chart import (
        build_sphere,
        load_person,
    )

    person = load_person()
    sample_sphere = build_sphere(person)
    print(f'All directions for {HOUSE + 1} house in question:')
    for direction in all_directions(sample_sphere):
        if make_datetime(direction['date']) < make_datetime(person['death']):
            print(direction)
