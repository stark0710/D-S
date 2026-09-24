"""
Fixed-Wing/Multirotor/VTOL Shared Optimization Utilities

Provides timing helper, normalizations, and common vector operators.
"""

import time
from typing import List, Dict, Any

class TimingHelper:
    """
    Context manager to accurately measure execution durations.
    """
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.time() - self.start

def normalize_value(val: float, min_val: float, max_val: float) -> float:
    """Scales a value linearly between 0.0 and 1.0."""
    denom = max_val - min_val
    if denom <= 0.0:
        return 0.0
    return (val - min_val) / denom

def weighted_sum(values: List[float], weights: List[float]) -> float:
    """Computes the dot product sum of value and weight arrays."""
    if len(values) != len(weights):
        raise ValueError("Values and weights lists must be of the same length.")
    return sum(v * w for v, w in zip(values, weights))

def format_diagnostics(diagnostics: Dict[str, Any]) -> str:
    """Generates simple key-value listing string from a diagnostics dict."""
    lines = []
    for k, v in diagnostics.items():
        lines.append(f"{k}: {v}")
    return "\n".join(lines)
