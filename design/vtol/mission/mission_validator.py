"""
VTOL Mission Requirements Validator Subsystem

Purpose:
    Defines the `MissionValidator` class, which validates raw user inputs
    for physical feasibility, consistency, and compliance.
"""

from typing import List
from backend.design.vtol.mission.mission_requirements import (
    MissionRequirements,
    TakeoffMethod,
    LandingMethod,
)


class MissionValidationError(ValueError):
    """
    Exception raised when VTOL mission requirements fail validation.
    """

    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class MissionValidator:
    """
    Validator enforcing logical consistency and feasibility checks across the
    hover, transition, and cruise flight regimes.
    """

    def validate(self, requirements: MissionRequirements) -> None:
        """
        Validates the VTOL mission requirements.

        Args:
            requirements (MissionRequirements): The requirements to validate.

        Raises:
            MissionValidationError: If any validation checks fail.
        """
        errors: List[str] = []

        # 1. Null Checks
        if requirements is None:
            raise MissionValidationError(["Requirements object is null."])

        # 2. General parameters
        if requirements.payload_kg <= 0.0:
            errors.append(f"Payload capacity must be positive (got {requirements.payload_kg} kg)")
        elif requirements.payload_kg > 500.0:
            errors.append(f"Payload capacity exceeds maximum supported limit of 500 kg (got {requirements.payload_kg} kg)")

        if requirements.max_altitude_m <= 0.0:
            errors.append(f"Maximum altitude must be positive (got {requirements.max_altitude_m} m)")
        elif requirements.max_altitude_m > 8000.0:
            errors.append(f"Maximum altitude exceeds physical limits (got {requirements.max_altitude_m} m)")

        if requirements.budget is not None and requirements.budget <= 0.0:
            errors.append(f"Budget must be positive (got {requirements.budget})")

        # 3. Hover Requirements Validation
        hover = requirements.hover_reqs
        if hover is None:
            errors.append("Hover requirements are missing.")
        else:
            if hover.hover_duration_min < 0.0:
                errors.append(f"Hover duration cannot be negative (got {hover.hover_duration_min} min)")
            if hover.hover_altitude_m < 0.0:
                errors.append(f"Hover altitude cannot be negative (got {hover.hover_altitude_m} m)")
            elif hover.hover_altitude_m > requirements.max_altitude_m:
                errors.append(f"Hover altitude ({hover.hover_altitude_m} m) cannot exceed maximum altitude ({requirements.max_altitude_m} m)")

            if hover.climb_rate_vertical_m_s <= 0.0:
                errors.append(f"Vertical climb rate must be positive (got {hover.climb_rate_vertical_m_s} m/s)")
            if hover.descent_rate_vertical_m_s <= 0.0:
                errors.append(f"Vertical descent rate must be positive (got {hover.descent_rate_vertical_m_s} m/s)")
            if hover.wind_limit_hover_kts < 0.0:
                errors.append(f"Hover wind limit cannot be negative (got {hover.wind_limit_hover_kts} kts)")

        # 4. Transition Requirements Validation
        trans = requirements.transition_reqs
        if trans is None:
            errors.append("Transition requirements are missing.")
        else:
            if trans.transition_speed_kmh <= 0.0:
                errors.append(f"Transition completion speed must be positive (got {trans.transition_speed_kmh} km/h)")
            if trans.transition_duration_s <= 0.0:
                errors.append(f"Transition duration must be positive (got {trans.transition_duration_s} s)")
            if trans.transition_altitude_m < 0.0:
                errors.append(f"Transition altitude cannot be negative (got {trans.transition_altitude_m} m)")
            elif trans.transition_altitude_m > requirements.max_altitude_m:
                errors.append(f"Transition altitude ({trans.transition_altitude_m} m) cannot exceed maximum altitude ({requirements.max_altitude_m} m)")

            if not (0.0 <= trans.max_transition_pitch_deg <= 90.0):
                errors.append(f"Max transition pitch must be between 0 and 90 degrees (got {trans.max_transition_pitch_deg})")

        # 5. Cruise Requirements Validation
        cruise = requirements.cruise_reqs
        if cruise is None:
            errors.append("Cruise requirements are missing.")
        else:
            if cruise.cruise_speed_kmh <= 0.0:
                errors.append(f"Cruise speed must be positive (got {cruise.cruise_speed_kmh} km/h)")
            elif cruise.cruise_speed_kmh > 450.0:
                errors.append(f"Cruise speed exceeds maximum supported VTOL speed (got {cruise.cruise_speed_kmh} km/h)")

            if cruise.cruise_altitude_m < 0.0:
                errors.append(f"Cruise altitude cannot be negative (got {cruise.cruise_altitude_m} m)")
            elif cruise.cruise_altitude_m > requirements.max_altitude_m:
                errors.append(f"Cruise altitude ({cruise.cruise_altitude_m} m) cannot exceed maximum altitude ({requirements.max_altitude_m} m)")

            if cruise.cruise_range_km <= 0.0:
                errors.append(f"Cruise range target must be positive (got {cruise.cruise_range_km} km)")
            if cruise.cruise_endurance_min <= 0.0:
                errors.append(f"Cruise endurance target must be positive (got {cruise.cruise_endurance_min} min)")
            if cruise.wind_limit_cruise_kts < 0.0:
                errors.append(f"Cruise wind limit cannot be negative (got {cruise.wind_limit_cruise_kts} kts)")

        # 6. Physical Consistency Checks
        if hover and cruise:
            if hover.wind_limit_hover_kts > cruise.wind_limit_cruise_kts:
                errors.append(
                    f"Hover wind limit ({hover.wind_limit_hover_kts} kts) cannot exceed "
                    f"cruise wind limit ({cruise.wind_limit_cruise_kts} kts) as hover is inherently more wind-sensitive."
                )

        if trans and cruise:
            if trans.transition_speed_kmh >= cruise.cruise_speed_kmh:
                errors.append(
                    f"Transition speed ({trans.transition_speed_kmh} km/h) must be less than "
                    f"cruise speed ({cruise.cruise_speed_kmh} km/h)."
                )

        if cruise:
            # Range vs endurance/speed consistency
            max_theoretical_range = cruise.cruise_speed_kmh * (cruise.cruise_endurance_min / 60.0)
            if cruise.cruise_range_km > max_theoretical_range * 1.5:
                errors.append(
                    f"Cruise range ({cruise.cruise_range_km} km) is physically inconsistent with "
                    f"cruise speed ({cruise.cruise_speed_kmh} km/h) and endurance ({cruise.cruise_endurance_min} min). "
                    f"Max range should not exceed 1.5x theoretical range ({max_theoretical_range:.1f} km)."
                )

        # 7. Takeoff & Landing Method Verification
        if requirements.takeoff_method == TakeoffMethod.VERTICAL:
            if hover and hover.hover_duration_min == 0.0:
                errors.append("Vertical Takeoff requires a positive hover duration.")
        if requirements.landing_method == LandingMethod.VERTICAL:
            if hover and hover.hover_duration_min == 0.0:
                errors.append("Vertical Landing requires a positive hover duration.")

        if errors:
            raise MissionValidationError(errors)
