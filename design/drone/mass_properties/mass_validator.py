"""
MassValidator Subsystem

Purpose:
    Defines the `MassValidator` class responsible for validating multirotor mass properties and CG balance against constraints.

Role in Architecture:
    `MassValidator` checks MTOW limits, pitch/roll balance margins, CG offset bounds, and lateral symmetry.
"""

from backend.design.drone.mass_properties.mass_result import MassResult


class MassValidator:
    """
    Validator for multirotor mass properties and Center of Gravity balance.

    Design Principles:
        - Single Responsibility Principle: Mass properties, MTOW, and CG balance constraint validation only.
    """

    def validate_mass_properties(
        self,
        result: MassResult,
        max_mtow_kg: float = 25.0
    ) -> list[str]:
        """
        Validates a MassResult against MTOW and CG balance constraints.

        Args:
            result (MassResult): Target mass result object.
            max_mtow_kg (float): Maximum allowable MTOW limit in kg.

        Returns:
            list[str]: List of warning messages.
        """
        warnings: list[str] = []

        if result.total_mass_kg > max_mtow_kg:
            warnings.append(
                f"Total All-Up Weight ({result.total_mass_kg:.2f} kg) exceeds maximum MTOW limit ({max_mtow_kg:.2f} kg)."
            )

        if not result.balance_analysis.pitch_balanced:
            warnings.append(
                f"Pitch static unbalance detected: CG longitudinal offset ({result.center_of_gravity.cg_x_mm:.1f}mm) "
                f"exceeds allowable margin (+/-{result.center_of_gravity.cg_margin_x_mm:.1f}mm). "
                f"Recommend relocating battery by {result.balance_analysis.battery_shift_recommendation_mm:.1f}mm."
            )

        if not result.balance_analysis.roll_balanced:
            warnings.append(
                f"Roll static unbalance detected: CG lateral offset ({result.center_of_gravity.cg_y_mm:.1f}mm) "
                f"exceeds allowable margin (+/-{result.center_of_gravity.cg_margin_y_mm:.1f}mm)."
            )

        return warnings
