"""Calculates promissors and significators of the given house

Requires the proprietary ``calc`` computation engine, which is not
distributed with this repository; without it this module cannot be used.
"""

import calc.natal.directions as dirs
from calc.sphere import Sphere

import direction_analysis.simplified_astro_model.basic_astro_functions as bs
from direction_analysis.helpers.type_annotations_runtime import (
    PromissorDict,
    SignificatorDict,
)
from direction_analysis.simplified_astro_model.params import (
    BRIGHTNESS,
    HOUSE,
    IS_EVENT_FAVORABLE,
    NATURAL_RULER,
)

PLANETS = ['Sun', 'Mon', 'Mer', 'Ven', 'Mar', 'Jup', 'Sat']


def promissors_by_aspects(sphere: Sphere,
                          house_num: int = HOUSE,
                          is_favorable: bool = IS_EVENT_FAVORABLE) -> list[int]:
    """Returns the planets whose [un]favorable aspects fall
    on the cusp of the i-th house"""
    aspects = bs.aspects_to_cusp(sphere, house_num, is_favorable)
    return [item['planet'] for item in aspects]


def promissors_by_position(sphere: Sphere, house_num: int = HOUSE) -> list[int]:
    """Returns a list of planets in the i-th house and its opposite house"""
    return (bs.planet_in_house(sphere, house_num)
            + bs.planet_in_house(sphere, (house_num + 6) % 12))


def promissors_by_rulership(sphere: Sphere, house_num: int = HOUSE) -> list[int]:
    """Returns a list of the major rulers of the i-th cusp"""
    return bs.house_rulers(sphere, house_num)


def promissors_by_corulership(sphere: Sphere, house_num: int = HOUSE) -> list[int]:
    """Returns a list of the co-rulers of the i-th house"""
    co_ruler = bs.house_coruler(sphere, house_num)
    if co_ruler is None:
        return []

    return [co_ruler]


def planets_for_promissors(sphere: Sphere,
                           house_num: int = HOUSE,
                           is_favorable: bool = IS_EVENT_FAVORABLE,
                           natural_ruler: int | None = NATURAL_RULER,
                           of_life_and_activity: bool = False) -> list[int]:
    """
    Returns a list of planets whose aspects and antiscia will
    form the promissors of the event
    """
    planets = [
        *promissors_by_position(sphere, house_num),
        *promissors_by_rulership(sphere, house_num),
    ]

    if not of_life_and_activity:
        planets = [
            *planets,
            *promissors_by_aspects(sphere, house_num, is_favorable),
            *promissors_by_corulership(sphere, house_num),
        ]

    if natural_ruler is not None:
        planets.append(natural_ruler)

    return list(set(planets))


def search_aspects(sphere: Sphere,
                   planets: list[int],
                   is_favorable: bool = IS_EVENT_FAVORABLE,
                   ) -> list[PromissorDict]:
    """
    Searches for [un]favorable aspects of the given planets
    """
    promissors = []
    for p in planets:
        promissors += bs.fav_unfav_aspects(sphere, p, is_favorable)

    result: list[PromissorDict] = []
    for item in promissors:
        planet = item['planet']
        aspect = item['aspect']
        score = item['score']

        # Remove dim promissors
        if abs(score) < abs(BRIGHTNESS):
            continue

        mundane_aspects = dirs.aspects_on_circle(sphere, planet)
        aspect_vector = [
            a for a in mundane_aspects
            if a.name == aspect
        ][0].vector

        result.append({
            'object': f'{PLANETS[planet]} aspect:{aspect}',
            'vector': aspect_vector,
            'score': score
        })

    return result


def search_antiscia(sphere: Sphere,
                    planets: list[int],
                    is_favorable: bool = IS_EVENT_FAVORABLE,
                    ) -> list[PromissorDict]:
    """
    Searches for [un]favorable antiscia of the given planets
    """
    result: list[PromissorDict] = []
    for p in planets:
        for dist in ['far', 'close']:
            antiscion = dirs.mund_antis_by_name(
                sphere, planet_num=p, is_closest=dist == 'close'
            )

            if antiscion:
                score_planet = bs.assess_state(
                    p, sphere.planets[p].vector.ecliptical.lon)
                intrinsic_state = -1 if p in bs.MALEFIC_PLANETS else 1

                if dist == 'far':
                    score_antis = bs.assess_state(
                        p, antiscion.ecliptical.lon
                    )
                else:
                    score_antis = 0

                score = score_planet + intrinsic_state + score_antis
                # Remove non bright promissors
                if abs(score) < abs(BRIGHTNESS) and p not in bs.MALEFIC_PLANETS:
                    continue

                if (
                    (is_favorable and score < 0) or
                    (not is_favorable and score > 0)
                ):
                    continue

                result.append({
                    'object': f'{PLANETS[p]} {dist} antiscion',
                    'vector': antiscion,
                    'score': score,
                })

    return result


def all_promissors(sphere: Sphere,
                   house_num: int = HOUSE,
                   is_favorable: bool = IS_EVENT_FAVORABLE,
                   natural_ruler: int | None = NATURAL_RULER,
                   of_life_and_activity: bool = False) -> list[PromissorDict]:
    """
    Returns a list of all possible promissors of the event in the given house,
    or the promissors of life and activity
    """
    planets = planets_for_promissors(
        sphere, house_num, is_favorable,
        natural_ruler, of_life_and_activity
    )

    return [
        *search_aspects(sphere, planets, is_favorable),
        *search_antiscia(sphere, planets, is_favorable),
    ]


def all_significators(sphere: Sphere,
                      house_num: int,
                      natural_ruler: int | None = NATURAL_RULER
                      ) -> list[SignificatorDict]:
    """Returns a list of the house significators"""
    planets = [
        *bs.planet_in_house(sphere, house_num),
        *bs.house_rulers(sphere, house_num, ignore_exaltation=True),
    ]

    if natural_ruler is not None:
        planets.append(natural_ruler)

    planets = list(set(planets))

    significators: list[SignificatorDict] = []
    for p in planets:
        significators.append({
            'object': PLANETS[p],
            'vector': sphere.planets[p].vector
        })

    significators.append({
        'object': f'cusp {house_num + 1}',
        'vector': sphere.cusps_regio[house_num].vector
    })

    return significators


# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# Usage example:
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
if __name__ == '__main__':
    from direction_analysis.simplified_astro_model.example_chart import (
        build_sphere,
        load_person,
    )

    sample_sphere = build_sphere(load_person())
    PREFIX = "" if IS_EVENT_FAVORABLE else "un"
    print(f'All {PREFIX}favorable promissors of the {HOUSE + 1} house:')
    for prom in all_promissors(sample_sphere, HOUSE, IS_EVENT_FAVORABLE):
        print(prom)

    print(f'All significators of the {HOUSE + 1} house:')
    for signif in all_significators(sample_sphere, house_num=HOUSE):
        print(signif)
