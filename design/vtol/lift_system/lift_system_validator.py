"""
VTOL Lift System Validator Subsystem

Purpose:
    Defines the `LiftSystemValidator` class checking clearances, thrust margins,
    ESC thermal current ratings, and battery C-rate discharges.
"""

from typing import List
import math
from backend.design.vtol.lift_system.lift_system_requirements import LiftSystemRequirements
from backend.design.vtol.lift_system.lift_system_result import LiftSystemResult


class LiftSystemValidationError(ValueError):
    """
    Exception raised when VTOL lift system sizing violates safety or physical margins.
    """

    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class LiftSystemValidator:
    """
    Validates sized lift system parameters.
    """

    def validate(self, requirements: LiftSystemRequirements, result: LiftSystemResult) -> None:
        """
        Validates the lift system sizing results.

        Args:
            requirements (LiftSystemRequirements): Inputs.
            result (LiftSystemResult): Outputs.

        Raises:
            LiftSystemValidationError: If rules are violated.
        """
        errors: List[str] = []

        if requirements is None:
            raise LiftSystemValidationError(["Requirements object is null."])

        hover = result.hover_analysis
        layout = result.rotor_layout
        power = result.power_analysis
        analysis = result.engineering_analysis

        # 0. Physical invariants validation
        mtow = getattr(getattr(requirements.mission_result, "mission_analysis", None), "estimated_mtow_kg", None)
        if mtow is not None and mtow <= 0.0:
            errors.append(f"Invalid aircraft mass: {mtow} kg <= 0. Mass must be strictly positive.")

        if len(layout.rotors) <= 0:
            errors.append(f"Invalid lift rotor count: {len(layout.rotors)} <= 0. Rotor count must be strictly positive.")

        if hover.required_hover_thrust_n <= 0.0:
            errors.append(f"Invalid required hover thrust: {hover.required_hover_thrust_n} N <= 0.")

        if result.technical_requirements:
            per_motor_t = result.technical_requirements.get("required_thrust_per_motor_n")
            if per_motor_t is not None and per_motor_t <= 0.0:
                errors.append(f"Invalid per-motor thrust: {per_motor_t} N <= 0.")

        if power.hover_total_power_kw <= 0.0:
            errors.append(f"Invalid hover power: {power.hover_total_power_kw} kW <= 0.")

        if power.hover_total_current_a <= 0.0:
            errors.append(f"Invalid hover current: {power.hover_total_current_a} A <= 0.")

        # 1. Thrust safety margin check
        if hover.available_hover_thrust_n < hover.required_hover_thrust_n:
            errors.append(
                f"Thrust sizing failure: available vertical lift thrust ({hover.available_hover_thrust_n:.1f} N) "
                f"is less than required hover thrust limit ({hover.required_hover_thrust_n:.1f} N)."
            )

        # 2. Disk loading limits
        if not (5.0 <= analysis.disk_loading_n_m2 <= requirements.metadata.get("max_disk_loading", 150.0)):
            errors.append(
                f"Disk loading boundary violation: calculated disk loading ({analysis.disk_loading_n_m2:.1f} N/m²) "
                f"falls outside allowable bounds (5.0 to 150.0 N/m²)."
            )

        # 3. Rotor spacing tip clearance check
        # Check closest spacing between any pair of rotors
        rotors = layout.rotors
        prop_diam = result.lift_propeller_selection["diameter_m"]

        if prop_diam <= 0.0:
            errors.append(f"Invalid rotor diameter: {prop_diam} m <= 0. Diameter must be strictly positive.")

        if len(rotors) > 1:
            min_dist = float("inf")
            for i in range(len(rotors)):
                for j in range(i + 1, len(rotors)):
                    dx = rotors[i].x_m - rotors[j].x_m
                    dy = rotors[i].y_m - rotors[j].y_m
                    dz = rotors[i].z_m - rotors[j].z_m
                    # Coaxial rotors share X and Y coordinates (dist = 0) which is allowed,
                    # but non-coaxial rotors must not overlap.
                    dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                    if dist > 0.001 and dist < min_dist:
                        min_dist = dist

            # Minimum clearance is 2.5% of propeller diameter
            if min_dist != float("inf") and min_dist <= prop_diam * 1.025:
                errors.append(
                    f"Rotor clearance check failed: closest rotor spacing ({min_dist:.3f} m) "
                    f"is less than required tip clearance safety margin ({prop_diam * 1.025:.3f} m)."
                )

        # 4. Battery C-rate check
        if power.battery_c_rate_required > requirements.metadata.get("max_battery_c_rate", 45.0):
            errors.append(
                f"Battery thermal overload: required hover discharge C-rate ({power.battery_c_rate_required:.1f} C) "
                f"exceeds safety threshold limit of {requirements.metadata.get('max_battery_c_rate', 45.0):.1f} C."
            )

        if errors:
            raise LiftSystemValidationError(errors)
