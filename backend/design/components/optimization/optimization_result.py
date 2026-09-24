"""
OptimizationResult Subsystem

Purpose:
    Defines the `OptimizationResult` domain model representing the output of an engineering optimization workflow.

Role in Architecture:
    `OptimizationResult` encapsulates the best optimized `OptimizationCandidate`, full optimization candidate history,
    iteration step records, improvement summary text, termination reason, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.components.optimization.optimization_candidate import OptimizationCandidate
from backend.design.components.optimization.optimization_iteration import OptimizationIteration


@dataclass(slots=True)
class OptimizationResult:
    """
    Aggregated engineering optimization workflow output.

    Attributes:
        best_design (OptimizationCandidate | None): Winning optimized candidate design.
        optimization_history (list[OptimizationCandidate]): Full list of evaluated candidate variants across all iterations.
        iterations (list[OptimizationIteration]): Step records summarizing each iteration step.
        improvement_summary (str): Transparent summary of score improvements achieved.
        termination_reason (str): Reason why optimization terminated (e.g. MaxIterations, TargetScoreReached).
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    best_design: OptimizationCandidate | None
    optimization_history: list[OptimizationCandidate] = field(default_factory=list)
    iterations: list[OptimizationIteration] = field(default_factory=list)
    improvement_summary: str = ""
    termination_reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
