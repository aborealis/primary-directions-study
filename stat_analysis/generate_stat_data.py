"""
Generates statistical data for analysis — p0: the probability
of a random event on the primary direction, and y = {0,1}: the
actually observed or unobserved event on the primary direction.

Requires the proprietary astrological computation engine (the ``calc``
package), which is not distributed with this repository; without it
this script cannot be re-run and the published ``p0_y-*-fixed.txt``
data files are the reference output.
"""
import argparse
import json
import os
import sys
from datetime import datetime

# Allow running this script directly (python stat_analysis/generate_stat_data.py)
# in addition to the module form (python -m stat_analysis.generate_stat_data).
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

import calc.helpers.time as tm
from calc.sphere import Sphere
from tqdm import tqdm

import direction_analysis.probability_assessment.directions_intervals as di
import direction_analysis.probability_assessment.person_data as person_data
from direction_analysis.helpers.common_functions import extract_date, extract_time

# === Settings ===
DEFAULT_SAMPLE = 'sample-400-violent-death-public.json'
DEFAULT_OUTPUT = 'p0_y-400.txt'


def main() -> None:
    """Generates the p0_y data file for the given sample of charts."""
    parser = argparse.ArgumentParser(
        description='Generate p0/y statistical data from a sample file')
    parser.add_argument(
        '--sample', default=DEFAULT_SAMPLE,
        help=f'Sample file from the samples/ directory (default: {DEFAULT_SAMPLE})')
    parser.add_argument(
        '--output', default=DEFAULT_OUTPUT,
        help=f'Output file in the stat_analysis/ directory, or an absolute '
             f'path (default: {DEFAULT_OUTPUT})')
    args = parser.parse_args()

    # Relative paths are resolved inside the corresponding directories of
    # the repository, regardless of the current working directory.
    input_file = os.path.join(REPO_ROOT, 'samples', args.sample)
    output_file = os.path.join(REPO_ROOT, 'stat_analysis', args.output)

    with open(input_file, encoding='utf-8') as f_in:
        persons = json.load(f_in)

    total_success = 0
    total_p0 = 0.0

    with open(output_file, 'w', encoding='utf-8') as f_out:
        for person in tqdm(persons, desc="Processing", unit="rows"):
            year, month, day = extract_date(person['chartData']['date'])
            hour, minute = extract_time(person['chartData']['time'])
            sphere = Sphere(
                localtime=tm.LocalTime(tm.ModernStyle(
                    naive_datetime=datetime(year, month, day, hour, minute),
                    time_zone_hrs=person['chartData']['tz_hr'],
                    geo_lon=person['chartData']['lon'],
                )),
                geo_lat=person['chartData']['lat'],
            )

            intervals = di.shorten_intervals(
                sphere,
                person['chartData']['date'],
                person['death']
            )
            y = person_data.is_event_in_interval(person['events'], intervals)

            # Total duration of the action intervals of directions
            # relative to lifespan
            p0 = (
                person_data.total_action_length(intervals)
                / person_data.life_len(person)
            )

            f_out.write(f'{p0}, {int(y)} \n')

            total_p0 += p0
            total_success += y

    print(f'Total success (real): {total_success}')
    print(f'Total success (H0): {total_p0}')


if __name__ == '__main__':
    main()
