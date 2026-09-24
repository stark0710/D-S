"""
ReportValidator Subsystem

Purpose:
    Defines the `ReportValidator` class responsible for validating structure and section ordering of an `EngineeringReport`.

Role in Architecture:
    `ReportValidator` enforces structural validation rules on built reports prior to export or delivery.
"""

from backend.design.studio.reports.report import EngineeringReport


class ReportValidationError(ValueError):
    """Raised when EngineeringReport validation fails."""
    pass


class ReportValidator:
    """
    Validator for EngineeringReport instances.

    Design Principles:
        - Single Responsibility Principle: Report structure and section ordering validation only.
    """

    def validate(self, report: EngineeringReport) -> bool:
        """
        Validates report structure, required fields, and section ordering.

        Args:
            report (EngineeringReport): Target report instance.

        Returns:
            bool: True if valid.

        Raises:
            ReportValidationError: If validation checks fail.
        """
        if not report.report_id or not report.report_id.strip():
            raise ReportValidationError("EngineeringReport report_id must not be empty.")

        if not report.title or not report.title.strip():
            raise ReportValidationError("EngineeringReport title must not be empty.")

        if not report.sections:
            raise ReportValidationError("EngineeringReport must contain at least one section.")

        for sec in report.sections:
            if not sec.title or not sec.title.strip():
                raise ReportValidationError("ReportSection title must not be empty.")

            if sec.order <= 0:
                raise ReportValidationError(f"ReportSection '{sec.title}' must have a positive 1-based order index (got {sec.order}).")

        return True
