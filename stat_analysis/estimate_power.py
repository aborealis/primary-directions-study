"""
Type II Error Control — Statistical Power Analysis (Monte Carlo, vectorized)
"""
import argparse
import os
import sys
from typing import Any

import matplotlib.pyplot as plt

# Allow running this script directly (python stat_analysis/estimate_power.py)
# in addition to the module form (python -m stat_analysis.estimate_power).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stat_analysis.helpers.array_backend import (
    Array,
    RandomGenerator,
    get_array_module,
    gpu_active,
)
from stat_analysis.helpers.data_loading import load_p0_y
from stat_analysis.helpers.monte_carlo import monte_carlo_p_value_vectorized
from stat_analysis.helpers.type_annotation import PowerConfig

# === Settings ===
FILE_TO_READ = 'p0_y-100-fixed.txt'

# Estimated relative risk from bootstrap analysis
R_ESTIMATE = 1.15
CONFIG = PowerConfig(
    # k = 100, 200, 300, ... as described in Appendix 4 of the paper;
    # the loop stops at the first k reaching the 80% power target (k = 400)
    sample_sizes=list(range(100, 1001, 100)),
    n_simulations=10000,
    n_monte_carlo=10000,
    alpha=0.05,
    random_seed=42,
    verbose=True
)

# Array computation backend (cupy or numpy) selected by the USE_GPU setting,
# and whether it actually runs on the GPU (backend-specific code must branch
# on this flag, not on the USE_GPU intention — see array_backend).
np: Any = get_array_module()
ON_GPU = gpu_active()


def bootstrap_indices(rng: RandomGenerator, n_pilot: int, k: int) -> Array:
    """Generate bootstrap indices. The cupy Generator has no choice(), so
    on the GPU the same draws are made with integers()."""
    if ON_GPU:
        return rng.integers(0, n_pilot, size=k)
    return rng.choice(n_pilot, size=k, replace=True)


def simulate_h1(rng: RandomGenerator, p1: Array) -> int:
    """Simulate Bernoulli outcomes under alternative hypothesis. int() works
    on both backends: on a 0-dimensional cupy array it synchronizes."""
    outcomes = (rng.uniform(0, 1, size=len(p1)) <= p1).astype(int)
    return int(np.sum(outcomes))


def calculate_power_vectorized(p0_list: list[float],
                               r_estimate: float,
                               config: PowerConfig | None = None,
                               ) -> dict[int, float]:
    """
    Statistical power estimation using vectorized Monte Carlo approach.
    """
    if config is None:
        config = PowerConfig()

    rng = np.random.default_rng(config.random_seed)

    # Prepare pilot probabilities
    p0 = np.asarray(p0_list)
    p1 = np.minimum(r_estimate * p0, 1.0)
    n_pilot = len(p0)

    # Default sample sizes
    sample_sizes = config.sample_sizes or list(range(100, 1001, 100))

    power_results = {}

    if config.verbose:
        print("Calculating statistical power...")
        print("Sample Size | Power (%)")
        print("-" * 24)

    for k in sample_sizes:
        significant = 0

        for _ in range(config.n_simulations):

            # Bootstrap sampling
            idx = bootstrap_indices(rng, n_pilot, k)
            p0_sample = p0[idx]
            p1_sample = p1[idx]

            # Simulated statistic under H1
            s_obs = simulate_h1(rng, p1_sample)

            # Monte-Carlo p-value
            p_value = monte_carlo_p_value_vectorized(
                p0_sample,
                s_obs,
                config.n_monte_carlo,
                rng
            )

            significant += (p_value <= config.alpha)

        power = significant / config.n_simulations
        power_results[k] = power

        if config.verbose:
            print(f"{k:11d} | {power * 100:6.1f}%")

        if power >= 0.80:
            if config.verbose:
                print(f"✓ Target power reached at k = {k}")
            break

    return power_results


def find_min_sample_size(power_results: dict[int, float]) -> int:
    """Find minimum sample size for 80% power"""
    for k, power in power_results.items():
        if power >= 0.80:
            return k
    return 0


def print_summary(power_results: dict[int, float],
                  r_estimate: float,
                  p0_list: list[float]) -> None:
    """Prints summary"""
    min_sample_size = find_min_sample_size(power_results)
    sample_sizes = list(power_results.keys())

    print("\n" + "=" * 50)
    print("POWER ANALYSIS SUMMARY")
    print("=" * 50)
    print(f"Pilot relative risk (r): {r_estimate:.3f}")
    print(f"Pilot sample size: {len(p0_list)}")
    if min_sample_size:
        print(f"Minimum sample size for 80% power: {min_sample_size}")
        print(f"Achieved power at k={min_sample_size}: "
              f"{power_results[min_sample_size] * 100:.1f}%")
    else:
        print(
            f"Target power not reached. Maximum tested: k={max(sample_sizes)}")
        print(f"Power at k={max(sample_sizes)}: "
              f"{power_results[max(sample_sizes)] * 100:.1f}%")


def plot_power(power_results: dict[int, float]) -> None:
    """
    Create a plot for power analysis results
    """
    # Create figure with two subplots: table and graph
    _, ax_plot = plt.subplots(1, 1, figsize=(12, 6))

    # Prepare data
    sample_sizes = list(power_results.keys())
    powers = [power_results[k] * 100 for k in sample_sizes]

    # Create power curve plot
    ax_plot.plot(sample_sizes, powers, 'o-', linewidth=3, markersize=8,
                 color='#2E86AB', markerfacecolor='#A23B72')

    # Add target power line
    ax_plot.axhline(y=80, color='red', linestyle='--', alpha=0.7,
                    linewidth=2, label='80% Power Target')

    # Find and mark minimum sample size for 80% power
    min_sample_size = find_min_sample_size(power_results)
    ax_plot.axvline(x=min_sample_size, color='green', linestyle=':', alpha=0.7,
                    linewidth=2, label=f'Minimum n = {min_sample_size}')

    # Style the plot
    ax_plot.set_xlabel('Sample Size (k)', fontsize=12, fontweight='bold')
    ax_plot.set_ylabel('Statistical Power (%)', fontsize=12, fontweight='bold')
    ax_plot.set_title('Power Analysis: Sample Size vs Statistical Power',
                      fontsize=14, fontweight='bold')
    ax_plot.grid(True, alpha=0.3)
    ax_plot.legend(fontsize=10)
    ax_plot.set_ylim(0, 100)

    # Add value annotations on plot points
    for k, power in zip(sample_sizes, powers, strict=False):
        ax_plot.annotate(f'{power:.1f}%', (k, power),
                         textcoords="offset points", xytext=(0, 10),
                         ha='center', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.show()


def main() -> None:
    """Runs the power analysis from the command line."""
    parser = argparse.ArgumentParser(
        description='Monte-Carlo statistical power analysis '
                    '(Type II error control)')
    parser.add_argument(
        '--plot', action='store_true',
        help='Show a plot of the power curve after the analysis')
    args = parser.parse_args()

    p0_pilot, _y_pilot = load_p0_y(FILE_TO_READ)
    print(f"Successfully loaded {len(p0_pilot)} data points from file")

    power_results = calculate_power_vectorized(
        p0_list=p0_pilot,
        r_estimate=R_ESTIMATE,
        config=CONFIG,
    )

    print_summary(power_results, R_ESTIMATE, p0_pilot)

    if args.plot:
        plot_power(power_results)


if __name__ == '__main__':
    main()
