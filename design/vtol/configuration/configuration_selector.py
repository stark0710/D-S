"""
VTOL Configuration Selector Subsystem

Purpose:
    Defines the `ConfigurationSelector` class responsible for scoring candidate layouts
    and picking the optimal architecture.
"""

from typing import Dict, Tuple
from backend.design.vtol.mission.mission_requirements import VTOLType, TakeoffMethod
from backend.design.vtol.configuration.configuration_requirements import ConfigurationRequirements
from backend.design.vtol.configuration.configuration_strategy import ConfigurationStrategy


class ConfigurationSelector:
    """
    Selects the optimal mechanical configuration based on candidate layout scoring.
    """

    def select_best_layout(
        self, requirements: ConfigurationRequirements, strategy: ConfigurationStrategy
    ) -> Tuple[VTOLType, Dict[VTOLType, float]]:
        """
        Scores all candidate VTOL configurations and selects the optimal layout.

        Args:
            requirements (ConfigurationRequirements): User preferences and mission result.
            strategy (ConfigurationStrategy): Selected configuration strategy.

        Returns:
            Tuple[VTOLType, Dict[VTOLType, float]]: The selected configuration and candidate scores.
        """
        # If user explicitly preferred a layout, respect it but still compile candidates
        preferred = requirements.preferred_vtol_type

        candidates = [
            VTOLType.QUADPLANE,
            VTOLType.TILT_ROTOR,
            VTOLType.TILT_WING,
            VTOLType.LIFT_CRUISE,
            VTOLType.TAIL_SITTER,
            VTOLType.VECTORED_THRUST,
            VTOLType.TWIN_BOOM_VTOL,
            VTOLType.BOX_WING_VTOL,
            VTOLType.HYBRID_VTOL,
            VTOLType.CUSTOM,
        ]

        scores: Dict[VTOLType, float] = {}
        mission_res = requirements.mission_result
        payload = mission_res.mission_profile.payload_kg
        range_km = mission_res.mission_profile.total_range_km
        wind_kts = mission_res.hover_requirements.wind_limit_hover_kts

        for candidate in candidates:
            # Base score from strategy
            score = strategy.score_vtol_type(candidate)

            # Fine-tune based on physical performance limits
            if candidate == VTOLType.TAIL_SITTER:
                if payload > 8.0:
                    score -= 15.0  # Tail sitters have difficulty balancing heavy payloads
                if wind_kts > 20.0:
                    score -= 10.0  # Wind makes landing a tail sitter vertically highly challenging

            elif candidate == VTOLType.TILT_WING:
                if wind_kts > 18.0:
                    score -= 15.0  # High wing chord area acts as sail in crosswind hover/transition

            elif candidate == VTOLType.QUADPLANE:
                if range_km > 100.0:
                    score -= 15.0  # Fixed lift propellers generate heavy parasitic drag in cruise

            elif candidate == VTOLType.LIFT_CRUISE:
                if range_km > 150.0:
                    score -= 10.0  # Parasitic boom drag limits high-range performance

            scores[candidate] = round(max(0.0, score), 1)

        # Select winner
        if preferred is not None and preferred in scores:
            selected = preferred
        else:
            # Pick highest score
            selected = max(scores, key=scores.get)

        return selected, scores
