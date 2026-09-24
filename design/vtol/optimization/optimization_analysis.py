"""
VTOL Optimization Sizing Aggregator
"""
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class OptimizationAnalysis:
    initial_fitness: float
    final_fitness: float
    improvement_pct: float
    iterations_run: int
    is_converged: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
