from typing import List, Optional
from .transition_result import TransitionResult
from .transition_constraints import TransitionConstraints
from .authoritative_transition import AuthoritativeTransitionResult, TransitionPhysicsValidationError

class TransitionValidator:
    """
    Validates conversion parameters, flight stability limits, and aerodynamic physics invariants.
    """

    @staticmethod
    def validate_inputs(
        mass_kg: float,
        wing_area_m2: float,
        air_density_kg_m3: float,
        lift_motor_count: int,
        direction: str = "TRANSITION_TO_CRUISE",
        transition_speed_kmh: Optional[float] = None,
        cl_max: Optional[float] = None,
    ) -> None:
        """
        Validates transition engineering inputs against physical invariants.
        Raises TransitionPhysicsValidationError if any invariant is violated.
        """
        errors = []
        if mass_kg <= 0.0:
            errors.append(f"Physical invariant violation: mass ({mass_kg} kg) must be > 0.")
        if wing_area_m2 <= 0.0:
            errors.append(f"Physical invariant violation: wing area ({wing_area_m2} m²) must be > 0.")
        if air_density_kg_m3 <= 0.0:
            errors.append(f"Physical invariant violation: air density ({air_density_kg_m3} kg/m³) must be > 0.")
        if lift_motor_count <= 0:
            errors.append(f"Physical invariant violation: lift motor count ({lift_motor_count}) must be > 0.")
        if transition_speed_kmh is not None and transition_speed_kmh <= 0.0:
            errors.append(f"Physical invariant violation: transition speed ({transition_speed_kmh} km/h) must be > 0.")
        if cl_max is not None and cl_max <= 0.0:
            errors.append(f"Physical invariant violation: CL_max ({cl_max}) must be > 0.")

        norm_dir = direction.strip().upper() if direction else ""
        if norm_dir not in ("TRANSITION_TO_CRUISE", "TRANSITION_TO_VTOL"):
            errors.append(
                f"Invalid transition direction: '{direction}'. "
                "Must be 'TRANSITION_TO_CRUISE' or 'TRANSITION_TO_VTOL'."
            )

        if errors:
            raise TransitionPhysicsValidationError(errors)

    @staticmethod
    def validate_corridor(auth_result: AuthoritativeTransitionResult) -> List[str]:
        """
        Checks authoritative transition corridor points for physical consistency.
        """
        issues = []
        if not auth_result.corridor_points or len(auth_result.corridor_points) < 2:
            issues.append("Corridor contains insufficient operating points (< 2).")
            return issues

        # Check non-negative thrust and valid lift fractions across all points
        for p in auth_result.corridor_points:
            if p.wing_lift_n < -1e-6:
                issues.append(f"Negative wing lift ({p.wing_lift_n:.2f} N) at {p.stage_name}.")
            if p.required_vertical_thrust_n < -1e-6:
                issues.append(f"Negative required vertical thrust ({p.required_vertical_thrust_n:.2f} N) at {p.stage_name}.")
            if p.vertical_thrust_per_motor_n < -1e-6:
                issues.append(f"Negative per-motor vertical thrust ({p.vertical_thrust_per_motor_n:.2f} N) at {p.stage_name}.")
            if p.wing_lift_fraction < -1e-4 or p.wing_lift_fraction > 1.0001:
                issues.append(f"Wing lift fraction ({p.wing_lift_fraction:.3f}) out of physical [0, 1] range at {p.stage_name}.")
            if p.vertical_thrust_fraction < -1e-4 or p.vertical_thrust_fraction > 1.0001:
                issues.append(f"Vertical thrust fraction ({p.vertical_thrust_fraction:.3f}) out of physical [0, 1] range at {p.stage_name}.")

        # Check handover condition
        entry_point = auth_result.corridor_points[-1] if auth_result.direction == "TRANSITION_TO_CRUISE" else auth_result.corridor_points[0]
        if entry_point.wing_lift_fraction < 0.95:
            issues.append(
                f"Fixed-wing entry occurs prematurely: wing lift fraction is only {entry_point.wing_lift_fraction:.2f} (< 0.95 required)."
            )

        return issues

    @staticmethod
    def validate(result: TransitionResult, constraints: TransitionConstraints) -> List[str]:
        warnings = []

        # Check conversion speed
        v_conv = result.transition_analysis.conversion_speed_kmh
        if v_conv < constraints.min_conversion_speed_kmh or v_conv > constraints.max_conversion_speed_kmh:
            warnings.append(
                f"Sized transition conversion speed ({v_conv:.1f} km/h) "
                f"is outside safe boundaries ({constraints.min_conversion_speed_kmh:.1f} - {constraints.max_conversion_speed_kmh:.1f} km/h)"
            )

        # Check duration
        t_conv = result.transition_analysis.duration_s
        if t_conv > constraints.max_transition_duration_s:
            warnings.append(
                f"Transition conversion duration ({t_conv:.1f} s) "
                f"exceeds safety threshold ({constraints.max_transition_duration_s:.1f} s)"
            )

        # Check stability margin
        margin = result.stability_analysis.min_stability_margin
        if margin < constraints.min_stability_margin_transition:
            warnings.append(
                f"Minimum transition stability margin ({margin * 100.0:.1f}%) "
                f"is below safety threshold ({constraints.min_stability_margin_transition * 100.0:.1f}%)"
            )

        # Authoritative corridor checks
        if result.authoritative_result is not None:
            corridor_issues = TransitionValidator.validate_corridor(result.authoritative_result)
            warnings.extend(corridor_issues)

        return warnings
