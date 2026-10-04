"""Selection of the array computation backend: CuPy (GPU) or NumPy (CPU)."""

import warnings
from types import ModuleType
from typing import Any, TypeAlias

from stat_analysis.params import USE_GPU

# numpy.ndarray and cupy.ndarray (and their random generators) share the
# API surface used by this code but are distinct types; the analysis
# functions annotate them loosely as Any on purpose.
Array: TypeAlias = Any
RandomGenerator: TypeAlias = Any

# Backend selected on the first call: (array module, runs on the GPU).
_selected_backend: tuple[ModuleType, bool] | None = None


def _select_backend() -> tuple[ModuleType, bool]:
    """
    Returns the array module selected by the USE_GPU setting — cupy when
    GPU calculations are enabled and a working cupy installation exists,
    numpy otherwise — together with a flag telling whether the module
    actually runs on the GPU.
    """
    global _selected_backend

    if _selected_backend is None:
        if USE_GPU:
            try:
                import cupy

                # cupy compiles its kernels on first use, so a successful
                # import does not yet prove the backend works: without the
                # CUDA toolkit headers (or with a missing driver) the failure
                # surfaces only inside the first calculation. A tiny probe
                # verifies the full path up front.
                cupy.arange(1).sum()
            except (ImportError, RuntimeError) as error:
                warnings.warn(
                    f'USE_GPU is enabled but cupy is unusable ({error}); '
                    'falling back to numpy',
                    stacklevel=2,
                )
            else:
                _selected_backend = (cupy, True)

        if _selected_backend is None:
            import numpy
            _selected_backend = (numpy, False)

    return _selected_backend


def get_array_module() -> ModuleType:
    """Returns the array module selected by the USE_GPU setting."""
    return _select_backend()[0]


def gpu_active() -> bool:
    """
    Returns True when the selected array module is cupy running on the
    GPU — as opposed to USE_GPU, which only expresses the intention: when
    cupy is missing or broken the backend silently falls back to numpy.
    Backend-specific code must branch on this flag, not on USE_GPU.
    """
    return _select_backend()[1]
