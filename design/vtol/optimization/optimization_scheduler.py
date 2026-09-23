from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class OptimizationScheduler:
    """
    Manages generation counts and parameter adjustments.
    """
    current_iteration: int
    max_iterations: int
    current_mutation_rate: float
    convergence_detected: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
