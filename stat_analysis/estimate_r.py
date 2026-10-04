"""Estimates r — the relative risk — using the bootstrap estimation method."""
import argparse
import os
import sys
from typing import Any

import numpy as np
from tqdm import tqdm

# Allow running this script directly (python stat_analysis/estimate_r.py)
# in addition to the module form (python -m stat_analysis.estimate_r).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stat_analysis.helpers.data_loading import load_p0_y

# === Settings ===
# Defaults reproduce the pilot analysis from the paper (100 charts,
# 10,000 bootstrap repetitions → the a priori RR = 1.154).
FILE_TO_READ = 'p0_y-100-fixed.txt'
N_BOOTSTRAP = 10000
RANDOM_SEED = 42

# To reproduce the other bootstrap runs from the paper:
#   Control bootstrap on all available charts (Figure 3: 1,102 charts,
#   1,000,000 iterations):
#     python stat_analysis/estimate_r.py --file p0_y-max-fixed.txt --n-bootstrap 1000000
#   The final 400-chart sample:
#     python stat_analysis/estimate_r.py --file p0_y-400-fixed.txt


# === Main code ===
def bootstrap_relative_risk(p0_list: list[float],
                            y_list: list[int],
                            n_bootstrap: int = 10000,
                            random_seed: int | None = None) -> dict[str, Any]:
    """
    Estimates relative risk using bootstrap method

    Parameters:
    -----------
    p0_list : list[float]
        List of probabilities of random death on fatal directions
    y_list : list[int]
        List of observed outcomes (0 or 1)
    n_bootstrap : int
        Number of bootstrap repetitions
    random_seed : int, optional
        Seed for reproducibility

    Returns:
    --------
    dict : Analysis results
    """

    # Create random number generator
    if random_seed is not None:
        rng = np.random.default_rng(seed=random_seed)
    else:
        rng = np.random.default_rng()

    # Convert to numpy arrays for efficiency
    p0_array = np.array(p0_list)
    y_array = np.array(y_list)

    n_original = len(p0_array)

    # Storage for bootstrap estimates
    r_values = []

    for _ in tqdm(range(n_bootstrap), desc="Processing", unit="rows"):
        # Step 2: Create bootstrap sample
        indices = rng.choice(n_original, size=n_original, replace=True)

        p0_bootstrap = p0_array[indices]
        y_bootstrap = y_array[indices]

        # Calculate expected and observed counts
        E_S0 = np.sum(p0_bootstrap)
        S_OBS = np.sum(y_bootstrap)

        # Estimate relative risk (avoid division by zero)
        if E_S0 > 0:
            r = S_OBS / E_S0
        else:
            r = np.nan  # If E_S0 = 0, return NaN

        r_values.append(r)

    # Remove NaN values (if any)
    r_valid = np.array([r for r in r_values if not np.isnan(r)])

    # Step 3: Calculate percentiles
    r_2_5 = np.percentile(r_valid, 2.5)
    r_50 = np.percentile(r_valid, 50)  # Median
    r_97_5 = np.percentile(r_valid, 97.5)

    # Determine interval width
    ci_width = r_97_5 - r_2_5
    wide_interval_threshold = 1.0  # Threshold for "wide" interval

    # Select point estimate
    if ci_width > wide_interval_threshold:
        point_estimate = r_2_5  # Conservative estimate for wide interval
        estimate_type = "conservative (lower bound)"
    else:
        point_estimate = r_50   # Median for narrow interval
        estimate_type = "median"

    # Calculate p1_i for original data
    p1_original = point_estimate * p0_array

    results = {
        'point_estimate': point_estimate,
        'estimate_type': estimate_type,
        'ci_lower': r_2_5,
        'ci_upper': r_97_5,
        'ci_width': ci_width,
        'bootstrap_distribution': r_valid,
        'p1_estimates': p1_original.tolist(),
        'n_valid_bootstrap': len(r_valid)
    }

    return results


def main() -> None:
    """Runs the bootstrap relative-risk estimation from the command line."""
    parser = argparse.ArgumentParser(
        description='Bootstrap estimation of the relative risk (RR)')
    parser.add_argument(
        '--file', default=FILE_TO_READ,
        help=f'Input file from stat_analysis/ (default: {FILE_TO_READ})')
    parser.add_argument(
        '--n-bootstrap', type=int, default=N_BOOTSTRAP,
        help=f'Number of bootstrap repetitions (default: {N_BOOTSTRAP})')
    parser.add_argument(
        '--seed', type=int, default=RANDOM_SEED,
        help=f'Random seed (default: {RANDOM_SEED})')
    parser.add_argument(
        '--plot', action='store_true',
        help='Show a histogram of the bootstrap distribution')
    args = parser.parse_args()

    p0_example, y_example = load_p0_y(args.file)

    print("Example data:")
    print(f"p0_list: {p0_example[:5]}...")  # First 5 values
    print(f"y_list: {y_example[:5]}...")
    print(f"Sum of y_i: {np.sum(y_example)}")

    # Run analysis
    results = bootstrap_relative_risk(
        p0_list=p0_example,
        y_list=y_example,
        n_bootstrap=args.n_bootstrap,
        random_seed=args.seed
    )

    # Print results
    print("\n" + "=" * 50)
    print("BOOTSTRAP ANALYSIS RESULTS")
    print("=" * 50)
    print(
        f"Point estimate of relative risk (r): {results['point_estimate']:.3f}")
    print(f"Type of estimate: {results['estimate_type']}")
    print(
        f"95% confidence interval: "
        f"[{results['ci_lower']:.3f}, {results['ci_upper']:.3f}]")
    print(f"CI width: {results['ci_width']:.3f}")
    print(f"Number of bootstrap repetitions: {results['n_valid_bootstrap']}")

    # Visualization (optional)
    if args.plot:
        import matplotlib.pyplot as plt

        plt.figure(figsize=(10, 6))
        plt.hist(results['bootstrap_distribution'],
                 bins=50, alpha=0.7, edgecolor='black')
        plt.axvline(results['point_estimate'], color='red', linestyle='--',
                    linewidth=2, label=f'Estimate ({results["estimate_type"]})')
        plt.axvline(results['ci_lower'], color='orange', linestyle=':',
                    linewidth=2, label='95% CI (lower bound)')
        plt.axvline(results['ci_upper'], color='orange', linestyle=':',
                    linewidth=2, label='95% CI (upper bound)')
        plt.xlabel('Relative Risk (r)')
        plt.ylabel('Frequency')
        plt.title('Bootstrap Distribution of Relative Risk')
        plt.legend()
        plt.grid(alpha=0.3)
        plt.show()

    # Show first 5 p1_i estimates
    print("\nFirst 5 p1_i estimates:")
    for i, (p0, p1) in enumerate(
        zip(p0_example[:5], results['p1_estimates'][:5], strict=False)):
        print(f"  Person {i + 1}: p0 = {p0:.3f} → p1 = {p1:.3f}")


if __name__ == '__main__':
    main()
