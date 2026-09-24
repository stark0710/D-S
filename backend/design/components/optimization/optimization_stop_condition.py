"""
OptimizationStopCondition Subsystem

Purpose:
    Defines the `OptimizationStopCondition` class for evaluating optimization termination conditions.

Role in Architecture:
    `OptimizationStopCondition` checks maximum iterations, minimum score improvement threshold, target score achievement,
    or lack of improvement to terminate optimization loops cleanly.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class OptimizationStopCondition:
    """
    Configurable termination conditions for optimization workflows.

    Attributes:
        max_iterations (int): Upper bound on allowed iteration loops (default 10).
        min_improvement (float): Minimum required score improvement delta to continue (default 0.001).
        target_score (float): Target score threshold at which optimization terminates early (default 0.98).
        max_no_improvement_steps (int): Maximum consecutive steps without improvement before stopping (default 3).
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    max_iterations: int = 10
    min_improvement: float = 0.001
    target_score: float = 0.98
    max_no_improvement_steps: int = 3
    metadata: dict[str, Any] = field(default_factory=dict)

    def should_stop(
        self,
        current_iteration: int,
        improvement_delta: float,
        current_best_score: float,
        no_improvement_count: int = 0
    ) -> tuple[bool, str]:
        """
        Evaluates whether optimization should terminate.

        Args:
            current_iteration (int): Current iteration step.
            improvement_delta (float): Score improvement achieved in current step.
            current_best_score (float): Current best overall score achieved.
            no_improvement_count (int): Consecutive steps without improvement.

        Returns:
            tuple[bool, str]: Tuple of (should_stop boolean, termination_reason string).
        """
        if current_best_score >= self.target_score:
            return True, f"Target score threshold achieved ({current_best_score:.3f} >= {self.target_score:.3f})."

        if current_iteration >= self.max_iterations:
            return True, f"Maximum iterations limit reached ({current_iteration} >= {self.max_iterations})."

        if no_improvement_count >= self.max_no_improvement_steps:
            return True, f"No further score improvement for {no_improvement_count} consecutive iterations."

        if current_iteration > 1 and improvement_delta < self.min_improvement and no_improvement_count > 0:
            return True, f"Improvement delta ({improvement_delta:.4f}) fell below minimum threshold ({self.min_improvement:.4f})."

        return False, ""
