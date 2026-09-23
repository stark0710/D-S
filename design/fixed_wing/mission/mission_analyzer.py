"""
Fixed-Wing Mission Analyzer Subsystem

Purpose:
    Defines the `MissionAnalyzer` class, which conducts the engineering analysis of requirements.

Role in Architecture:
    `MissionAnalyzer` uses the selected `MissionStrategy`, `MissionClassifier`, and `MissionScoringService`
    to compute air density, estimate energy demands, evaluate risks, and assemble the final `MissionProfile`.
"""

import math
from typing import Dict, Any, List
from backend.design.fixed_wing.mission.mission_requirements import MissionRequirements, MissionCategory
from backend.design.fixed_wing.mission.mission_profile import MissionProfile
from backend.design.fixed_wing.mission.mission_strategy import MissionStrategy
from backend.design.fixed_wing.mission.mission_scoring import MissionScoringService


class MissionAnalyzer:
    """
    Coordinator service for fixed-wing mission analysis and profile construction.
    """

    def __init__(self, scoring_service: MissionScoringService | None = None) -> None:
        self._scoring_service = scoring_service if scoring_service else MissionScoringService()

    def analyze_mission(
        self, requirements: MissionRequirements, strategy: MissionStrategy
    ) -> MissionProfile:
        """
        Runs the full engineering analysis to construct a MissionProfile.

        Args:
            requirements (MissionRequirements): Clean and validated requirements.
            strategy (MissionStrategy): The strategy corresponding to the mission category.

        Returns:
            MissionProfile: Processed mission profile containing physics and operational indices.
        """
        # 1. Determine Standard Air Density based on operational altitude
        # Standard Atmosphere formula: rho = rho_0 * (1 - 2.25577e-5 * h) ^ 4.25588
        h = requirements.operational_altitude_m
        rho_0 = 1.225
        if h > 0.0:
            air_density = rho_0 * math.pow((1.0 - 0.0000225577 * h), 4.25588)
        else:
            air_density = rho_0

        # 2. Estimate Physics parameters using strategy
        physics = strategy.estimate_physics(requirements, air_density)

        # 3. Retrieve complexity indices from scoring service
        comp_score, comp_cat = self._scoring_service.calculate_complexity(requirements)

        # 4. Generate general summary
        summary = (
            f"Fixed-Wing {strategy.category.value} Mission Profile. "
            f"Payload: {requirements.payload_kg} kg, Endurance: {requirements.flight_time_min} min, "
            f"Speed: {requirements.cruise_speed_kmh} km/h, Altitude: {requirements.operational_altitude_m} m. "
            f"Est. Energy: {physics['energy_demand_kwh']:.2f} kWh. Complexity: {comp_cat}."
        )

        # 5. Construct the MissionProfile
        user_mtow = requirements.maximum_takeoff_weight_limit_kg
        seed_mtow = user_mtow if (user_mtow is not None and user_mtow > 0.0) else max(2.0, requirements.payload_kg * 3.5)

        profile = MissionProfile(
            mission_category=strategy.category,
            payload_kg=requirements.payload_kg,
            flight_time_min=requirements.flight_time_min,
            cruise_speed_kmh=requirements.cruise_speed_kmh,
            stall_speed_target_kmh=requirements.stall_speed_target_kmh,
            maximum_takeoff_weight_limit_kg=user_mtow,
            initial_mtow_seed_kg=seed_mtow,
            current_iteration_mtow_kg=seed_mtow,
            operational_altitude_m=requirements.operational_altitude_m,
            mission_range_km=requirements.mission_range_km,
            launch_method=requirements.launch_method,
            landing_method=requirements.landing_method,
            budget=requirements.budget,
            environment=requirements.environment,
            autonomy_level=requirements.autonomy_level,
            air_density_kg_m3=round(air_density, 4),
            energy_demand_kwh=physics["energy_demand_kwh"],
            cruise_emphasis=physics["cruise_emphasis"],
            payload_emphasis=physics["payload_emphasis"],
            launch_recovery_complexity=physics["launch_recovery_complexity"],
            environmental_complexity=physics["environmental_complexity"],
            operational_risk_score=physics["operational_risk_score"],
            mission_summary=summary,
            metadata={
                "complexity_score": comp_score,
                "complexity_category": comp_cat,
            }
        )

        return profile
