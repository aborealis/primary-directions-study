"""
Data of an individual horoscope for point-specific directions analysis.

Provides the example chart used by the ``__main__`` usage examples of
the simplified astrological model modules. Importing this module has no
side effects: the chart is loaded and the sphere is built only when
``load_person()`` and ``build_sphere()`` are called.

Requires the proprietary ``calc`` computation engine, which is not
distributed with this repository; without it this module cannot be used.
"""
import json
import os
from datetime import datetime

import calc.helpers.time as tm
from calc.sphere import Sphere

from direction_analysis.helpers.common_functions import extract_date, extract_time

# === Settings ====
FILE_TO_READ = "sample-100-violent-death-public.json"

# Repository root (this file lives in direction_analysis/simplified_astro_model/).
REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_person(filename: str = FILE_TO_READ) -> dict:
    """Loads the first (example) chart record from the sample file"""
    input_file = os.path.join(REPO_ROOT, 'samples', filename)
    with open(input_file, encoding='utf-8') as f_in:
        data = json.load(f_in)

    return data[0]


def build_sphere(person: dict) -> Sphere:
    """Constructs the celestial sphere from the person's birth data"""
    year, month, day = extract_date(person['chartData']['date'])
    hour, minute = extract_time(person['chartData']['time'])

    return Sphere(
        localtime=tm.LocalTime(tm.ModernStyle(
            naive_datetime=datetime(year, month, day, hour, minute),
            time_zone_hrs=person['chartData']['tz_hr'],
            geo_lon=person['chartData']['lon'],
        )),
        geo_lat=person['chartData']['lat'],
    )


def main() -> None:
    """Prints the name of the example chart"""
    person = load_person()
    print('\033[1;33mExample chart:\033[0m', person['name'])


if __name__ == '__main__':
    main()
