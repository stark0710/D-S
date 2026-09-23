"""
DroneMissionValidator Subsystem

Purpose:
    Defines the `DroneMissionValidator` class responsible for validating multirotor mission profile completeness, consistency, and feasibility.

Role in Architecture:
    `DroneMissionValidator` checks input parameters, detects invalid or extreme bounds, and issues transparent engineering warnings.
"""

from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile


class DroneMissionValidator:
    """
    Validator for multirotor mission profiles.

    Design Principles:
        - Single Responsibility Principle: Multirotor mission completeness, consistency, and feasibility validation only.
    """

    def validate_mission(self, profile: DroneMissionProfile) -> list[str]:
        """
        Validates a DroneMissionProfile and returns a list of warnings.

        Args:
            profile (DroneMissionProfile): Target mission profile.

        Returns:
            list[str]: List of warning messages.
        """
        warnings: list[str] = []

        if profile.payload_weight_kg <= 0:
            warnings.append("Payload weight is zero or negative. Ensure valid payload mass requirement.")

        total_time = profile.target_hover_time_min + profile.target_cruise_time_min
        if total_time <= 0:
            warnings.append("Target flight time (hover + cruise) is zero or negative.")

        if total_time > 60.0:
            warnings.append(
                f"Target flight time ({total_time:.1f} min) exceeds typical multirotor battery energy density bounds (~45-60 min). "
                "Consider hybrid or high energy density battery chemistry."
            )

        if profile.payload_weight_kg > 15.0:
            warnings.append(
                f"High payload mass ({profile.payload_weight_kg:.1f} kg). "
                "Recommend heavy-lift multirotor configuration (Octocopter or coaxial Octo-quad)."
            )

        if profile.max_wind_speed_m_s > 15.0:
            warnings.append(
                f"High operational wind tolerance ({profile.max_wind_speed_m_s:.1f} m/s) requires high motor responsiveness "
                "and elevated thrust-to-weight ratio (>= 2.2)."
            )

        return warnings
