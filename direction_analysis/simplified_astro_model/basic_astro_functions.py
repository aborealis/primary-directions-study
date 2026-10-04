"""List of functions for the analysis of directions

Requires the proprietary ``calc`` computation engine, which is not
distributed with this repository; without it this module cannot be used.
"""

import calc.natal.directions as dirs
from calc.helpers.common import min_distance
from calc.sphere import Sphere

from direction_analysis.simplified_astro_model.params import (
    BRIGHTNESS,
    HOUSE,
    IS_EVENT_FAVORABLE,
    NATURAL_RULER,
)

ORBS = [18, 12, 8, 13, 6.5, 8, 7]
MALEFIC_PLANETS = [4, 6]
MALEFIC_ASPECTS = [-90, 90, 180]

# fmt: off
DIGNITIES = [
    # Ar Tau Gem Can Leo Vir Lib Sco Sag Cap Aqu Pis
    [ 4,  0,  0,  0,  5,  0, -4,  0,  0,  0, -5,  0],  # Sun
    [ 0,  4,  0,  5,  0,  0,  0, -4,  0, -5,  0,  0],  # Moon
    [ 0,  0,  5,  0,  0,  5,  0,  0, -5,  0,  0, -5],  # Mer
    [-5,  5,  0,  0,  0, -4,  5, -5,  0,  0,  0,  4],  # Ven
    [ 5, -5,  0, -4,  0,  0, -5,  5,  0,  4,  0,  2],  # Mar
    [ 0,  0, -5,  4,  0, -5,  0,  0,  5, -4,  0,  5],  # Jup
    [-4,  0,  0, -5, -5,  0,  4,  0,  0,  5,  5,  0],  # Sat
]
# fmt: on


