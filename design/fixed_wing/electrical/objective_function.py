"""
Electrical System Optimization Objective Function

Computes the weighted score of a candidate configuration across 8 design metrics.
"""

from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate


class ElectricalObjectiveFunction:
    """
    Evaluates fitness scores for valid electrical system configurations.
    """

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        # Default weights summing to 1.0
        self.weights = weights if weights else {
            "reliability": 0.20,
            "power_margin": 0.15,
            "weight": 0.15,
            "cost": 0.10,
            "manufacturability": 0.10,
            "serviceability": 0.10,
            "mission_compatibility": 0.10,
            "future_upgrade_margin": 0.10,
        }

    def evaluate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> float:
        """
        Calculates and returns the aggregated optimization score (between 0.0 and 1.0).
        """
        dv = candidate.design_variables
        derived = candidate.derived_variables

        fc = dv["flight_controller"]
        gps = dv["gps"]
        telemetry = dv["telemetry"]
        receiver = dv["receiver"]
        servo = dv["servo"]
        bec = dv["bec"]
        pm = dv["power_module"]
        payload = dv["mission_equipment"]
        layout = dv["power_distribution_layout"]

        # 1. Reliability (Max 1.0)
        # Redundant power layouts and triple-redundant flight controllers increase score
        fc_rel = 1.0 if fc["triple_redundant"] else 0.5
        layout_rel = 1.0 if layout == "Dual Redundant Bus" else 0.6
        reliability_score = 0.5 * fc_rel + 0.5 * layout_rel

        # 2. Power Margin (Max 1.0)
        # BEC margins and PM current headroom
        bec_margin_ratio = max(0.0, derived["bec_continuous_margin_a"] / bec["max_continuous_current_a"])
        pm_margin_ratio = max(0.0, derived["pm_continuous_margin_a"] / pm["max_continuous_current_a"])
        power_margin_score = 0.5 * bec_margin_ratio + 0.5 * pm_margin_ratio

        # 3. Low Weight (Max 1.0)
        # Lower mass is better. Normalize mass (typically 100g to 2000g)
        mass_g = derived["estimated_electrical_mass_g"]
        # Invert such that lower weight yields a higher score (min mass 50g, max mass 2000g)
        weight_score = max(0.0, 1.0 - (mass_g - 50.0) / 1950.0)

        # 4. Low Cost (Max 1.0)
        # Lower component cost is better. Sum cost of selected components.
        total_cost = (
            fc["price"]
            + gps["price"]
            + telemetry["price"]
            + receiver["price"]
            + (servo["price"] * dv["servo_count"])
            + bec["price"]
            + pm["price"]
            + payload["price"]
        )
        # Max expected cost is around $7000 (mainly due to FLIR Duo / MicaSense / YellowScan)
        cost_score = max(0.0, 1.0 - (total_cost - 100.0) / 25000.0)

        # 5. Manufacturability (Max 1.0)
        # Simple bus is easier to manufacture. XT60/XT90 connectors are standard.
        layout_mfg = 1.0 if layout == "Single Bus" else 0.5
        connector_name = derived["connector_name"]
        conn_mfg = 1.0 if "XT" in connector_name else 0.7
        manufacturability_score = 0.6 * layout_mfg + 0.4 * conn_mfg

        # 6. Serviceability (Max 1.0)
        # Standard connections and modular flight controllers are easier to service
        fc_serv = 1.0 if "Pixhawk" in fc["name"] or "Cube" in fc["name"] else 0.7
        conn_serv = 1.0 if "XT60" in connector_name or "XT90" in connector_name else 0.6
        serviceability_score = 0.5 * fc_serv + 0.5 * conn_serv

        # 7. Mission Compatibility (Max 1.0)
        # Higher score if GNSS supports dual frequencies or RTK for mapping, or range telemetry is high band
        profile = context.requirements.mission_result.mission_profile
        category = profile.mission_category.value if hasattr(profile.mission_category, "value") else str(profile.mission_category)
        
        comp_score = 0.5
        if category.lower() in ("survey", "mapping"):
            comp_score = 1.0 if gps["supports_rtk"] else 0.6
        elif category.lower() == "cargo":
            comp_score = 1.0 if fc["triple_redundant"] else 0.6
        elif category.lower() == "agriculture":
            comp_score = 1.0 if "Sprayer" in payload["name"] else 0.7
        
        mission_compatibility_score = comp_score

        # 8. Future Upgrade Margin (Max 1.0)
        # Number of spare interfaces (e.g. Ethernet, SPI are great for upgrades)
        fc_interfaces = fc["interfaces"]
        upgrade_score = len(fc_interfaces) / 5.0 # Max 5 interfaces
        future_upgrade_margin_score = min(1.0, upgrade_score)

        # Save scores to candidate dictionary
        candidate.objective_scores.update({
            "reliability": round(reliability_score, 4),
            "power_margin": round(power_margin_score, 4),
            "weight": round(weight_score, 4),
            "cost": round(cost_score, 4),
            "manufacturability": round(manufacturability_score, 4),
            "serviceability": round(serviceability_score, 4),
            "mission_compatibility": round(mission_compatibility_score, 4),
            "future_upgrade_margin": round(future_upgrade_margin_score, 4),
        })

        # Weighted aggregate sum
        total_score = (
            self.weights["reliability"] * reliability_score
            + self.weights["power_margin"] * power_margin_score
            + self.weights["weight"] * weight_score
            + self.weights["cost"] * cost_score
            + self.weights["manufacturability"] * manufacturability_score
            + self.weights["serviceability"] * serviceability_score
            + self.weights["mission_compatibility"] * mission_compatibility_score
            + self.weights["future_upgrade_margin"] * future_upgrade_margin_score
        )

        candidate.objective_scores["electrical_score"] = round(total_score, 4)
        return total_score
