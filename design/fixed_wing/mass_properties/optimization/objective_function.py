"""
Fixed-Wing Mass Properties Optimization Objective Function
"""

from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate


class MassObjectiveFunction:
    """
    Computes a composite fitness score across empty weight, payload fraction,
    structural efficiency, manufacturability, energy efficiency, and growth margin.
    """
    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self.weights = weights or {
            "low_empty_weight": 0.20,
            "payload_fraction": 0.20,
            "structural_efficiency": 0.15,
            "manufacturability": 0.15,
            "energy_efficiency": 0.15,
            "growth_margin": 0.15,
        }
        # Normalize weights
        total = sum(self.weights.values())
        self.weights = {k: v / total for k, v in self.weights.items()}

    def evaluate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> float:
        derived = candidate.derived_variables
        empty_weight = derived["empty_weight_kg"]
        mtow = derived["mtow_kg"]
        payload_frac = derived["payload_fraction"]
        battery_frac = derived["battery_fraction"]
        struct_frac = derived["structural_fraction"]

        dv = candidate.design_variables
        fasteners = dv["fastener_allowance"]
        paint = dv["paint_finish_type"]
        safety_margin = dv["safety_growth_margin"]

        mtow_limit = getattr(context.requirements.mission_result.constraints, "maximum_takeoff_weight_kg", 25.0)

        # 1. Low Empty Weight (Minimize empty weight relative to MTOW limit)
        score_low_empty = max(0.0, min(1.0, 1.0 - (empty_weight / mtow_limit)))

        # 2. Payload Fraction (Maximize payload fraction)
        score_payload = max(0.0, min(1.0, payload_frac / 0.50))

        # 3. Structural Efficiency (Minimize structural fraction relative to limit)
        score_structure = max(0.0, min(1.0, 1.0 - struct_frac))

        # 4. Manufacturability (Standard fasteners and no/thin paint is easier to manufacture)
        paint_score = 1.0 if paint == "None" else 0.85
        fasteners_score = 1.0 if fasteners <= 0.03 else 0.90
        score_manufacturability = 0.5 * paint_score + 0.5 * fasteners_score

        # 5. Energy Efficiency (Minimize battery fraction overhead)
        score_energy = max(0.0, min(1.0, 1.0 - battery_frac))

        # 6. Future Growth Margin (Higher safety margins represent capacity for future sensor/structural expansion)
        score_growth = max(0.0, min(1.0, safety_margin / 0.15))

        # Compute weighted sum
        scores = {
            "low_empty_weight": score_low_empty,
            "payload_fraction": score_payload,
            "structural_efficiency": score_structure,
            "manufacturability": score_manufacturability,
            "energy_efficiency": score_energy,
            "growth_margin": score_growth,
        }

        candidate.objective_scores.update(scores)

        total_score = sum(scores[k] * self.weights[k] for k in self.weights)
        return total_score
