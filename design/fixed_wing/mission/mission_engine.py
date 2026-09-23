"""
Fixed-Wing Mission Engine Subsystem

Purpose:
    Defines the `MissionEngine` class, which serves as the public orchestrator for the Fixed-Wing Mission Engineering Framework.

Role in Architecture:
    `MissionEngine` receives raw requirements, validates them, classifies the mission category,
    selects the strategy, triggers the analysis, scores the mission, and outputs the final `MissionResult`.
"""

from typing import List, Dict, Any
from datetime import datetime

from backend.design.fixed_wing.mission.mission_requirements import MissionRequirements, MissionCategory
from backend.design.fixed_wing.mission.mission_profile import MissionProfile
from backend.design.fixed_wing.mission.mission_constraints import MissionConstraints
from backend.design.fixed_wing.mission.mission_result import MissionResult
from backend.design.fixed_wing.mission.mission_validator import MissionValidator
from backend.design.fixed_wing.mission.mission_classifier import MissionClassifier
from backend.design.fixed_wing.mission.mission_registry import MissionStrategyRegistry
from backend.design.fixed_wing.mission.mission_analyzer import MissionAnalyzer
from backend.design.fixed_wing.mission.mission_scoring import MissionScoringService


class MissionEngine:
    """
    Orchestration engine (Facade) for the Fixed-Wing Mission Engineering Framework.
    
    Adheres to:
        - SOLID principles (Single Responsibility, Dependency Injection)
        - Clean Architecture (Orchestrates application workflow)
    """

    def __init__(
        self,
        validator: MissionValidator | None = None,
        classifier: MissionClassifier | None = None,
        analyzer: MissionAnalyzer | None = None,
        scoring_service: MissionScoringService | None = None,
    ) -> None:
        """
        Constructor injection for dependencies.
        """
        self._validator = validator if validator else MissionValidator()
        self._classifier = classifier if classifier else MissionClassifier()
        self._analyzer = analyzer if analyzer else MissionAnalyzer(scoring_service)
        self._scoring_service = scoring_service if scoring_service else MissionScoringService()

    def process_mission(self, requirements: MissionRequirements) -> MissionResult:
        """
        Captures, validates, and analyzes mission requirements to generate the official design record foundation.

        Args:
            requirements (MissionRequirements): Raw mission requirements from the user.

        Returns:
            MissionResult: Consolidated engineering result carrying constraints and profile.
        """
        # 1. Validate requirements (Raises MissionValidationError if invalid)
        self._validator.validate(requirements)

        # 2. Classify/Refine Mission Category
        category: MissionCategory = self._classifier.classify(requirements)

        # 3. Retrieve strategy from registry
        strategy = MissionStrategyRegistry.get(category)

        # 4. Perform Engineering Analysis (air density, energy, complexity ratings)
        profile: MissionProfile = self._analyzer.analyze_mission(requirements, strategy)

        # 5. Evaluate Feasibility and Scopes
        feasibility_score, warnings = self._scoring_service.calculate_feasibility(requirements)
        
        # Get complexity rating
        complexity_score = profile.metadata.get("complexity_score", 0.0)
        complexity_cat = profile.metadata.get("complexity_category", "Medium")

        # Consolidated overall mission score
        mission_score = self._scoring_service.calculate_mission_score(feasibility_score, complexity_score)

        # 6. Normalize requirements for downstream sizing tasks
        normalized_reqs = self._scoring_service.normalize_requirements(requirements)

        # 7. Define engineering constraints based on the profile
        constraints = MissionConstraints(
            minimum_payload_kg=requirements.payload_weight_kg if hasattr(requirements, 'payload_weight_kg') else requirements.payload_kg,
            minimum_range_km=requirements.mission_range_km,
            minimum_endurance_min=requirements.flight_time_min,
            target_cruise_speed_kmh=requirements.cruise_speed_kmh,
            maximum_stall_speed_kmh=requirements.stall_speed_target_kmh,
            maximum_takeoff_weight_kg=requirements.maximum_takeoff_weight_limit_kg,
            budget_limit=requirements.budget,
            required_launch_method=requirements.launch_method,
            required_landing_method=requirements.landing_method,
            operating_environment=requirements.environment,
            required_autonomy_level=requirements.autonomy_level,
        )

        # 8. Retrieve recommendations from strategy
        recommendations = strategy.get_recommendations(requirements, profile)

        # Add generic warning if feasibility is low
        if feasibility_score < 50.0:
            warnings.append("Mission feasibility is critical. Consider modifying payload or endurance constraints.")

        # 9. Compile metadata
        metadata = {
            "engine_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "feasibility_score": feasibility_score,
            "complexity_score": complexity_score,
            "source_category": requirements.mission_category.value,
        }

        # 10. Return compiled MissionResult
        return MissionResult(
            mission_profile=profile,
            mission_category=category,
            mission_score=mission_score,
            complexity=complexity_cat,
            engineering_requirements=normalized_reqs,
            constraints=constraints,
            recommendations=recommendations,
            warnings=warnings,
            metadata=metadata,
        )
