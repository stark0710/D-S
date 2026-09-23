"""
Fixed-Wing Manufacturing Validator Subsystem

Purpose:
    Defines the `ManufacturingValidator` class to validate cost, drawings, and BOM lists.

Role in Architecture:
    `ManufacturingValidator` blocks handoff if unit cost exceeds budget constraints.
"""

from typing import List, Dict, Any
import os


class ManufacturingValidationError(ValueError):
    """Exception raised when generated manufacturing parameters fail safety checks."""
    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class ManufacturingValidator:
    """
    Validator enforcing manufacturing feasibility and package integrity.
    """

    def validate(
        self,
        cost_usd: float,
        max_cost_limit: float,
        bom: List[Dict[str, Any]],
        drawings: Dict[str, str],
        fab_files: Dict[str, str],
    ) -> List[str]:
        """
        Validates the sized manufacturing package.

        Returns:
            List[str]: A list of non-fatal warnings.

        Raises:
            ManufacturingValidationError: If critical compliance check errors are found.
        """
        errors: List[str] = []
        warnings: List[str] = []

        # 1. Budget check
        if cost_usd <= 0.0:
            errors.append("Invalid cost estimate: Sized production unit cost is zero or negative.")
        elif cost_usd > max_cost_limit:
            errors.append(
                f"Production cost estimate ({cost_usd:.2f} USD) exceeds the "
                f"maximum allowed budget constraint ({max_cost_limit:.2f} USD)."
            )

        # 2. BOM check
        if not bom:
            errors.append("Manufacturing package incomplete: Bill of Materials (BOM) list is empty.")
        else:
            # Check part numbering presence
            for item in bom:
                if "part_number" not in item:
                    errors.append("BOM compliance failed: Part numbering index is missing on some parts.")
                    break

        # 3. File existence checks
        for name, path in drawings.items():
            if not os.path.exists(path):
                errors.append(f"Manufacturing drawing missing: drawing for '{name}' was not found at '{path}'.")

        for proc, path in fab_files.items():
            if not os.path.exists(path):
                errors.append(f"Fabrication file missing: file for '{proc}' was not found at '{path}'.")

        if errors:
            raise ManufacturingValidationError(errors)

        return warnings
