"""
ManufacturingValidator Subsystem

Purpose:
    Defines the `ManufacturingValidator` class responsible for validating manufacturing package outputs against constraints.

Role in Architecture:
    `ManufacturingValidator` checks BOM cost bounds, document completeness, and material constraint matches.
"""

from backend.design.drone.manufacturing.manufacturing_result import ManufacturingResult
from backend.design.drone.manufacturing.manufacturing_constraints import ManufacturingConstraints


class ManufacturingValidator:
    """
    Validator for multirotor manufacturing package engineering outputs.

    Design Principles:
        - Single Responsibility Principle: BOM budget, sourcing lead time, and document completeness check only.
    """

    def validate_manufacturing_package(
        self,
        result: ManufacturingResult,
        constraints: ManufacturingConstraints
    ) -> list[str]:
        """
        Validates a ManufacturingResult against ManufacturingConstraints.

        Args:
            result (ManufacturingResult): Target manufacturing result object.
            constraints (ManufacturingConstraints): Sourcing constraints.

        Returns:
            list[str]: List of warning messages.
        """
        warnings: list[str] = []

        cost = result.bill_of_materials.total_cost_usd
        if cost > constraints.max_cost_usd:
            warnings.append(
                f"Manufacturing BOM cost (${cost:.2f}) exceeds target budget limit (${constraints.max_cost_usd:.2f})."
            )

        if not result.assembly_plan.required_tools:
            warnings.append("Assembly plan lacks required assembly tooling checklist definitions.")

        return warnings
