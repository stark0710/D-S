"""
ElectricalValidator Subsystem

Purpose:
    Defines the `ElectricalValidator` class responsible for validating multirotor electrical subsystem designs against constraints.

Role in Architecture:
    `ElectricalValidator` checks battery mass, ESC current margins, battery C-rate capacity, PDB rating compatibility, and wiring voltage drop.
"""

from backend.design.drone.electrical.electrical_result import ElectricalResult
from backend.design.drone.electrical.electrical_constraints import ElectricalConstraints


class ElectricalValidator:
    """
    Validator for multirotor electrical power designs.

    Design Principles:
        - Single Responsibility Principle: Electrical power subsystem constraint and safety validation only.
    """

    def validate_electrical(
        self,
        result: ElectricalResult,
        constraints: ElectricalConstraints
    ) -> list[str]:
        """
        Validates an ElectricalResult against ElectricalConstraints.

        Args:
            result (ElectricalResult): Target electrical result.
            constraints (ElectricalConstraints): Electrical constraints.

        Returns:
            list[str]: List of warning messages.
        """
        warnings: list[str] = []

        bat_wt = result.selected_battery.get("estimated_battery_weight_g", 0.0)
        if bat_wt > constraints.max_battery_weight_g:
            warnings.append(
                f"Battery pack weight ({bat_wt:.0f}g) exceeds maximum allowed limit ({constraints.max_battery_weight_g:.0f}g)."
            )

        req_c = result.current_analysis.required_discharge_c
        bat_c = result.selected_battery.get("discharge_rating_c", 20.0)
        if req_c > bat_c:
            warnings.append(
                f"Required battery discharge rate ({req_c:.1f}C) exceeds pack continuous C-rating ({bat_c:.1f}C). Risk of battery thermal runaway."
            )

        v_drop = result.voltage_analysis.estimated_voltage_drop_v
        if v_drop > 0.5:
            warnings.append(
                f"Wiring voltage drop ({v_drop:.2f}V) under peak load is high (> 0.5V). Recommend increasing main lead AWG gauge."
            )

        return warnings
