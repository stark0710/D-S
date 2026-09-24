from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class OptimizationHistory:
    """
    Optimization trajectory recording iterations.
    """
    iterations: List[int]
    best_objective_values: List[float]
    average_objective_values: List[float]
    constraint_penalties: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)
