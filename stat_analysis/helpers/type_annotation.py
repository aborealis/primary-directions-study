"""Custom type annotations for the statistical scripts."""

from dataclasses import dataclass


@dataclass
class PowerConfig:
    """Configuration of the statistical power estimation"""

    # Candidate sample sizes (k) to test, in increasing order
    sample_sizes: list[int] | None = None
    # Number of simulated studies per sample size k
    n_simulations: int = 1000
    # Number of Monte-Carlo repetitions per p-value estimate
    n_monte_carlo: int = 1000
    # Significance level
    alpha: float = 0.05
    # Seed of the random generator; None for a non-deterministic seed
    random_seed: int | None = None
    verbose: bool = True
