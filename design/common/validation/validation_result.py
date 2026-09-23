"""
ValidationResult Subsystem

Purpose:
    Defines the `ValidationResult` domain model returned by the Requirement Validation Framework.

Role in Architecture:
    `ValidationResult` aggregates all `ValidationIssue` objects identified during requirement validation,
    summarizes overall validity (`is_valid`), separates errors from warnings, and carries metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.common.validation.validation_issue import ValidationIssue


@dataclass(slots=True)
class ValidationResult:
    """
    Aggregated validation result summary.

    Attributes:
        is_valid (bool): True if zero ERROR severity issues were found; False otherwise.
        issues (list[ValidationIssue]): All identified validation issues (info, warnings, and errors).
        warnings (list[ValidationIssue]): Subset of issues with WARNING severity.
        errors (list[ValidationIssue]): Subset of issues with ERROR severity.
        metadata (dict[str, Any]): Additional diagnostic execution metadata.
    """

    is_valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    errors: list[ValidationIssue] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
