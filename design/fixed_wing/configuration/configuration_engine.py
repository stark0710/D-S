"""
Fixed-Wing Aircraft Configuration Engine Subsystem

Purpose:
    Defines the `ConfigurationEngine` class, serving as the orchestrator for the
    Aircraft Configuration Engineering Framework.

Role in Architecture:
    `ConfigurationEngine` accepts the `MissionResult` and user preferences, invokes validators,
    delegates layout selection, scores alternatives, generates design advice, and produces the
    final `ConfigurationResult`.
"""

from typing import Dict, Any, List
from datetime import datetime

from backend.design.fixed_wing.configuration.configuration_requirements import ConfigurationRequirements
from backend.design.fixed_wing.configuration.configuration_profile import ConfigurationProfile
from backend.design.fixed_wing.configuration.configuration_result import ConfigurationResult
from backend.design.fixed_wing.configuration.configuration_strategy import ConfigurationStrategy
from backend.design.fixed_wing.configuration.configuration_validator import ConfigurationValidator
from backend.design.fixed_wing.configuration.configuration_registry import ConfigurationStrategyRegistry
from backend.design.fixed_wing.configuration.configuration_selector import ConfigurationSelector
from backend.design.fixed_wing.configuration.configuration_comparator import ConfigurationComparator
from backend.design.fixed_wing.configuration.configuration_recommender import ConfigurationRecommender


class ConfigurationEngine:
    """
    Facade class driving the aircraft architecture layout selection pipeline.
    """

    def __init__(
        self,
        validator: ConfigurationValidator | None = None,
        selector: ConfigurationSelector | None = None,
        comparator: ConfigurationComparator | None = None,
        recommender: ConfigurationRecommender | None = None,
    ) -> None:
        self._validator = validator if validator else ConfigurationValidator()
        self._selector = selector if selector else ConfigurationSelector()
        self._comparator = comparator if comparator else ConfigurationComparator()
        self._recommender = recommender if recommender else ConfigurationRecommender()

    def process_configuration(
        self,
        requirements: ConfigurationRequirements,
        profile: ConfigurationProfile | None = None,
    ) -> ConfigurationResult:
        """
        Determines the optimal configuration layout for the aircraft.

        Args:
            requirements (ConfigurationRequirements): Input wrapper holding mission context and user settings.
            profile (ConfigurationProfile | None): Optional weighting configuration profile.

        Returns:
            ConfigurationResult: The official architectural selection.
        """
        if profile is None:
            profile = ConfigurationProfile()

        mission_profile = requirements.mission_result.mission_profile
        category = mission_profile.mission_category

        # 1. Fetch matching strategy from registry
        # We can map standard MissionCategory names to ConfigurationStrategyRegistry lookup strings
        strategy_name = category.value if hasattr(category, 'value') else str(category)
        strategy = ConfigurationStrategyRegistry.get(strategy_name)

        # 2. Select layout and alternatives
        selection_data = self._selector.select_configuration(requirements, strategy, profile)
        best_layout = selection_data["selected_layout"]
        best_scores = selection_data["selected_scores"]
        alternatives = selection_data["alternatives"]

        # Prepare candidates list starting with primary candidate
        candidates = [{"layout": best_layout, "scores": best_scores, "is_fallback": False}]
        for alt in alternatives:
            candidates.append({"layout": alt["layout"], "scores": alt["scores"], "is_fallback": True})

        from backend.design.fixed_wing.configuration.configuration_validator import ConfigurationValidationError

        chosen_candidate = None
        validation_errors = []
        fallback_attempts = []
        primary_rej_reason = ""
        primary_layout_name = best_layout.get("architecture", "Primary Layout")

        for cand in candidates:
            if cand["is_fallback"]:
                fallback_attempts.append(cand["layout"].get("architecture"))
            try:
                warnings = self._validator.validate(requirements, cand["layout"])
                chosen_candidate = cand
                break
            except ConfigurationValidationError as e:
                err_msg = "; ".join(e.errors)
                validation_errors.append(f"{cand['layout'].get('architecture', 'Candidate')}: {err_msg}")
                if not cand["is_fallback"]:
                    primary_rej_reason = err_msg

        if chosen_candidate is None:
            # Raise configuration validation error if all options fail
            raise ConfigurationValidationError(errors=validation_errors)

        # Update best_layout and best_scores with chosen candidate
        best_layout = chosen_candidate["layout"]
        best_scores = chosen_candidate["scores"]
        is_fallback_active = chosen_candidate["is_fallback"]
        reason_won = "Alternative layout passed validation checks" if is_fallback_active else "Primary candidate is valid"

        # 4. Generate recommendations
        payload = mission_profile.payload_kg
        recommendations = self._recommender.generate_recommendations(best_layout, payload)
        
        # Merge strategy-specific recommendations
        strategy_recommendations = strategy.get_recommendations(requirements)
        for rec in strategy_recommendations:
            if rec not in recommendations:
                recommendations.append(rec)

        # 5. Extract engineering rationale
        rationale = strategy.get_engineering_rationale(requirements, best_layout)

        # 6. Format alternatives for output result
        alternative_configs: List[Dict[str, Any]] = []
        for alt in alternatives:
            alt_layout = alt["layout"]
            alt_scores = alt["scores"]
            
            # Run comparison of selected best layout vs this alternative
            comparison = self._comparator.compare(best_layout, alt_layout, best_scores, alt_scores)
            
            alternative_configs.append({
                "layout": alt_layout,
                "score": alt["score"],
                "rationale": alt["rationale"],
                "comparison": comparison,
            })

        metadata = {
            "engine_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "strategy_applied": strategy.name,
            "overall_score": best_scores["overall_score"],
            "primary_candidate": primary_layout_name,
            "primary_rejection_reason": primary_rej_reason,
            "fallback_candidates_attempted": fallback_attempts,
            "final_candidate_selected": best_layout.get("architecture"),
            "reason_final_candidate_won": reason_won,
        }

        # 7. Compile into ConfigurationResult
        return ConfigurationResult(
            selected_configuration=best_layout,
            configuration_score=best_scores["overall_score"],
            wing_configuration=best_layout.get("wing_position", "High Wing"),
            propulsion_configuration=best_layout.get("propulsion_layout", "Tractor"),
            tail_configuration=best_layout.get("tail_configuration", "Conventional"),
            landing_gear_configuration=best_layout.get("landing_gear_configuration", "Tricycle"),
            engineering_rationale=rationale,
            alternative_configurations=alternative_configs,
            recommendations=recommendations,
            warnings=warnings,
            metadata=metadata,
        )
