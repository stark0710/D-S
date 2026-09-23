"""
CompatibilityIssue Subsystem

Purpose:
    Defines the `CompatibilityIssue` domain model representing a single compatibility finding.

Role in Architecture:
    `CompatibilityIssue` captures details about a specific compatibility rule finding (rule name, severity, message, recommendation).
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.components.compatibility.compatibility_severity import CompatibilitySeverity


@dataclass(slots=True)
class CompatibilityIssue:
    """
    Compatibility evaluation finding.

    Attributes:
        rule_name (str): Identifier of the rule that generated this issue.
        severity (CompatibilitySeverity): Severity level (INFO, WARNING, CRITICAL).
        message (str): Human-readable explanation of the compatibility finding.
        recommendation (str): Corrective guidance or suggested resolution.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    rule_name: str
    severity: CompatibilitySeverity
    message: str
    recommendation: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
