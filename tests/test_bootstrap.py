"""Tests of the bootstrap relative-risk estimation on synthetic data."""

import pytest

from stat_analysis.estimate_r import bootstrap_relative_risk


def test_bootstrap_narrow_interval_uses_median() -> None:
    """With CI width below the 1.0 threshold the median is the estimate."""
    p0_list = [0.5] * 20
    y_list = [0, 1] * 10

    results = bootstrap_relative_risk(
        p0_list=p0_list,
        y_list=y_list,
        n_bootstrap=2000,
        random_seed=42,
    )

    assert results['estimate_type'] == 'median'
    assert results['point_estimate'] == pytest.approx(1.0)
    assert results['ci_lower'] == pytest.approx(0.6)
    assert results['ci_upper'] == pytest.approx(1.4)
    assert results['ci_width'] == pytest.approx(0.8)
    assert results['n_valid_bootstrap'] == 2000


def test_bootstrap_wide_interval_uses_lower_bound() -> None:
    """With CI width above the 1.0 threshold the lower bound is the
    conservative point estimate."""
    p0_list = [0.01] * 10 + [0.02] * 10
    y_list = [1] * 8 + [0] * 12

    results = bootstrap_relative_risk(
        p0_list=p0_list,
        y_list=y_list,
        n_bootstrap=2000,
        random_seed=42,
    )

    assert results['estimate_type'] == 'conservative (lower bound)'
    assert results['point_estimate'] == results['ci_lower']
    assert results['point_estimate'] == pytest.approx(11.428571428571425)
    assert results['ci_upper'] == pytest.approx(48.0)
    # The 1.0 threshold is crossed in this synthetic case
    assert results['ci_width'] > 1.0


def test_bootstrap_p1_estimates() -> None:
    """The per-chart p1 estimates are point_estimate * p0."""
    p0_list = [0.5] * 20
    y_list = [0, 1] * 10

    results = bootstrap_relative_risk(
        p0_list=p0_list,
        y_list=y_list,
        n_bootstrap=2000,
        random_seed=42,
    )

    assert results['p1_estimates'] == pytest.approx(
        [results['point_estimate'] * p0 for p0 in p0_list])
