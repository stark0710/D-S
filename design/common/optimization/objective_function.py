"""
Fixed-Wing/Multirotor/VTOL Shared Objective Scorer

Computes candidate scores using normalized and weighted functions.
"""

from typing import Callable, Dict, List
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.optimization_context import OptimizationContext

class ObjectiveTerm:
    """
    Metadata container for an individual objective metric.
    """
    def __init__(
        self,
        name: str,
        score_fn: Callable[[OptimizationCandidate, OptimizationContext], float],
        weight: float = 1.0,
        minimize: bool = True
    ) -> None:
        self.name = name
        self.score_fn = score_fn
        self.weight = weight
        self.minimize = minimize

class ObjectiveFunction:
    """
    Manages terms and aggregates scores to rank candidate designs.
    """
    def __init__(self) -> None:
        self._terms: List[ObjectiveTerm] = []

    def add_objective(
        self,
        name: str,
        score_fn: Callable[[OptimizationCandidate, OptimizationContext], float],
        weight: float = 1.0,
        minimize: bool = True
    ) -> None:
        """Registers a new objective optimization goal."""
        self._terms.append(ObjectiveTerm(name, score_fn, weight, minimize))

    def calculate_scores(
        self,
        candidate: OptimizationCandidate,
        context: OptimizationContext,
        normalize_limits: Dict[str, tuple[float, float]] | None = None
    ) -> float:
        """
        Calculates and aggregates weighted objective scores.
        """
        total_score = 0.0
        for term in self._terms:
            try:
                raw_val = term.score_fn(candidate, context)
            except Exception as e:
                raw_val = float('inf') if term.minimize else float('-inf')
                
            candidate.objective_scores[term.name] = raw_val
            
            val = raw_val
            if normalize_limits and term.name in normalize_limits:
                min_lim, max_lim = normalize_limits[term.name]
                denom = max_lim - min_lim
                if denom > 0.0:
                    val = (raw_val - min_lim) / denom
                else:
                    val = 0.0
            
            multiplier = 1.0 if term.minimize else -1.0
            total_score += term.weight * val * multiplier
            
        candidate.overall_score = float(total_score)
        return float(total_score)
