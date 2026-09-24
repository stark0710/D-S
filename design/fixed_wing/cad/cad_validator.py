"""
Fixed-Wing CAD Validator Subsystem

Purpose:
    Defines the `CADValidator` class to validate geometry bounds, feature logs, and file existence.

Role in Architecture:
    `CADValidator` runs audits on generated solid volumes and file paths.
"""

from typing import List, Dict, Any
import os


class CADValidationError(ValueError):
    """Exception raised when generated CAD parameters fail safety audits."""
    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class CADValidator:
    """
    Validator enforcing geometric integrity and file export validity.
    """

    def validate(
        self,
        volume_m3: float,
        bbox: tuple[float, float, float],
        parts: Dict[str, Any],
        exported_files: Dict[str, str],
        allowed_formats: List[str],
    ) -> List[str]:
        """
        Validates the sized CAD parameters.

        Returns:
            List[str]: A list of non-fatal warnings.

        Raises:
            CADValidationError: If critical geometry or export errors are found.
        """
        errors: List[str] = []
        warnings: List[str] = []

        # 1. Volume check
        if volume_m3 <= 0.0:
            errors.append("Invalid solid geometry: Total calculated volume is zero or negative.")

        # 2. Bounding box check
        if any(dim <= 0.0 for dim in bbox):
            errors.append("Invalid bounding box: Bounding box dimensions must be strictly positive.")

        # 3. Parts checklist
        required_parts = ["wing", "fuselage", "tail"]
        for p in required_parts:
            if p not in parts:
                errors.append(f"Missing core assembly component: '{p}' was not generated.")

        # 4. File existence checks
        for fmt, path in exported_files.items():
            if fmt.upper() in allowed_formats:
                if not os.path.exists(path):
                    errors.append(f"Export file integrity check failed: file not found at '{path}'.")
                elif os.path.getsize(path) == 0:
                    errors.append(f"Export file integrity check failed: file at '{path}' is empty.")

        if errors:
            raise CADValidationError(errors)

        return warnings
