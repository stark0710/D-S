"""
VTOL Forward Propulsion Validator Subsystem

Purpose:
    Defines the `ForwardPropulsionValidator` class auditing clearances, ESC safety margins,
    thrust-to-drag margins, and climb capabilities.
"""

from typing import List
from backend.design.vtol.forward_propulsion.forward_propulsion_requirements import ForwardPropulsionRequirements
from backend.design.vtol.forward_propulsion.forward_propulsion_result import ForwardPropulsionResult


class ForwardPropulsionValidationError(ValueError):
    """
    Exception raised when VTOL forward propulsion sizing violates clearances or performance margins.
    """

    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class ForwardPropulsionValidator:
    """
    Validates sized forward propulsion parameters.
    """

    def validate(self, requirements: ForwardPropulsionRequirements, result: ForwardPropulsionResult) -> None:
        """
        Validates the forward propulsion sizing results.

        Args:
            requirements (ForwardPropulsionRequirements): Inputs.
            result (ForwardPropulsionResult): Outputs.

        Raises:
            ForwardPropulsionValidationError: If rules are violated.
        """
        errors: List[str] = []

        if requirements is None:
            raise ForwardPropulsionValidationError(["Requirements object is null."])

        esc = result.esc_selection
        motor = result.motor_selection
        layout = result.propulsion_layout
        analysis = result.cruise_analysis
        perf = result.performance_analysis
        power = result.power_analysis

        # 1. ESC safety margin check
        required_esc_current = motor["max_current_a"] * 1.2
        if esc["current_limit_a"] < required_esc_current:
            errors.append(
                f"ESC safety margin failure: selected ESC rating ({esc['current_limit_a']:.1f} A) "
                f"lacks 20% safety margin above motor max current ({motor['max_current_a']:.1f} A, needed {required_esc_current:.1f} A)."
            )

        # 2. Propeller-fuselage clearance check
        prop_radius = result.propeller_selection["diameter_m"] / 2.0
        fuse_width = requirements.fuselage_result.fuselage_geometry.width_m

        for p in layout.placements:
            if abs(p.y_m) > 0.05:  # Wing nacelle mounted
                available_clearance = abs(p.y_m) - (fuse_width / 2.0)
                if prop_radius >= available_clearance - 0.01:
                    errors.append(
                        f"Propeller tip clearance failure: propeller radius ({prop_radius:.3f} m) "
                        f"violates spacing margin relative to fuselage skin side wall ({available_clearance:.3f} m)."
                    )

        # 3. Thrust check
        if analysis.available_thrust_n < analysis.required_thrust_n:
            errors.append(
                f"Thrust insufficiency: maximum available cruise thrust ({analysis.available_thrust_n:.1f} N) "
                f"is less than required cruise thrust drag force ({analysis.required_thrust_n:.1f} N)."
            )

        # 4. Climb capability check
        min_climb = requirements.metadata.get("min_climb_rate", 1.5)
        if perf.rate_of_climb_m_s < min_climb:
            errors.append(
                f"Climb capability violation: sized climb rate ({perf.rate_of_climb_m_s:.2f} m/s) "
                f"is below required flight envelope rate of {min_climb:.2f} m/s."
            )

        if errors:
            raise ForwardPropulsionValidationError(errors)
