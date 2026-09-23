"""
ConstraintIssue Subsystem

Purpose:
    Defines the `ConstraintIssue` domain model representing a single engineering constraint finding or violation.

Role in Architecture:
    `ConstraintIssue` encapsulates the rule name, severity, target constraint name, expected value, actual value,
    explanatory message, and corrective recommendation.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.components.constraints.constraint_severity import ConstraintSeverity


@dataclass(slots=True)
class ConstraintIssue:
    """
    Diagnostic constraint evaluation finding.

    Attributes:
        rule_name (str): Identifier of the constraint rule that generated this finding.
        severity (ConstraintSeverity): Severity level (INFO, WARNING, CRITICAL).
        constraint_name (str): Name of the constraint evaluated (e.g. 'PayloadCapacity', 'FlightTime').
        expected_value (Any): Required or limit value.
        actual_value (Any): Calculated design value.
        message (str): Explanatory finding text.
        recommendation (str): Corrective engineering guidance.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    rule_name: str
    severity: ConstraintSeverity
    constraint_name: str
    expected_value: Any
    actual_value: Any
    message: str
    recommendation: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
