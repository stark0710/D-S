"""
Fixed-Wing Aircraft Configuration Selector Subsystem

Purpose:
    Defines the `ConfigurationSelector` class to orchestrate aircraft architecture selection.

Role in Architecture:
    `ConfigurationSelector` selects the primary layout using a strategy, scores it,
    evaluates other candidate options to rank them as alternatives, and compiles the selection.
"""

from typing import Dict, Any, List
from backend.design.fixed_wing.configuration.configuration_requirements import (
    ConfigurationRequirements,
    WingPosition,
    PropulsionLayout,
    TailConfiguration,
    LandingGearConfiguration,
)
from backend.design.fixed_wing.configuration.configuration_strategy import ConfigurationStrategy
from backend.design.fixed_wing.configuration.configuration_scoring import ConfigurationScoringService
from backend.design.fixed_wing.configuration.configuration_profile import ConfigurationProfile


class ConfigurationSelector:
    """
    Selector class to evaluate layout configurations and generate ranked alternatives.
    """

    def __init__(self, scoring_service: ConfigurationScoringService | None = None) -> None:
        self._scoring_service = scoring_service if scoring_service else ConfigurationScoringService()

    def select_configuration(
        self,
        requirements: ConfigurationRequirements,
        strategy: ConfigurationStrategy,
        profile: ConfigurationProfile,
    ) -> Dict[str, Any]:
        """
        Selects the best layout according to strategy, evaluates alternatives, and returns them.

        Args:
            requirements (ConfigurationRequirements): The input requirements.
            strategy (ConfigurationStrategy): The selected strategy.
            profile (ConfigurationProfile): Scoring weights profile.

        Returns:
            Dict[str, Any]: Dict containing:
                - 'selected_layout': Dict[str, str]
                - 'selected_scores': Dict[str, float]
                - 'alternatives': List[Dict[str, Any]]
        """
        # 1. Get strategy-selected best layout
        best_layout = strategy.select_best_layout(requirements)

        # 2. Score the best layout
        best_scores = self._scoring_service.score_configuration(requirements, best_layout, profile)

        # 3. Generate candidate alternative configurations for comparison
        candidates = self._get_comparison_candidates(requirements)
        
        alternatives: List[Dict[str, Any]] = []
        for candidate in candidates:
            # Skip if it is exactly the selected best layout
            if (
                candidate["wing_position"] == best_layout["wing_position"]
                and candidate["propulsion_layout"] == best_layout["propulsion_layout"]
                and candidate["tail_configuration"] == best_layout["tail_configuration"]
                and candidate["landing_gear_configuration"] == best_layout["landing_gear_configuration"]
            ):
                continue
                
            scores = self._scoring_service.score_configuration(requirements, candidate, profile)
            
            # Form explanation/rationale stub
            alt_rationale = (
                f"{candidate['architecture']} offers simplicity={scores['simplicity']} "
                f"and aerodynamics={scores['aerodynamics']}."
            )
            
            alternatives.append({
                "layout": candidate,
                "score": scores["overall_score"],
                "scores": scores,
                "rationale": alt_rationale,
            })

        # Sort alternatives by score descending
        alternatives.sort(key=lambda x: x["score"], reverse=True)

        return {
            "selected_layout": best_layout,
            "selected_scores": best_scores,
            "alternatives": alternatives,
        }

    def _get_comparison_candidates(self, requirements: ConfigurationRequirements) -> List[Dict[str, str]]:
        """Returns standard configuration layouts for comparison."""
        return [
            {
                "wing_position": WingPosition.HIGH_WING.value,
                "propulsion_layout": PropulsionLayout.TRACTOR.value,
                "tail_configuration": TailConfiguration.CONVENTIONAL.value,
                "landing_gear_configuration": LandingGearConfiguration.TRICYCLE.value,
                "engine_count": "1",
                "payload_arrangement": "CG Bay (Internal)",
                "architecture": "Conventional High-Wing Tractor (Utility)",
            },
            {
                "wing_position": WingPosition.HIGH_WING.value,
                "propulsion_layout": PropulsionLayout.PUSHER.value,
                "tail_configuration": TailConfiguration.CONVENTIONAL.value,
                "landing_gear_configuration": LandingGearConfiguration.BELLY_LANDING.value,
                "engine_count": "1",
                "payload_arrangement": "Nose Bay",
                "architecture": "High-Wing Rear Pusher (Survey / Glider)",
            },
            {
                "wing_position": WingPosition.HIGH_WING.value,
                "propulsion_layout": PropulsionLayout.TWIN_BOOM_PUSHER.value,
                "tail_configuration": TailConfiguration.TWIN_BOOM.value,
                "landing_gear_configuration": LandingGearConfiguration.SKID.value,
                "engine_count": "1",
                "payload_arrangement": "CG Bay (Internal)",
                "architecture": "Twin-Boom Pusher Monoplane",
            },
            {
                "wing_position": WingPosition.HIGH_WING.value,
                "propulsion_layout": PropulsionLayout.TWIN_TRACTOR.value,
                "tail_configuration": TailConfiguration.CONVENTIONAL.value,
                "landing_gear_configuration": LandingGearConfiguration.TRICYCLE.value,
                "engine_count": "2",
                "payload_arrangement": "Fuselage Cargo Bay",
                "architecture": "Twin-Engine High-Wing Cargo",
            },
            {
                "wing_position": WingPosition.LOW_WING.value,
                "propulsion_layout": PropulsionLayout.TRACTOR.value,
                "tail_configuration": TailConfiguration.CONVENTIONAL.value,
                "landing_gear_configuration": LandingGearConfiguration.TAILDRAGGER.value,
                "engine_count": "1",
                "payload_arrangement": "CG Tank",
                "architecture": "Low-Wing Tractor Sprayer",
            },
            {
                "wing_position": WingPosition.MID_WING.value,
                "propulsion_layout": PropulsionLayout.PUSHER.value,
                "tail_configuration": TailConfiguration.TAILLESS.value,
                "landing_gear_configuration": LandingGearConfiguration.BELLY_LANDING.value,
                "engine_count": "1",
                "payload_arrangement": "CG Bay (Internal)",
                "architecture": "Tailless Flying Wing Pusher",
            }
        ]
