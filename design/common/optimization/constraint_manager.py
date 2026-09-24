"""
Fixed-Wing/Multirotor/VTOL Shared Constraint Manager

Provides registration and batch evaluation for engineering constraints rules.
"""

from typing import Callable, Dict, Any, List, Tuple
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.optimization_context import OptimizationContext

class Constraint:
    """
    Wraps constraint metadata and function callbacks.
    """
    def __init__(
        self,
        name: str,
        check_fn: Callable[[OptimizationCandidate, OptimizationContext], Tuple[bool, str]]
    ) -> None:
        self.name = name
        self.check_fn = check_fn

    def evaluate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> Tuple[bool, str]:
        return self.check_fn(candidate, context)

class ConstraintManager:
    """
    Aggregates constraints and executes validation checks against candidate designs.
    """
    def __init__(self) -> None:
        self._constraints: List[Constraint] = []

    def add_constraint(
        self,
        name: str,
        check_fn: Callable[[OptimizationCandidate, OptimizationContext], Tuple[bool, str]]
    ) -> None:
        """Registers a new validation rule constraint."""
        self._constraints.append(Constraint(name, check_fn))

    def evaluate_constraints(self, candidate: OptimizationCandidate, context: OptimizationContext) -> bool:
        """
        Runs all registered rules against a candidate.
        """
        all_passed = True
        for constraint in self._constraints:
            try:
                passed, reason = constraint.evaluate(candidate, context)
            except Exception as e:
                passed = False
                reason = f"ConstraintCheckException: {type(e).__name__}: {e}"
            
            candidate.constraint_results[constraint.name] = {
                "status": "PASS" if passed else "FAIL",
                "reason": reason
            }
            if not passed:
                all_passed = False
        
        candidate.constraints_passed = all_passed
        candidate.status = "PENDING" if all_passed else "INFEASIBLE"
        return all_passed
