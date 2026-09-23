"""
ValidationIssue Subsystem

Purpose:
    Defines the `ValidationIssue` domain model representing a single validation problem or advisory note.

Role in Architecture:
    `ValidationIssue` encapsulates details about a single requirement validation finding (field name, code, severity,
    message, and corrective recommendation).
"""

from dataclasses import dataclass
from backend.design.common.validation.validation_code import ValidationCode
from backend.design.common.validation.validation_severity import ValidationSeverity


@dataclass(slots=True)
class ValidationIssue:
    """
    Diagnostic validation finding for a single requirement field.

    Attributes:
        code (ValidationCode): Standardized classification code.
        severity (ValidationSeverity): Severity level (INFO, WARNING, ERROR).
        field_name (str): Name of the requirement field containing the issue.
        message (str): Human-readable explanation of the issue.
        recommendation (str): Corrective guidance or suggested action for the user.
    """

    code: ValidationCode
    severity: ValidationSeverity
    field_name: str
    message: str
    recommendation: str = ""
