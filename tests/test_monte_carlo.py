"""Tests of the vectorized Monte-Carlo p-value estimation (CPU path)."""

import numpy as np

from stat_analysis.helpers.monte_carlo import monte_carlo_p_value_vectorized


def test_monte_carlo_p_value_frozen() -> None:
    """A small synthetic case with a frozen expected p-value (seed 42).

    The test runs on the CPU path explicitly (numpy generator),
    so the expected value is backend-independent.
    """
    p0_sample = np.array([0.1, 0.2, 0.3, 0.5])
    rng = np.random.default_rng(42)

    p_value = monte_carlo_p_value_vectorized(
        p0_sample=p0_sample,
        s_obs=2,
        n_simulations=1000,
        random_generator=rng,
    )

    assert p_value == 0.297


def test_monte_carlo_p_value_deterministic() -> None:
    """The same seed reproduces the same p-value."""
    p0_sample = np.array([0.1, 0.2, 0.3, 0.5])

    p_first = monte_carlo_p_value_vectorized(
        p0_sample=p0_sample,
        s_obs=2,
        n_simulations=500,
        random_generator=np.random.default_rng(42),
    )
    p_second = monte_carlo_p_value_vectorized(
        p0_sample=p0_sample,
        s_obs=2,
        n_simulations=500,
        random_generator=np.random.default_rng(42),
    )

    assert p_first == p_second


def test_monte_carlo_extremes() -> None:
    """S_obs above every simulated outcome gives p = 0 and vice versa."""
    p0_sample = np.array([0.0, 0.0, 0.0])
    rng = np.random.default_rng(42)

    assert monte_carlo_p_value_vectorized(
        p0_sample, s_obs=1, n_simulations=100,
        random_generator=rng) == 0.0

    assert monte_carlo_p_value_vectorized(
        p0_sample, s_obs=0, n_simulations=100,
        random_generator=rng) == 1.0