def assess_state(planet_num: int, degree: float) -> int:
    """Evaluates the planet’s celestial state at the given degree in points"""
    sign = int(degree // 30)
    return DIGNITIES[planet_num][sign]


def assess_aspect(sphere: Sphere, planet_num: int, aspect: int) -> int:
    """Evaluates the beneficence of a planet’s aspect in points"""
    planet_degree = sphere.planets[planet_num].vector.ecliptical.lon
    aspect_degree = (planet_degree + aspect) % 360

    # Celestial state of the planet
    score = assess_state(planet_num, planet_degree)

    if aspect == 0:
        return score

    # Modification of the celestial state by the form of aspect
    if aspect in MALEFIC_ASPECTS and score > 0:
        score = 0
    elif aspect not in MALEFIC_ASPECTS and score < 0:
        score = 0

    return score + assess_state(planet_num, aspect_degree)


def aspects_to_cusp(sphere: Sphere,
                    house: int = HOUSE,
                    is_favorable: bool = IS_EVENT_FAVORABLE) -> list[dict]:
    """
    Returns zodiacal aspects of the planets to the cusp of the i-th house,
    where i = 0..11. Returns the neutral-favorable aspects for the favorable
    event and neutral-unfavorable aspects for the unfavorable one.
    """
    aspects = []

    for p in range(7):
        planet_lon = sphere.planets[p].vector.ecliptical.lon
        cusp_lon = sphere.cusps_regio[house].vector.ecliptical.lon
        for a in [-120, -90, -60, 0, 60, 90, 180]:
            aspect_degree = (planet_lon + a) % 360
            distance = min_distance(aspect_degree, cusp_lon)
            if distance <= ORBS[p] * 1:
                aspect_score = assess_aspect(sphere, p, a)

                # always consider aspects from the natural ruler of the house.
                # The malefic exception of the paper is applied here, for
                # zodiacal aspects to the house cusp, to Mars alone — the
                # natural ruler of violent death; the aspects of the remaining
                # planets are filtered by their score (see the malefic
                # exception note in README Section 3).
                if p == NATURAL_RULER:
                    use_aspect = True
                elif is_favorable:
                    # neutral-favorable aspects
                    use_aspect = aspect_score >= 0
                else:
                    # neutral-unfavorable aspects
                    use_aspect = aspect_score <= 0

                if use_aspect:
                    aspects.append({
                        'planet': p,
                        'aspect': a,
                        'score': aspect_score
                    })

    return aspects


def planet_in_house(sphere: Sphere, house_num: int = HOUSE) -> list[int]:
    """
    Determines the planets in a house (taking into account
    the mundane distance from the cusp)
    """
    # right ascension, RA
    cusp_mund_pos: float = dirs.mundpos_regio(
        sphere,
        sphere.cusps_regio[house_num].vector
    )

    conjunctions = []
    in_house = []

    for p in range(7):
        # right ascension, RA
        planet_mund_pos: float = dirs.mundpos_regio(
            sphere,
            sphere.planets[p].vector
        )

        # If a planet is closely conjunct the cusp (even if it is in the previous
        # house), we consider that planet to be partially determined by that house.
        if min_distance(cusp_mund_pos, planet_mund_pos) < ORBS[p] * 0.5:
            conjunctions.append(p)

        from_cusp = (planet_mund_pos - cusp_mund_pos) % 360
        to_next_cusp = (cusp_mund_pos + 30 - planet_mund_pos) % 360

        # If a planet's mudnade position is in the current primary house...
        if from_cusp + to_next_cusp - 30 < 1e-4:
            # ...and if it is not at the very end of that house
            if to_next_cusp > 3:
                in_house.append(p)

    result = [*in_house, *conjunctions]
    return list(set(result))


def house_rulers(sphere: Sphere, house_num: int,
                 ignore_exaltation: bool = False) -> list[int]:
    """Returns the list of house-ruler planets by sign/exaltation"""
    sign = int(sphere.cusps_regio[house_num].vector.ecliptical.lon // 30)
    scores = [5] if ignore_exaltation else [4, 5]

    result = []
    for p in range(7):
        if DIGNITIES[p][sign] in scores:
            result.append(p)

    return result


def house_coruler(sphere: Sphere, house_num: int) -> int | None:
    """Returns the co-ruler of the house based on the nearest intercepted sign"""
    sign = int(sphere.cusps_regio[house_num].vector.ecliptical.lon // 30)
    next_sign = (sign + 1) % 12

    cusp_mund_pos = dirs.mundpos_regio(
        sphere,
        sphere.cusps_regio[house_num].vector
    )

    next_sign_mund_pos = dirs.mundpos_regio(
        sphere,
        sphere.set_ecliptical(lon=next_sign * 30, lat=0)
    )

    from_cusp = (next_sign_mund_pos - cusp_mund_pos) % 360
    to_next_cusp = (cusp_mund_pos + 30 - next_sign_mund_pos) % 360

    # If the next sign begins within the house (in the mundane sense)
    # and if the sign occupies at least 10 mundane degrees...
    if from_cusp + to_next_cusp - 30 < 1e-4 and to_next_cusp > 10:
        # ...then we calculate the ruler of that intercepted sign
        for p in range(7):
            if DIGNITIES[p][next_sign] == 5:
                return p

    return None


def fav_unfav_aspects(sphere: Sphere,
                      planet_num: int,
                      min_score: int = BRIGHTNESS,
                      is_favorable: bool = IS_EVENT_FAVORABLE) -> list[dict]:
    """Returns a list of [un]favorable aspects of the planet"""
    aspects = []
    for a in [-120, -90, -60, 0, 60, 90, 120, 180]:
        score = assess_aspect(sphere, planet_num, a)
        if is_favorable:
            condition = score >= min_score
        else:
            condition = score <= -min_score
        if condition:
            aspects.append({
                'planet': planet_num,
                'aspect': a,
                'score': score,
            })
    return aspects


# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# Usage examples:
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
if __name__ == '__main__':
    from direction_analysis.simplified_astro_model.example_chart import (
        build_sphere,
        load_person,
    )

    sample_sphere = build_sphere(load_person())
    print('Planets in 10th:', planet_in_house(sample_sphere, house_num=9))
    print('Rulers of the 2nd:', house_rulers(sample_sphere, house_num=1))
    print('Co-ruler of the 5th:', house_coruler(sample_sphere, house_num=4))
    print('Fav. aspects to 3rd:', aspects_to_cusp(sample_sphere, 2, True))
    print('Unfav. aspects to 3rd:', aspects_to_cusp(sample_sphere, 2, False))
    print('Fav. aspects of Venus:', fav_unfav_aspects(sample_sphere, 3, True))
    print('Unfav. aspects of Venus:', fav_unfav_aspects(sample_sphere, 3, False))
