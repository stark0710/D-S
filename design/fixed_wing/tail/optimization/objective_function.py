"""
Fixed-Wing Tail Optimization Objective Function

Calculates weighted multi-objective scores for tail candidates based on
stability, drag, structural weight, manufacturability, mission suitability,
and future CG robustness.
"""

from backend.design.common.optimization.objective_function import ObjectiveFunction
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate


class TailObjectiveFunction(ObjectiveFunction):
    """
    Weighted multi-objective aggregator for tail design optimization.

    Lower overall score is better (objectives with minimize=False are negated
    by the base class, so maximising stability maps to lower total cost).
    """

    def __init__(
        self,
        w_long_stability: float = 0.25,
        w_dir_stability: float = 0.15,
        w_low_drag: float = 0.15,
        w_struct_weight: float = 0.10,
        w_manufacture: float = 0.15,
        w_mission: float = 0.10,
        w_cg_robustness: float = 0.10,
    ) -> None:
        super().__init__()
        # Register terms — all "minimize=True" terms want lower raw values to be better.
        self.add_objective(
            "longitudinal_stability",
            self._calc_longitudinal_stability,
            weight=w_long_stability,
            minimize=True,
        )
        self.add_objective(
            "directional_stability",
            self._calc_directional_stability,
            weight=w_dir_stability,
            minimize=True,
        )
        self.add_objective(
            "low_drag",
            self._calc_drag_penalty,
            weight=w_low_drag,
            minimize=True,
        )
        self.add_objective(
            "structural_weight",
            self._calc_structural_weight,
            weight=w_struct_weight,
            minimize=True,
        )
        self.add_objective(
            "manufacturability",
            self._calc_manufacturability,
            weight=w_manufacture,
            minimize=False,
        )
        self.add_objective(
            "mission_suitability",
            self._calc_mission_suitability,
            weight=w_mission,
            minimize=False,
        )
        self.add_objective(
            "cg_robustness",
            self._calc_cg_robustness,
            weight=w_cg_robustness,
            minimize=True,
        )

    # ------------------------------------------------------------------
    #  Objective term callbacks
    # ------------------------------------------------------------------

    @staticmethod
    def _calc_longitudinal_stability(
        c: OptimizationCandidate, ctx: OptimizationContext
    ) -> float:
        """Deviation of V_h from target (0.55) normalized across feasible bounds [0.35, 0.90]. Lower is better."""
        V_h = c.derived_variables.get("V_h_actual", c.design_variables.get("horizontal_V_h", 0.55))
        # Max deviation within feasible bounds: max(0.55 - 0.35, 0.90 - 0.55) = 0.35
        return min(1.0, abs(V_h - 0.55) / 0.35)

    @staticmethod
    def _calc_directional_stability(
        c: OptimizationCandidate, ctx: OptimizationContext
    ) -> float:
        """Deviation of V_v from target (0.04) normalized across feasible bounds [0.02, 0.08]. Lower is better."""
        V_v = c.derived_variables.get("V_v_actual", c.design_variables.get("vertical_V_v", 0.04))
        # Max deviation within feasible bounds: max(0.04 - 0.02, 0.08 - 0.04) = 0.04
        return min(1.0, abs(V_v - 0.04) / 0.04)

    @staticmethod
    def _calc_drag_penalty(
        c: OptimizationCandidate, ctx: OptimizationContext
    ) -> float:
        """Tail wetted area ratio relative to wing area, normalized to [0, 1]. Lower is better."""
        h_area = c.derived_variables.get("h_area_m2", 0.0)
        v_area = c.derived_variables.get("v_area_m2", 0.0)
        total_area = float(h_area + v_area)
        wing_spec = ctx.previous_specifications.get("WingPlanformOptimizer") if ctx and ctx.previous_specifications else None
        wing_area = getattr(wing_spec, "wing_area", getattr(wing_spec, "area_m2", 0.4)) if wing_spec else 0.4
        if wing_area <= 0.0:
            wing_area = 0.4
        area_ratio = total_area / wing_area
        # Typical feasible tail-to-wing area ratio spans [0.10, 0.40]
        return max(0.0, min(1.0, (area_ratio - 0.10) / (0.40 - 0.10)))

    @staticmethod
    def _calc_structural_weight(
        c: OptimizationCandidate, ctx: OptimizationContext
    ) -> float:
        """Tail volume proxy ((S_h + S_v) * arm) normalized against reference wing volume. Lower is better."""
        h_area = c.derived_variables.get("h_area_m2", 0.0)
        v_area = c.derived_variables.get("v_area_m2", 0.0)
        arm = c.derived_variables.get("tail_arm_m", 1.0)
        total_vol = float((h_area + v_area) * arm)
        wing_spec = ctx.previous_specifications.get("WingPlanformOptimizer") if ctx and ctx.previous_specifications else None
        wing_area = getattr(wing_spec, "wing_area", getattr(wing_spec, "area_m2", 0.4)) if wing_spec else 0.4
        wingspan = getattr(wing_spec, "wing_span", getattr(wing_spec, "span_m", 2.0)) if wing_spec else 2.0
        ref_vol = wing_area * wingspan
        if ref_vol <= 0.0:
            ref_vol = 0.8
        vol_ratio = total_vol / ref_vol
        # Typical empennage volume proxy ratio spans [0.05, 0.20]
        return max(0.0, min(1.0, (vol_ratio - 0.05) / (0.20 - 0.05)))

    @staticmethod
    def _calc_manufacturability(
        c: OptimizationCandidate, ctx: OptimizationContext
    ) -> float:
        """TailAnalysis manufacturability score (0–100) normalized to [0, 1]. Higher is better."""
        return c.derived_variables.get("manufacturability_score", 80.0) / 100.0

    @staticmethod
    def _calc_mission_suitability(
        c: OptimizationCandidate, ctx: OptimizationContext
    ) -> float:
        """TailAnalysis mission suitability score (0–100) normalized to [0, 1]. Higher is better."""
        return c.derived_variables.get("mission_suitability", 85.0) / 100.0

    @staticmethod
    def _calc_cg_robustness(
        c: OptimizationCandidate, ctx: OptimizationContext
    ) -> float:
        """Penalizes small tail volumes and short tail arms to favor CG robustness, normalized to [0, 1]. Lower is better."""
        V_h = c.derived_variables.get("V_h_actual", c.design_variables.get("horizontal_V_h", 0.55))
        arm_ratio = c.design_variables.get("tail_arm_ratio", 0.55)
        # Target: V_h >= 0.80 and arm_ratio >= 0.65. Max deficit across feasible space is 0.70
        deficit = float(max(0.0, 0.80 - V_h) + max(0.0, 0.65 - arm_ratio))
        return min(1.0, deficit / 0.70)
