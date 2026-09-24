"""
MissionFeasibilityAssessor Subsystem

Purpose:
    Defines the `MissionFeasibilityAssessor` class responsible for evaluating whether mission requirements
    are physically achievable within the studio design envelope.
"""

from backend.design.common.mission.mission_profile import MissionProfile
from backend.design.advisor.recommendation.mission_feasibility import MissionFeasibilityResult


class MissionFeasibilityAssessor:
    """
    Evaluator performing mission feasibility assessment across combined requirements.
    """

    # Engineering design envelope boundaries
    MAX_PAYLOAD_KG = 35.0
    MAX_RANGE_KM = 450.0
    MAX_ENDURANCE_MIN = 450.0
    MAX_CRUISE_SPEED_KMH = 300.0

    def assess(self, profile: MissionProfile) -> MissionFeasibilityResult:
        """
        Assesses whether the provided MissionProfile is physically feasible.

        Args:
            profile (MissionProfile): Target mission profile.

        Returns:
            MissionFeasibilityResult: Feasibility assessment outcome.
        """
        limiting_factors: list[str] = []
        reasons: list[str] = []
        warnings: list[str] = []

        payload = profile.payload_requirement
        rng = profile.range_requirement
        endurance = profile.flight_time_requirement
        speed = profile.cruise_speed_requirement

        # 1. Individual upper bound checks
        if payload > self.MAX_PAYLOAD_KG:
            limiting_factors.append("payload_weight_kg")
            reasons.append(f"Payload requirement ({payload:.1f} kg) exceeds maximum studio envelope limit ({self.MAX_PAYLOAD_KG:.1f} kg).")

        if rng > self.MAX_RANGE_KM:
            limiting_factors.append("target_range_km")
            reasons.append(f"Range requirement ({rng:.1f} km) exceeds maximum studio envelope limit ({self.MAX_RANGE_KM:.1f} km).")

        if endurance > self.MAX_ENDURANCE_MIN:
            limiting_factors.append("target_flight_time_min")
            reasons.append(f"Endurance requirement ({endurance:.1f} min) exceeds battery/fuel energy storage density limit ({self.MAX_ENDURANCE_MIN:.1f} min).")

        if speed > self.MAX_CRUISE_SPEED_KMH:
            limiting_factors.append("cruise_speed_kmh")
            reasons.append(f"Cruise speed requirement ({speed:.1f} km/h) exceeds platform dynamic limit ({self.MAX_CRUISE_SPEED_KMH:.1f} km/h).")

        # 2. Combined requirement checks
        if payload > 20.0 and rng > 200.0:
            limiting_factors.append("payload_range_combination")
            reasons.append(f"Combined heavy payload ({payload:.1f} kg) and extended range ({rng:.1f} km) exceeds structural MTOW limit.")

        if payload > 15.0 and endurance > 240.0:
            limiting_factors.append("payload_endurance_combination")
            reasons.append(f"Combined heavy payload ({payload:.1f} kg) and ultra-long endurance ({endurance:.1f} min) is physically unachievable.")

        # Near-limit warnings
        if payload > 25.0:
            warnings.append(f"High payload mass ({payload:.1f} kg) requires specialized heavy-lift structural airframe.")
        if rng > 300.0:
            warnings.append(f"Extended range target ({rng:.1f} km) approaches maximum battery energy density threshold.")

        is_feasible = (len(limiting_factors) == 0)
        confidence = 1.0 if is_feasible else 0.0

        return MissionFeasibilityResult(
            is_feasible=is_feasible,
            confidence=confidence,
            limiting_factors=limiting_factors,
            reasons=reasons,
            warnings=warnings,
        )
