"""
MissionAnalysisService Subsystem

Purpose:
    Defines the `MissionAnalysisService` class, which performs rule-based, deterministic engineering interpretation of user requirements.

Role in Architecture:
    `MissionAnalysisService` translates a validated `RequirementModel` into a structured `MissionProfile`
    and `MissionAnalysisResult`. It calculates deterministic mission complexity scores without AI models or optimization.
"""

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.mission.mission_complexity import MissionComplexity
from backend.design.common.mission.mission_constraints import MissionConstraints
from backend.design.common.mission.mission_profile import MissionProfile
from backend.design.common.mission.mission_analysis_result import MissionAnalysisResult


class MissionAnalysisService:
    """
    Service for interpreting requirements into engineering mission profiles.

    Design Principles:
        - Single Responsibility Principle: Requirement analysis and profile construction only.
        - Deterministic & Explainable: Rule-based complexity scoring without stochastic AI models.
    """

    def analyze_requirements(self, requirements: RequirementModel) -> MissionAnalysisResult:
        """
        Translates a validated RequirementModel into a MissionAnalysisResult.

        Args:
            requirements (RequirementModel): Validated user requirement model.

        Returns:
            MissionAnalysisResult: Structured result carrying constructed MissionProfile.
        """
        notes: list[str] = []

        # 1. Assess deterministic mission complexity
        complexity, complexity_notes = self._assess_complexity(requirements)
        notes.extend(complexity_notes)

        # 2. Construct MissionConstraints
        constraints = MissionConstraints(
            minimum_payload_kg=requirements.payload_weight_kg,
            minimum_range_km=requirements.target_range_km,
            minimum_endurance_min=requirements.target_flight_time_min,
            required_takeoff_type=requirements.takeoff_type,
            required_landing_type=requirements.landing_type,
            operating_environment=requirements.environment,
            budget_limit=requirements.budget,
            weight_limit=requirements.maximum_takeoff_weight_kg
        )

        # 3. Generate engineering summary
        summary = self._generate_summary(requirements, complexity)

        # 4. Construct MissionProfile
        profile = MissionProfile(
            mission_type=requirements.mission_type,
            mission_summary=summary,
            payload_requirement=requirements.payload_weight_kg,
            range_requirement=requirements.target_range_km,
            flight_time_requirement=requirements.target_flight_time_min,
            cruise_speed_requirement=requirements.cruise_speed_kmh,
            takeoff_requirement=requirements.takeoff_type,
            landing_requirement=requirements.landing_type,
            environment=requirements.environment,
            optimization_priority=requirements.optimization_priority,
            mission_complexity=complexity,
            constraints=constraints,
            metadata={"source_mode": requirements.design_mode.value}
        )

        return MissionAnalysisResult(
            mission_profile=profile,
            analysis_notes=notes,
            metadata={"complexity_rating": complexity.value}
        )

    def _assess_complexity(self, req: RequirementModel) -> tuple[MissionComplexity, list[str]]:
        """Evaluates deterministic rule-based complexity points."""
        score = 0
        notes: list[str] = []

        # Payload scoring
        if req.payload_weight_kg < 1.0:
            score += 0
        elif req.payload_weight_kg <= 5.0:
            score += 1
            notes.append("Medium payload mass (1-5 kg).")
        elif req.payload_weight_kg <= 15.0:
            score += 2
            notes.append("Heavy payload mass (5-15 kg).")
        else:
            score += 3
            notes.append("Very heavy payload mass (> 15 kg).")

        # Range scoring
        if req.target_range_km < 10.0:
            score += 0
        elif req.target_range_km <= 30.0:
            score += 1
            notes.append("Moderate operational range (10-30 km).")
        elif req.target_range_km <= 100.0:
            score += 2
            notes.append("Extended operational range (30-100 km).")
        else:
            score += 3
            notes.append("Long-range operational target (> 100 km).")

        # Endurance scoring
        if req.target_flight_time_min < 30.0:
            score += 0
        elif req.target_flight_time_min <= 60.0:
            score += 1
            notes.append("Moderate endurance (30-60 min).")
        elif req.target_flight_time_min <= 120.0:
            score += 2
            notes.append("High endurance (60-120 min).")
        else:
            score += 3
            notes.append("Ultra-high endurance target (> 120 min).")

        # Environment scoring
        if req.environment in (OperatingEnvironment.URBAN, OperatingEnvironment.FOREST):
            score += 1
            notes.append(f"Environmental complexity penalty for {req.environment.value}.")
        elif req.environment in (OperatingEnvironment.MOUNTAIN, OperatingEnvironment.DESERT, OperatingEnvironment.MARINE):
            score += 2
            notes.append(f"Severe environmental complexity penalty for {req.environment.value}.")

        # Classify score
        if score <= 2:
            complexity = MissionComplexity.VERY_LOW
        elif score <= 4:
            complexity = MissionComplexity.LOW
        elif score <= 6:
            complexity = MissionComplexity.MEDIUM
        elif score <= 8:
            complexity = MissionComplexity.HIGH
        else:
            complexity = MissionComplexity.VERY_HIGH

        notes.insert(0, f"Assessed mission complexity: {complexity.value} (Score: {score}).")
        return complexity, notes

    def _generate_summary(self, req: RequirementModel, complexity: MissionComplexity) -> str:
        """Generates a structured human-readable engineering mission summary."""
        return (
            f"Mission Summary for {req.mission_type.value} operation: "
            f"Payload={req.payload_weight_kg} kg, Endurance={req.target_flight_time_min} min, "
            f"Range={req.target_range_km} km, Cruise Speed={req.cruise_speed_kmh} km/h in {req.environment.value} environment. "
            f"Assessed Complexity Level: {complexity.value}."
        )
