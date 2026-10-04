"""Vectorized Monte-Carlo estimation of the p-value under the null hypothesis."""

from typing import Any

from stat_analysis.helpers.array_backend import Array, RandomGenerator, get_array_module

# Array computation backend (cupy or numpy) selected by the USE_GPU setting.
np: Any = get_array_module()


def monte_carlo_p_value_vectorized(p0_sample: Array,
                                   s_obs: int,
                                   n_simulations: int = 10000,
                                   random_generator: RandomGenerator | None = None
                                   ) -> float:
    """
    Vectorized version of Monte Carlo p-value calculation.

    Simulates ``n_simulations`` outcomes of the null hypothesis (the
    death is random), each with the per-chart probabilities ``p0_sample``,
    and returns the fraction of simulations in which the total number
    of events S0 reaches the observed ``s_obs``.
    """
    # A local alias for the generator: the ternary folds the Optional away
    # in a way both mypy and pyright narrow to a non-optional type.
    rng = random_generator if random_generator is not None else np.random.default_rng()

    k = len(p0_sample)

    # Step 1: Simulate all Monte Carlo iterations at once
    r_matrix = rng.uniform(
        0, 1, (n_simulations, k)
    )

    # Step 1: Simulate outcomes under H0 for all iterations
    y0_matrix = (r_matrix <= p0_sample).astype(int)
    s0_values = np.sum(y0_matrix, axis=1)

    # Step 2: Count cases where S0 >= S_obs
    count_extreme = np.sum(s0_values >= s_obs)

    # Step 3: Calculate p-value. float() works on both backends: on a
    # 0-dimensional cupy array it synchronizes and moves the scalar to
    # the host, just like .get() would.
    return float(count_extreme / n_simulations)
