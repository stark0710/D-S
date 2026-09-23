"""
Fixed-Wing Mission Validator Subsystem

Purpose:
    Defines the `MissionValidator` class, which validates raw user inputs for physical feasibility and consistency.

Role in Architecture:
    `MissionValidator` enforces limits and checks logical consistency between related mission parameters
    (e.g., ensuring cruise speed exceeds stall speed, range is consistent with speed/duration, etc.)
    before the mission is analyzed.
"""

from typing import List
from backend.design.fixed_wing.mission.mission_requirements import (
    MissionRequirements,
    LaunchMethod,
    LandingMethod,
)


class MissionValidationError(ValueError):
    """
    Exception raised when mission requirements fail validation.
    
    Attributes:
        errors (List[str]): List of validation error messages.
    """

    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class MissionValidator:
    """
    Validator for fixed-wing mission requirements.
    
    Design Principles:
        - Single Responsibility: Validating parameters and consistency.
        - Strict Type & Boundary Checks: Raises MissionValidationError on failures.
    """

    def validate(self, requirements: MissionRequirements) -> None:
        """
        Validates the given mission requirements.

        Args:
            requirements (MissionRequirements): Requirements to validate.

        Raises:
            MissionValidationError: If any validations fail.
        """
        errors: List[str] = []

        # 1. Payload Limits
        if requirements.payload_kg <= 0.0:
            errors.append(f"Payload capacity must be positive (got {requirements.payload_kg} kg)")
        elif requirements.payload_kg > 100.0:
            errors.append(f"Payload capacity exceeds maximum supported limit of 100 kg (got {requirements.payload_kg} kg)")

        # 2. Flight Time Targets
        if requirements.flight_time_min <= 0.0:
            errors.append(f"Flight time target must be positive (got {requirements.flight_time_min} minutes)")
        elif requirements.flight_time_min > 1440.0:
            errors.append(f"Flight time target exceeds maximum supported limit of 24 hours (got {requirements.flight_time_min} minutes)")

        # 3. Cruise Speed
        if requirements.cruise_speed_kmh <= 0.0:
            errors.append(f"Cruise speed must be positive (got {requirements.cruise_speed_kmh} km/h)")
        elif requirements.cruise_speed_kmh > 350.0:
            errors.append(f"Cruise speed exceeds maximum operational limit of 350 km/h (got {requirements.cruise_speed_kmh} km/h)")

        # 4. Range
        if requirements.mission_range_km <= 0.0:
            errors.append(f"Mission range must be positive (got {requirements.mission_range_km} km)")

        # 5. Budget
        if requirements.budget is not None and requirements.budget <= 0.0:
            errors.append(f"Budget must be positive (got {requirements.budget})")

        # 6. Launch & Landing Methods Validation
        # Verify launch_method and landing_method are from enums (handled by strong typing, but double check)
        if not isinstance(requirements.launch_method, LaunchMethod):
            errors.append(f"Invalid launch method: {requirements.launch_method}")
        if not isinstance(requirements.landing_method, LandingMethod):
            errors.append(f"Invalid landing method: {requirements.landing_method}")

        # 7. Mission Consistency & Physics Validation
        # Cruise speed must be greater than stall speed target if provided
        if requirements.stall_speed_target_kmh is not None:
            if requirements.stall_speed_target_kmh <= 0.0:
                errors.append(f"Stall speed target must be positive (got {requirements.stall_speed_target_kmh} km/h)")
            elif requirements.stall_speed_target_kmh >= requirements.cruise_speed_kmh:
                errors.append(
                    f"Stall speed target ({requirements.stall_speed_target_kmh} km/h) "
                    f"must be less than cruise speed ({requirements.cruise_speed_kmh} km/h)"
                )

        # MTOW limit must be greater than payload weight if provided
        if requirements.maximum_takeoff_weight_limit_kg is not None:
            if requirements.maximum_takeoff_weight_limit_kg <= 0.0:
                errors.append(f"Maximum takeoff weight limit must be positive (got {requirements.maximum_takeoff_weight_limit_kg} kg)")
            elif requirements.maximum_takeoff_weight_limit_kg <= requirements.payload_kg:
                errors.append(
                    f"Maximum takeoff weight limit ({requirements.maximum_takeoff_weight_limit_kg} kg) "
                    f"must be greater than payload weight ({requirements.payload_kg} kg)"
                )

        # Range must be physically consistent with speed and flight time.
        # Max theoretical range in flight_time at cruise_speed:
        max_theoretical_range = requirements.cruise_speed_kmh * (requirements.flight_time_min / 60.0)
        # We allow a small margin (e.g., tailwind, glide, etc.), say range can't exceed 1.5x theoretical range.
        if requirements.mission_range_km > max_theoretical_range * 1.5:
            errors.append(
                f"Mission range ({requirements.mission_range_km} km) is physically inconsistent with "
                f"cruise speed ({requirements.cruise_speed_kmh} km/h) and flight time ({requirements.flight_time_min} min). "
                f"Max theoretical range is {max_theoretical_range:.1f} km."
            )

        # Heavy payload vs Launch Method consistency
        if requirements.payload_kg > 12.0 and requirements.launch_method == LaunchMethod.HAND_LAUNCH:
            errors.append(
                f"Hand Launch is unsafe for payload mass of {requirements.payload_kg} kg. "
                "Select Catapult or Runway launch."
            )

        # Heavy payload vs Landing Method consistency
        if requirements.payload_kg > 20.0 and requirements.landing_method == LandingMethod.BELLY_LANDING:
            errors.append(
                f"Belly Landing is unsafe for heavy payload mass of {requirements.payload_kg} kg. "
                "Select Runway, Parachute, or Net Recovery landing."
            )

        if errors:
            raise MissionValidationError(errors)
