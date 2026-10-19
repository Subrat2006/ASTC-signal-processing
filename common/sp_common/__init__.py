"""Small shared helpers for the Signal Processing Ladder solutions.

Deliberately generic: constants, unit conversions, statistics, plotting defaults and
*seeded synthetic data generators with known ground truth* (``sp_common.synth``).
They contain no solutions to any problem; the signal processing is yours to write.
"""
from . import constants, units, stats, plotting, rng, synth  # noqa: F401

__all__ = ["constants", "units", "stats", "plotting", "rng", "synth"]
__version__ = "1.0.0"
