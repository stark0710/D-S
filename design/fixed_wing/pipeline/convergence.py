"""
Convergence Evaluator for Fixed-Wing Sizing Loop.
"""

from dataclasses import dataclass
from typing import List


# Configurable Defaults
DEFAULT_CONVERGENCE_TOLERANCE: float = 0.01  # 1% relative MTOW change
DEFAULT_MAX_ITERATIONS: int = 40
SMALL_POSITIVE_EPSILON: float = 1e-6


@dataclass(slots=True)
class IterationRecord:
    """
    Encapsulates convergence metrics for a single iteration step.
    """
    iteration: int
    mtow_old: float
    mtow_new: float
    absolute_delta_kg: float
    relative_delta: float
    converged: bool


class ConvergenceEvaluator:
    """
    Evaluates relative MTOW convergence between sizing iteration steps.
    """

    def __init__(
        self,
        tolerance: float = DEFAULT_CONVERGENCE_TOLERANCE,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
        epsilon: float = SMALL_POSITIVE_EPSILON,
    ) -> None:
        self.tolerance = tolerance
        self.max_iterations = max_iterations
        self.epsilon = epsilon

    def evaluate_step(self, iteration: int, mtow_old: float, mtow_new: float) -> IterationRecord:
        """
        Calculates absolute and relative change in MTOW and determines convergence.
        """
        abs_delta = abs(mtow_new - mtow_old)
        denominator = max(abs(mtow_old), self.epsilon)
        rel_delta = abs_delta / denominator

        converged = rel_delta <= self.tolerance

        return IterationRecord(
            iteration=iteration,
            mtow_old=round(mtow_old, 4),
            mtow_new=round(mtow_new, 4),
            absolute_delta_kg=round(abs_delta, 4),
            relative_delta=round(rel_delta, 6),
            converged=converged,
        )
