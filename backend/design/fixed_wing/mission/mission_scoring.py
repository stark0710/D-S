"""
Fixed-Wing Mission Scoring Subsystem

Purpose:
    Defines the `MissionScoringService` class, which computes feasibility, complexity,
    and normalized engineering scores for fixed-wing missions.

Role in Architecture:
    Calculates numerical indices for mission complexity, feasibility, and normalizes requirements
    for downstream sizing tasks.
"""

from typing import Dict, Any, Tuple
from backend.design.fixed_wing.mission.mission_requirements import MissionRequirements, EnvironmentType


class MissionScoringService:
    """
    Engineering calculator for mission scoring, complexity, and feasibility assessment.
    """

    def calculate_complexity(self, req: MissionRequirements) -> Tuple[float, str]:
        """
        Calculates a complexity score (0.0 to 100.0) and translates it to a category.

        Returns:
            Tuple[float, str]: (complexity_score, complexity_category)
        """
        points = 0.0

        # 1. Payload complexity
        if req.payload_kg < 1.0:
            points += 5.0
        elif req.payload_kg <= 5.0:
            points += 15.0
        elif req.payload_kg <= 15.0:
            points += 30.0
        else:
            points += 50.0

        # 2. Endurance complexity
        if req.flight_time_min < 30.0:
            points += 5.0
        elif req.flight_time_min <= 90.0:
            points += 15.0
        elif req.flight_time_min <= 240.0:
            points += 30.0
        else:
            points += 50.0

        # 3. Range complexity
        if req.mission_range_km < 15.0:
            points += 5.0
        elif req.mission_range_km <= 50.0:
            points += 15.0
        elif req.mission_range_km <= 150.0:
            points += 30.0
        else:
            points += 50.0

        # 4. Environmental penalties
        env = req.environment
        if env in (EnvironmentType.MOUNTAIN, EnvironmentType.MARINE):
            points += 15.0
        elif env in (EnvironmentType.DESERT, EnvironmentType.FOREST):
            points += 10.0
        elif env == EnvironmentType.URBAN:
            points += 20.0

        # Max points is 170. Normalize to a 0.0 - 100.0 scale.
        complexity_score = min(100.0, (points / 170.0) * 100.0)

        # Categorize
        if complexity_score < 25.0:
            category = "Low"
        elif complexity_score < 55.0:
            category = "Medium"
        elif complexity_score < 80.0:
            category = "High"
        else:
            category = "Very High"

        return round(complexity_score, 2), category

    def calculate_feasibility(self, req: MissionRequirements) -> Tuple[float, list[str]]:
        """
        Calculates the feasibility score (0.0 to 100.0) and generates feasibility warning notes.
        """
        score = 100.0
        warnings: list[str] = []

        # 1. Check extremely long endurance targets
        if req.flight_time_min > 300.0:
            penalty = (req.flight_time_min - 300.0) * 0.1
            score -= penalty
            warnings.append(f"Endurance target ({req.flight_time_min} min) is highly challenging for battery electric fixed-wings.")

        # 2. Check high payload weights
        if req.payload_kg > 20.0:
            penalty = (req.payload_kg - 20.0) * 1.5
            score -= penalty
            warnings.append(f"Heavy payload ({req.payload_kg} kg) increases wing loading and structural mass fraction significantly.")

        # 3. Check speed vs stall margins
        if req.stall_speed_target_kmh is not None:
            margin = req.cruise_speed_kmh - req.stall_speed_target_kmh
            if margin < 15.0:
                score -= 15.0
                warnings.append(f"Low speed margin ({margin:.1f} km/h) between cruise and stall speeds.")

        # 4. Check budget constraints
        if req.budget is not None:
            # Estimate a nominal cost based on requirements
            estimated_cost = 1000.0 + (req.payload_kg * 250.0) + (req.flight_time_min * 5.0)
            if req.budget < estimated_cost:
                deficit = estimated_cost - req.budget
                penalty = min(30.0, (deficit / estimated_cost) * 30.0)
                score -= penalty
                warnings.append(f"Budget constraint ({req.budget}) is tight compared to estimated cost of {estimated_cost:.0f}.")

        # 5. Check environmental difficulty
        if req.environment == EnvironmentType.URBAN:
            score -= 10.0
            warnings.append("Urban operational environments carry severe regulatory and obstacle hazards.")

        score = max(0.0, min(100.0, score))
        return round(score, 2), warnings

    def calculate_mission_score(self, feasibility: float, complexity: float) -> float:
        """
        Computes the consolidated overall mission score.
        A higher score means the mission requirements are well-defined, highly feasible, and well-balanced.
        """
        # Score is primarily based on feasibility with a slight discount for extreme complexity.
        score = feasibility * (1.0 - (complexity / 200.0))
        return round(score, 2)

    def normalize_requirements(self, req: MissionRequirements) -> Dict[str, Any]:
        """
        Normalizes requirements (e.g. speeds to m/s, payloads, range to meters, etc.)
        for downstream engineering scripts.
        """
        return {
            "payload_mass_kg": req.payload_kg,
            "flight_time_sec": req.flight_time_min * 60.0,
            "cruise_speed_m_s": req.cruise_speed_kmh / 3.6,
            "stall_speed_target_m_s": (req.stall_speed_target_kmh / 3.6) if req.stall_speed_target_kmh else None,
            "mission_range_m": req.mission_range_km * 1000.0,
            "operating_altitude_m": req.operational_altitude_m,
            "environment": req.environment.value,
            "launch_method": req.launch_method.value,
            "landing_method": req.landing_method.value,
            "autonomy_level": req.autonomy_level.value,
        }
