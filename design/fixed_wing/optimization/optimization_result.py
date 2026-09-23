"""
Fixed-Wing Wing Planform Optimization Result

Defines the structure for optimization execution results.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from backend.design.fixed_wing.optimization.optimization_models import PlanformCandidate
from backend.design.fixed_wing.wing.wing_result import WingResult

@dataclass
class WingOptimizationResult:
    """
    Result model enclosing the optimal planform configuration and sizing history.
    """
    best_candidate: PlanformCandidate | None
    best_wing_result: WingResult | None
    success: bool
    message: str
    evaluated_count: int = 0
    feasible_count: int = 0
    history: List[Dict[str, Any]] = field(default_factory=list)
    execution_time_seconds: float = 0.0
