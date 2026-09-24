"""
Fixed-Wing Engineering Report Validator Subsystem

Purpose:
    Defines the `ReportValidator` class to validate report chapters and file existence.

Role in Architecture:
    `ReportValidator` executes audits on section presence and export file sizes.
"""

from typing import List, Dict, Any
import os


class ReportValidationError(ValueError):
    """Exception raised when generated report parameters fail validations."""
    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class ReportValidator:
    """
    Validator enforcing report completeness and export file integrity.
    """

    def validate(
        self,
        exec_summary: str,
        sections: Dict[str, str],
        min_sections: int,
        exported_files: Dict[str, str],
    ) -> List[str]:
        """
        Validates the sized engineering report.

        Returns:
            List[str]: A list of non-fatal warnings.

        Raises:
            ReportValidationError: If critical section or export errors are found.
        """
        errors: List[str] = []
        warnings: List[str] = []

        # 1. Executive Summary check
        if not exec_summary or not exec_summary.strip():
            errors.append("Invalid report: Executive Summary is empty.")

        # 2. Section count check
        if len(sections) < min_sections:
            errors.append(
                f"Report incomplete: Sized chapters count ({len(sections)}) "
                f"is below the minimum required sections constraint ({min_sections})."
            )

        # 3. Core chapters check
        required_chapters = ["Executive Summary", "Mission Overview", "Configuration", "Wing Geometry"]
        for ch in required_chapters:
            if ch not in sections:
                errors.append(f"Missing core report chapter: '{ch}' was not compiled.")

        # 4. File existence checks
        for fmt, path in exported_files.items():
            if not os.path.exists(path):
                errors.append(f"Report export file missing: report file for '{fmt}' was not found at '{path}'.")
            elif os.path.getsize(path) == 0:
                errors.append(f"Report export file empty: report file for '{fmt}' at '{path}' is empty.")

        if errors:
            raise ReportValidationError(errors)

        return warnings
