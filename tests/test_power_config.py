"""Tests of the statistical power-analysis configuration."""

from stat_analysis.estimate_power import CONFIG, FILE_TO_READ, R_ESTIMATE
from stat_analysis.helpers.type_annotation import PowerConfig


def test_study_power_config() -> None:
    """The configuration reproduces Appendix 4 of the paper."""
    assert CONFIG.sample_sizes == list(range(100, 1001, 100))
    assert CONFIG.n_simulations == 10000
    assert CONFIG.n_monte_carlo == 10000
    assert CONFIG.alpha == 0.05
    assert CONFIG.random_seed == 42
    assert CONFIG.verbose is True
    # The a priori relative risk from the pilot bootstrap
    assert R_ESTIMATE == 1.15
    # The power analysis is based on the pilot data
    assert FILE_TO_READ == 'p0_y-100-fixed.txt'


def test_power_config_defaults() -> None:
    config = PowerConfig()

    assert config.sample_sizes is None
    assert config.n_simulations == 1000
    assert config.n_monte_carlo == 1000
    assert config.alpha == 0.05
    assert config.random_seed is None
    assert config.verbose is True
