"""
Fixed-Wing/Multirotor/VTOL Shared Optimization Candidate

Holds design variable choices, calculated derived values, and optimization metrics.
"""

from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class OptimizationCandidate:
    """
    Model enclosing variable states, constraint statuses, and objective scoring.
    """
    design_variables: Dict[str, Any]
    derived_variables: Dict[str, Any] = field(default_factory=dict)
    constraints_passed: bool = True
    constraint_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    objective_scores: Dict[str, float] = field(default_factory=dict)
    overall_score: float = 0.0
    status: str = "PENDING"
    diagnostics: Dict[str, Any] = field(default_factory=dict)
