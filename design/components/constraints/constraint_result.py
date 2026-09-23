"""
ConstraintResult Subsystem

Purpose:
    Defines the `ConstraintResult` domain model representing the output of an engineering constraint evaluation.

Role in Architecture:
    `ConstraintResult` aggregates status, overall score, all identified issues, warnings, lists of satisfied and violated constraint names, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.components.constraints.constraint_status import ConstraintStatus
from backend.design.components.constraints.constraint_issue import ConstraintIssue


@dataclass(slots=True)
class ConstraintResult:
    """
    Aggregated engineering constraint evaluation output.

    Attributes:
        status (ConstraintStatus): Overall constraint satisfaction status (SATISFIED, SATISFIED_WITH_WARNINGS, VIOLATED, UNKNOWN).
        overall_score (float): Normalized satisfaction score from 0.0 (all violated) to 1.0 (all satisfied).
        issues (list[ConstraintIssue]): All identified constraint findings.
        warnings (list[ConstraintIssue]): Subset of issues with WARNING severity.
        satisfied_constraints (list[str]): Names of successfully satisfied engineering constraints.
        violated_constraints (list[str]): Names of violated engineering constraints.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    status: ConstraintStatus
    overall_score: float
    issues: list[ConstraintIssue] = field(default_factory=list)
    warnings: list[ConstraintIssue] = field(default_factory=list)
    satisfied_constraints: list[str] = field(default_factory=list)
    violated_constraints: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
