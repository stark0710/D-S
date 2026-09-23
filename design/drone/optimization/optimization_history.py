"""
OptimizationHistory Subsystem

Purpose:
    Defines the `OptimizationHistory` class for tracking optimization iterations and convergence history.

Role in Architecture:
    `OptimizationHistory` records iteration logs, candidate evaluation trajectories, and convergence metrics.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class OptimizationIterationLog:
    """Single optimization iteration log record."""
    iteration: int
    best_score: float
    candidate_count: int
    metadata: dict[str, Any] = field(default_factory=dict)


class OptimizationHistory:
    """
    Tracking service for optimization iteration history.

    Design Principles:
        - Single Responsibility Principle: Optimization trajectory and iteration logging only.
    """

    def __init__(self) -> None:
        """Initializes OptimizationHistory."""
        self._history: list[OptimizationIterationLog] = []

    def record_iteration(self, iteration: int, best_score: float, candidate_count: int) -> None:
        """Records an iteration snapshot."""
        self._history.append(OptimizationIterationLog(iteration, best_score, candidate_count))

    def get_history(self) -> list[OptimizationIterationLog]:
        """Returns the full iteration history."""
        return list(self._history)
