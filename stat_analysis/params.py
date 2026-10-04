"""Parameters of the statistical calculations.

USE_GPU selects the array computation backend used by the Monte-Carlo
and power-analysis scripts: CuPy on the GPU when True, NumPy on the
CPU when False (see stat_analysis/helpers/array_backend.py).
"""

USE_GPU = True
