"""Tests of the published sample files."""

import json
from pathlib import Path

# Repository root (this file lives in tests/).
REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLES_DIR = REPO_ROOT / 'samples'

# The published sample sizes: pilot, final, and the full pool
EXPECTED_SIZES = {'100': 100, '400': 400, 'max': 1102}

# Titles of the violent-death event categories
ALLOWED_CATEGORY_TITLES = {'Death by Accident', 'Death by Homicide'}


def load_sample(size: str) -> list[dict]:
    path = SAMPLES_DIR / f'sample-{size}-violent-death-public.json'
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def test_public_sample_sizes() -> None:
    for size, expected in EXPECTED_SIZES.items():
        assert len(load_sample(size)) == expected, size


def test_public_sample_unique_charts() -> None:
    for size in EXPECTED_SIZES:
        keys = [(person['name'], person['chartData']['date'],
                 person['chartData']['time']) for person in load_sample(size)]
        assert len(keys) == len(set(keys)), size


def test_public_samples_exact_schema() -> None:
    """The published schema carries exactly the fields used by the study."""
    for size in EXPECTED_SIZES:
        for person in load_sample(size):
            assert set(person) == {'name', 'chartData', 'death', 'events'}, size


def test_public_samples_event_categories() -> None:
    """Events carry only the category title and date; the numeric
    category identifier is not part of the published samples."""
    for size in EXPECTED_SIZES:
        for person in load_sample(size):
            for event in person['events']:
                assert event['category'] in ALLOWED_CATEGORY_TITLES, size
                assert set(event) == {'category', 'date'}, size
