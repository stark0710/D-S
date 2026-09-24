"""
Fixed-Wing Flight Performance Objective Function
"""

from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate


class FlightPerformanceObjectiveFunction:
    """
    Computes a composite score mapping aerodynamic efficiency, mission margins,
    energy consumption rates, excess rate of climb, and thrust/power reserves.
    """
    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self.weights = weights or {
            "mission_success": 0.25,
            "energy_efficiency": 0.20,
            "safety_margin": 0.15,
            "operational_perf": 0.15,
            "aerodynamic_eff": 0.15,
            "power_margin": 0.10,
        }
        # Normalize weights
        total = sum(self.weights.values())
        self.weights = {k: v / total for k, v in self.weights.items()}

    def evaluate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> float:
        derived = candidate.derived_variables
        res = derived["flight_result"]

        # 1. Mission Success (completion probability + range/endurance reserve)
        prob = res.mission_performance.mission_completion_probability
        score_mission = prob / 100.0

        # 2. Energy Efficiency (Wh/km rate)
        wh_km = derived["energy_consumption"]
        score_energy = max(0.0, min(1.0, 1.0 - (wh_km / 50.0)))

        # 3. Safety Margin (excess rate of climb over baseline)
        roc = derived["rate_of_climb"]
        score_safety = max(0.0, min(1.0, roc / 8.0))

        # 4. Operational Performance (top speed vs typical UAV speeds)
        v_max = derived["maximum_speed"]
        score_ops = max(0.0, min(1.0, v_max / 120.0))

        # 5. Aerodynamic Efficiency (L/D cruise ratio)
        best_ld = res.glide_analysis.glide_ratio
        score_aero = max(0.0, min(1.0, best_ld / 25.0))

        # 6. Power Margin (available vs required cruise power)
        req = derived["power_required"]
        avail = derived["power_available"]
        p_margin = (avail - req) / max(1.0, avail)
        score_power = max(0.0, min(1.0, p_margin))

        scores = {
            "mission_success": score_mission,
            "energy_efficiency": score_energy,
            "safety_margin": score_safety,
            "operational_perf": score_ops,
            "aerodynamic_eff": score_aero,
            "power_margin": score_power,
        }

        candidate.objective_scores.update(scores)

        total_score = sum(scores[k] * self.weights[k] for k in self.weights)
        return total_score
