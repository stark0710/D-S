"""
DroneMissionAnalysis Subsystem

Purpose:
    Defines the `DroneMissionAnalysis` class responsible for multirotor mission decomposition and parameter estimation.

Role in Architecture:
    `DroneMissionAnalysis` derives estimated All-Up Weight (AUW) targets, hover power margins, and flight time targets
    from a `DroneMissionProfile`.
"""

from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.mission.drone_mission_requirements import DroneMissionRequirements
from backend.design.drone.mission.drone_mission_constraints import DroneMissionConstraints


class DroneMissionAnalysis:
    """
    Decomposition engine for multirotor mission profiles.

    Design Principles:
        - Single Responsibility Principle: Multirotor mission parameter decomposition and requirement derivation only.
    """

    def derive_requirements(self, profile: DroneMissionProfile) -> DroneMissionRequirements:
        """
        Derives DroneMissionRequirements from DroneMissionProfile.

        Args:
            profile (DroneMissionProfile): Target mission profile.

        Returns:
            DroneMissionRequirements: Derived multirotor engineering requirements.
        """
        # Multirotor payload fraction is typically 28-35% of MTOW/AUW
        payload = max(0.1, profile.payload_weight_kg)
        estimated_auw = round(payload * 3.3, 2)

        total_flight_time = profile.target_hover_time_min + profile.target_cruise_time_min

        hover_margin = 1.8
        if profile.max_wind_speed_m_s > 12.0:
            hover_margin = 2.2
        elif profile.max_wind_speed_m_s > 8.0:
            hover_margin = 2.0

        return DroneMissionRequirements(
            required_payload_kg=payload,
            estimated_auw_target_kg=estimated_auw,
            flight_time_target_min=total_flight_time,
            range_target_km=profile.target_range_km,
            hover_power_margin_min=hover_margin,
            cruise_speed_target_kmh=profile.cruise_speed_kmh,
            max_wind_tolerance_m_s=profile.max_wind_speed_m_s,
            redundancy_level=profile.required_redundancy,
            environmental_constraints={
                "altitude_m": profile.operating_altitude_m,
                "wind_m_s": profile.max_wind_speed_m_s
            },
            safety_margin_percent=20.0
        )

    def derive_constraints(
        self,
        profile: DroneMissionProfile,
        requirements: DroneMissionRequirements
    ) -> DroneMissionConstraints:
        """
        Derives DroneMissionConstraints from DroneMissionProfile and requirements.

        Args:
            profile (DroneMissionProfile): Target mission profile.
            requirements (DroneMissionRequirements): Derived requirements.

        Returns:
            DroneMissionConstraints: Derived physical & operational constraints.
        """
        max_mtow = round(requirements.estimated_auw_target_kg * 1.25, 2)
        min_tw = requirements.hover_power_margin_min

        # Estimate motor-to-motor diagonal size limit based on MTOW
        max_dim = 650.0
        if requirements.estimated_auw_target_kg > 10.0:
            max_dim = 1400.0
        elif requirements.estimated_auw_target_kg > 5.0:
            max_dim = 900.0

        return DroneMissionConstraints(
            max_takeoff_weight_kg=max_mtow,
            max_dimensions_mm=max_dim,
            min_thrust_to_weight_ratio=min_tw,
            max_current_draw_a=round(requirements.estimated_auw_target_kg * 30.0, 1),
            operating_temp_range=(-10.0, 45.0)
        )
