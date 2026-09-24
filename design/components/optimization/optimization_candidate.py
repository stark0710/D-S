"""
OptimizationCandidate Subsystem

Purpose:
    Defines the `OptimizationCandidate` domain model representing an intermediate design variant evaluated during optimization.

Role in Architecture:
    `OptimizationCandidate` encapsulates a `DesignContext`, its evaluated `EngineeringScore`, iteration number,
    parent candidate reference, applied modifications dictionary, and diagnostic metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.common.context.design_context import DesignContext
from backend.design.components.scoring.engineering_score import EngineeringScore


@dataclass(slots=True)
class OptimizationCandidate:
    """
    Intermediate design candidate evaluated during optimization.

    Attributes:
        design_context (DesignContext): DesignContext carrying design data and requirements.
        engineering_score (EngineeringScore | float | None): Evaluated engineering score model or numeric score.
        iteration (int): Optimization iteration step number (0 = baseline).
        parent_candidate (Any | None): Optional reference to parent candidate from which this variant was derived.
        modifications (dict[str, Any]): Dictionary of parameter modifications applied to derive this candidate.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    design_context: DesignContext
    engineering_score: EngineeringScore | float | None = None
    iteration: int = 0
    parent_candidate: Any | None = None
    modifications: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
