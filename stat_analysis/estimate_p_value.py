"""Determines the p-value of the observed number of events by Monte-Carlo simulation."""
import argparse
import os
import sys
from typing import Any

# Allow running this script directly (python stat_analysis/estimate_p_value.py)
# in addition to the module form (python -m stat_analysis.estimate_p_value).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stat_analysis.helpers.array_backend import get_array_module
from stat_analysis.helpers.data_loading import load_p0_y
from stat_analysis.helpers.monte_carlo import monte_carlo_p_value_vectorized

# === Settings ===
# Defaults reproduce the published result for the 400-chart sample (p = 0.1077).
FILE_TO_READ = 'p0_y-400-fixed.txt'
N_SIMULATIONS = 10000
RANDOM_SEED = 42


def main() -> None:
    """Estimates the p-value of the observed number of deaths."""
    parser = argparse.ArgumentParser(
        description='Monte-Carlo p-value for the observed number of deaths')
    parser.add_argument(
        '--file', default=FILE_TO_READ,
        help=f'Input file from stat_analysis/ (default: {FILE_TO_READ})')
    parser.add_argument(
        '--n-sims', type=int, default=N_SIMULATIONS,
        help=f'Number of Monte-Carlo simulations (default: {N_SIMULATIONS})')
    parser.add_argument(
        '--seed', type=int, default=RANDOM_SEED,
        help=f'Random seed (default: {RANDOM_SEED})')
    args = parser.parse_args()

    np: Any = get_array_module()

    p0_list, y_list = load_p0_y(args.file)
    s_obs = sum(y_list)

    # Convert to numpy/cupy array
    p0_array = np.array(p0_list)

    # Create random generator
    rng = np.random.default_rng(args.seed)

    p_value = monte_carlo_p_value_vectorized(
        p0_sample=p0_array,
        s_obs=s_obs,
        n_simulations=args.n_sims,
        random_generator=rng
    )

    print('p-value:', p_value)


if __name__ == '__main__':
    main()
