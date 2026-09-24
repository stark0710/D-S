"""
Fixed-Wing/Multirotor/VTOL Shared Optimization Result

Defines standard output model enclosing optimized designs and tracking data.
"""

from dataclasses import dataclass, field
from typing import Any, List, Dict
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate

@dataclass
class OptimizationResult:
    """
    Result containing optimal candidate specifications and solver diagnostic data.
    """
    winning_candidate: OptimizationCandidate | None
    generated_specification: Any
    success: bool
    message: str
    evaluated_count: int = 0
    feasible_count: int = 0
    history: List[OptimizationCandidate] = field(default_factory=list)
    rejected_summary: Dict[str, Any] = field(default_factory=dict)
    execution_time_seconds: float = 0.0
    iteration_count: int = 0
    diagnostics: Dict[str, Any] = field(default_factory=dict)
