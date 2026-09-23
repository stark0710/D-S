"""
CompatibilityResult Subsystem

Purpose:
    Defines the `CompatibilityResult` domain model representing the output of a component compatibility check.

Role in Architecture:
    `CompatibilityResult` aggregates status, overall score, all identified issues, separated warnings, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.components.compatibility.compatibility_status import CompatibilityStatus
from backend.design.components.compatibility.compatibility_issue import CompatibilityIssue


@dataclass(slots=True)
class CompatibilityResult:
    """
    Aggregated component compatibility evaluation output.

    Attributes:
        status (CompatibilityStatus): Overall compatibility status (COMPATIBLE, COMPATIBLE_WITH_WARNINGS, INCOMPATIBLE, UNKNOWN).
        score (float): Normalized compatibility score from 0.0 (incompatible) to 1.0 (perfectly compatible).
        issues (list[CompatibilityIssue]): All identified compatibility findings.
        warnings (list[CompatibilityIssue]): Subset of issues with WARNING severity.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    status: CompatibilityStatus
    score: float
    issues: list[CompatibilityIssue] = field(default_factory=list)
    warnings: list[CompatibilityIssue] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
