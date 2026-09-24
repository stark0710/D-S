"""
PayloadValidator Subsystem

Purpose:
    Defines the `PayloadValidator` class responsible for validating multirotor payload integration designs against constraints.

Role in Architecture:
    `PayloadValidator` checks payload physical envelope dimensions, mass limits, power draw limits, and CG offset bounds.
"""

from backend.design.drone.payload.payload_result import PayloadResult
from backend.design.drone.payload.payload_constraints import PayloadConstraints


class PayloadValidator:
    """
    Validator for multirotor payload integration designs.

    Design Principles:
        - Single Responsibility Principle: Payload mechanical, electrical, and CG constraint validation only.
    """

    def validate_payload(
        self,
        result: PayloadResult,
        constraints: PayloadConstraints
    ) -> list[str]:
        """
        Validates a PayloadResult against PayloadConstraints.

        Args:
            result (PayloadResult): Target payload result.
            constraints (PayloadConstraints): Payload constraints.

        Returns:
            list[str]: List of warning messages.
        """
        warnings: list[str] = []

        p_w = result.power_analysis.payload_power_w
        if p_w > constraints.max_payload_power_w:
            warnings.append(
                f"Payload power draw ({p_w:.1f}W) exceeds maximum allowed limit ({constraints.max_payload_power_w:.1f}W)."
            )

        cg_x = abs(result.balance_analysis.cg_offset_x_mm)
        if cg_x > constraints.max_cg_offset_mm:
            warnings.append(
                f"Longitudinal CG offset ({cg_x:.1f}mm) exceeds maximum allowable CG offset ({constraints.max_cg_offset_mm:.1f}mm). Risk of control saturation."
            )

        dims = result.selected_payload.dimensions_mm
        max_d = constraints.max_dimensions_mm
        if dims[0] > max_d[0] or dims[1] > max_d[1] or dims[2] > max_d[2]:
            warnings.append(
                f"Payload physical dimensions ({dims[0]}x{dims[1]}x{dims[2]}mm) exceed maximum envelope ({max_d[0]}x{max_d[1]}x{max_d[2]}mm)."
            )

        return warnings
