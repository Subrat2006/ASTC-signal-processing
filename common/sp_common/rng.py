"""Reproducible random numbers. Call `get_rng()` at the top of every notebook."""
import numpy as np

DEFAULT_SEED = 2026


def get_rng(seed=DEFAULT_SEED):
    """Return a NumPy Generator with a fixed seed (state the seed in your report)."""
    return np.random.default_rng(seed)
