"""
VTOL Optimization Profile parameters
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class OptimizationProfile:
    """
    Optimizer variables: generation size, crossover rates, and iteration counts.
    """
    max_iterations: int = 50
    population_size: int = 20
    crossover_rate: float = 0.80
    mutation_rate: float = 0.15
    convergence_tolerance: float = 1e-4
    metadata: Dict[str, Any] = field(default_factory=dict)
