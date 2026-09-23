"""
Fixed-Wing Aircraft Configuration Scoring Subsystem

Purpose:
    Defines the `ConfigurationScoringService` class to evaluate and score configuration options.

Role in Architecture:
    `ConfigurationScoringService` analyzes a proposed configuration layout against operational requirements
    to calculate indices for suitability, simplicity, aerodynamics, stability, maintenance, cost, and a combined score.
"""

from typing import Dict, Any, List
from backend.design.fixed_wing.configuration.configuration_requirements import (
    ConfigurationRequirements,
    WingPosition,
    PropulsionLayout,
    TailConfiguration,
    LandingGearConfiguration,
)
from backend.design.fixed_wing.configuration.configuration_profile import ConfigurationProfile


class ConfigurationScoringService:
    """
    Scoring service calculating engineering indices for aircraft configurations.
    """

    def score_configuration(
        self,
        requirements: ConfigurationRequirements,
        layout: Dict[str, str],
        profile: ConfigurationProfile | None = None,
    ) -> Dict[str, float]:
        """
        Computes detailed suitability, simplicity, cost, stability, maintenance, and aerodynamic scores
        for a layout configuration.

        Args:
            requirements (ConfigurationRequirements): Mission and user constraints.
            layout (Dict[str, str]): Layout mapping under evaluation.
            profile (ConfigurationProfile | None): Profile containing scoring weights.

        Returns:
            Dict[str, float]: Evaluation scores.
        """
        if profile is None:
            profile = ConfigurationProfile()

        # Extract requirements
        mission_profile = requirements.mission_result.mission_profile
        payload = mission_profile.payload_kg
        endurance = mission_profile.flight_time_min

        # Extract layout values
        wing = layout.get("wing_position", "High Wing")
        prop = layout.get("propulsion_layout", "Tractor")
        tail = layout.get("tail_configuration", "Conventional")
        gear = layout.get("landing_gear_configuration", "Tricycle")

        # 1. Structural Simplicity & Cost (Heuristics)
        simplicity = 100.0
        cost = 100.0

        if wing == WingPosition.PARASOL_WING.value:
            simplicity -= 15.0
            cost -= 10.0
        elif wing == WingPosition.MID_WING.value:
            simplicity -= 5.0

        if prop in (PropulsionLayout.TWIN_TRACTOR.value, PropulsionLayout.TWIN_PUSHER.value, PropulsionLayout.TWIN_BOOM_PUSHER.value):
            simplicity -= 25.0  # Twin engines are structurally complex
            cost -= 30.0
        elif prop == PropulsionLayout.DISTRIBUTED.value:
            simplicity -= 40.0
            cost -= 45.0

        if tail == TailConfiguration.TWIN_BOOM.value:
            simplicity -= 15.0
            cost -= 15.0
        elif tail == TailConfiguration.CANARD.value:
            simplicity -= 10.0
            cost -= 10.0

        if gear == LandingGearConfiguration.RETRACTABLE.value:
            simplicity -= 20.0
            cost -= 25.0
        elif gear == LandingGearConfiguration.SKID.value:
            simplicity += 10.0  # Skids are simpler than wheels
            cost += 10.0

        # 2. Aerodynamics & Stability
        aerodynamics = 70.0
        stability = 70.0

        if wing == WingPosition.HIGH_WING.value:
            stability += 15.0  # Passive roll stability (pendulum effect)
            aerodynamics += 5.0
        elif wing == WingPosition.LOW_WING.value:
            stability += 5.0
            aerodynamics += 2.0
        elif wing == WingPosition.MID_WING.value:
            aerodynamics += 8.0  # Cleanest aerodynamic wing-fuselage junction

        if prop == PropulsionLayout.PUSHER.value:
            aerodynamics += 5.0  # Laminar flow over nose
        elif prop == PropulsionLayout.TRACTOR.value:
            stability += 5.0  # Prop wash increases elevator/rudder authority at low speeds

        if tail == TailConfiguration.V_TAIL.value:
            aerodynamics += 8.0  # Reduced wetted area
            stability -= 5.0     # V-tails can suffer from Dutch roll or control coupling
        elif tail == TailConfiguration.TAILLESS.value or tail == TailConfiguration.FLYING_WING.value:
            aerodynamics += 15.0 # No tail drag
            stability -= 15.0    # Hard to stabilize passively in pitch

        if gear == LandingGearConfiguration.RETRACTABLE.value:
            aerodynamics += 15.0
        elif gear == LandingGearConfiguration.BELLY_LANDING.value:
            aerodynamics += 12.0  # No landing gear drag in flight

        # 3. Mission Suitability (Alignment with Category)
        suitability = 80.0
        category = mission_profile.mission_category.value if hasattr(mission_profile.mission_category, 'value') else mission_profile.mission_category

        if "Long Endurance" in category:
            # Long endurance needs low drag (belly/retractable gear, high wing, pusher/V-tail)
            if gear in (LandingGearConfiguration.SKID.value, LandingGearConfiguration.RETRACTABLE.value, LandingGearConfiguration.BELLY_LANDING.value):
                suitability += 10.0
            if wing == WingPosition.HIGH_WING.value:
                suitability += 5.0
        elif "Cargo" in category:
            # Cargo needs volume and runway gear (High wing, Twin engine, Tricycle gear)
            if wing == WingPosition.HIGH_WING.value:
                suitability += 10.0
            if prop in (PropulsionLayout.TWIN_TRACTOR.value, PropulsionLayout.TWIN_PUSHER.value):
                suitability += 10.0
            if gear == LandingGearConfiguration.TRICYCLE.value:
                suitability += 5.0
            if gear == LandingGearConfiguration.BELLY_LANDING.value:
                suitability -= 20.0
        elif "Survey" in category or "Mapping" in category:
            # Survey needs nose camera visibility (Pusher propulsion, High wing)
            if prop in (PropulsionLayout.PUSHER.value, PropulsionLayout.TWIN_BOOM_PUSHER.value):
                suitability += 10.0
            if wing == WingPosition.HIGH_WING.value:
                suitability += 5.0

        # 4. Maintenance Accessibility
        maintenance = 80.0
        if wing == WingPosition.HIGH_WING.value:
            maintenance += 5.0
        elif wing == WingPosition.PARASOL_WING.value:
            maintenance -= 5.0
        if prop in (PropulsionLayout.TWIN_TRACTOR.value, PropulsionLayout.TWIN_PUSHER.value):
            maintenance -= 15.0  # Twice the engines to maintain
        if gear == LandingGearConfiguration.RETRACTABLE.value:
            maintenance -= 10.0

        # Enforce boundaries (0.0 to 100.0)
        simplicity = max(0.0, min(100.0, simplicity))
        cost = max(0.0, min(100.0, cost))
        aerodynamics = max(0.0, min(100.0, aerodynamics))
        stability = max(0.0, min(100.0, stability))
        suitability = max(0.0, min(100.0, suitability))
        maintenance = max(0.0, min(100.0, maintenance))

        # 5. Calculate weighted overall score
        total_weight = (
            profile.structural_simplicity_weight
            + profile.manufacturability_weight
            + profile.aerodynamic_efficiency_weight
            + profile.cost_impact_weight
            + profile.stability_weight
            + profile.maintenance_weight
        )

        weighted_sum = (
            (simplicity * profile.structural_simplicity_weight)
            + (simplicity * profile.manufacturability_weight)  # simplicity correlates directly to manufacturability
            + (aerodynamics * profile.aerodynamic_efficiency_weight)
            + (cost * profile.cost_impact_weight)
            + (stability * profile.stability_weight)
            + (maintenance * profile.maintenance_weight)
        )

        overall_score = (weighted_sum / total_weight) * 0.6 + suitability * 0.4

        return {
            "suitability": round(suitability, 2),
            "simplicity": round(simplicity, 2),
            "manufacturability": round(simplicity * 0.95, 2),
            "aerodynamics": round(aerodynamics, 2),
            "stability": round(stability, 2),
            "maintenance": round(maintenance, 2),
            "cost": round(cost, 2),
            "overall_score": round(overall_score, 2),
        }
