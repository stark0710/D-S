"""
Fixed-Wing Center of Gravity (CG) Optimization Objective Function
"""

from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate


class CGObjectiveFunction:
    """
    Computes a composite score measuring target static margin deviation, packaging order,
    mission configuration preferences, component movement minimization, and layout flexibility.
    """
    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self.weights = weights or {
            "target_stability": 0.30,
            "packaging_order": 0.20,
            "mission_suitability": 0.15,
            "minimal_movement": 0.15,
            "payload_flexibility": 0.20,
        }
        # Normalize weights
        total = sum(self.weights.values())
        self.weights = {k: v / total for k, v in self.weights.items()}

    def evaluate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> float:
        derived = candidate.derived_variables
        sm = derived["static_margin"]

        dv = candidate.design_variables
        bf = dv["battery_pos_fraction"]
        pf = dv["payload_pos_fraction"]
        af = dv["avionics_pos_fraction"]

        # Context category
        profile = getattr(context.requirements, "mission_result", None)
        if profile is not None:
            m_profile = profile.mission_profile
        else:
            m_profile = getattr(context.requirements, "mission_profile", None)
        category = getattr(m_profile, "mission_category", "MAPPING")
        cat_str = category.value if hasattr(category, "value") else str(category)

        # 1. Target Stability (prefer static stability margin close to 15%)
        score_stability = max(0.0, min(1.0, 1.0 - abs(sm - 0.15) / 0.05))

        # 2. Packaging Order (manufacturability - prefer flight controller forward, battery middle, payload aft)
        score_order = 1.0 if (af < bf and bf < pf) or (af < pf and pf < bf) else 0.70

        # 3. Mission Suitability (Survey/Mapping payload forward; Cargo/Delivery payload centered)
        if "mapping" in cat_str.lower() or "survey" in cat_str.lower():
            # mapping cameras need a clear view forward
            score_suitability = max(0.0, min(1.0, 1.0 - abs(pf - 0.30) / 0.30))
        elif "cargo" in cat_str.lower() or "delivery" in cat_str.lower():
            # cargo payload should be close to cg for neutral drop balance
            score_suitability = max(0.0, min(1.0, 1.0 - abs(pf - 0.45) / 0.20))
        else:
            score_suitability = 1.0

        # 4. Minimal Component Movement (relative to packaging default positions)
        dev = abs(bf - 0.35) + abs(pf - 0.28) + abs(af - 0.38)
        score_movement = max(0.0, min(1.0, 1.0 - dev / 1.5))

        # 5. Payload Flexibility (volume availability - leave space around cg/center)
        score_flex = max(0.0, min(1.0, 1.0 - abs(pf - bf)))

        scores = {
            "target_stability": score_stability,
            "packaging_order": score_order,
            "mission_suitability": score_suitability,
            "minimal_movement": score_movement,
            "payload_flexibility": score_flex,
        }

        candidate.objective_scores.update(scores)

        total_score = sum(scores[k] * self.weights[k] for k in self.weights)
        return total_score
