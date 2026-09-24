"""
OptimizationIteration Subsystem

Purpose:
    Defines the `OptimizationIteration` domain model representing a single step record in the optimization history.

Role in Architecture:
    `OptimizationIteration` records iteration step number, candidate count evaluated, best score achieved,
    score improvement delta, duration, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class OptimizationIteration:
    """
    Diagnostic history record for a single optimization iteration step.

    Attributes:
        iteration_number (int): Ordinal iteration step number.
        candidate_count (int): Number of modified candidates evaluated in this iteration.
        best_score (float): Highest score achieved in this iteration step.
        improvement (float): Score improvement delta achieved over prior iteration best score.
        duration (float): Execution duration in seconds.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    iteration_number: int
    candidate_count: int
    best_score: float
    improvement: float
    duration: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
