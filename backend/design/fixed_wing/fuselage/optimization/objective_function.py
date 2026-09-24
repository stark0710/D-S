"""
Fixed-Wing Fuselage Sizing Objective Function

Evaluates candidate multi-objective scores for internal volume packaging, structural mass fractions,
fineness ratio drag efficiency, cross-section shape manufacturability, static margin compliance,
and configuration suitabilities.
"""

from backend.design.common.optimization.objective_function import ObjectiveFunction
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.optimization_utils import normalize_value

class FuselageObjectiveFunction(ObjectiveFunction):
    """
    Weighted scoring aggregator for fuselage optimization objectives.
    """
    def __init__(
        self,
        w_pkg: float = 0.25,
        w_struct: float = 0.20,
        w_aero: float = 0.20,
        w_mfg: float = 0.15,
        w_cg: float = 0.15,
        w_mission: float = 0.05
    ) -> None:
        super().__init__()
        self.w_pkg = w_pkg
        self.w_struct = w_struct
        self.w_aero = w_aero
        self.w_mfg = w_mfg
        self.w_cg = w_cg
        self.w_mission = w_mission

        # Register objectives. Lower overall score is better.
        self.add_objective("packaging", self._calc_packaging_efficiency, weight=w_pkg, minimize=False)
        self.add_objective("structures", self._calc_structural_efficiency, weight=w_struct, minimize=True)
        self.add_objective("aerodynamics", self._calc_aerodynamic_efficiency, weight=w_aero, minimize=False)
        self.add_objective("manufacturability", self._calc_manufacturability, weight=w_mfg, minimize=False)
        self.add_objective("cg_margin", self._calc_cg_margin, weight=w_cg, minimize=False)
        self.add_objective("mission", self._calc_mission_suitability, weight=w_mission, minimize=False)

    def _calc_packaging_efficiency(self, c: OptimizationCandidate, ctx: OptimizationContext) -> float:
        res = c.derived_variables.get("fuselage_result")
        if not res or not res.fuselage_analysis:
            return 0.5
        # Proximity to ideal utilization (e.g. 60-80%)
        ratio = getattr(res.fuselage_analysis, "volume_utilization_ratio", 0.5)
        return float(normalize_value(ratio, 0.1, 0.9))

    def _calc_structural_efficiency(self, c: OptimizationCandidate, ctx: OptimizationContext) -> float:
        l = c.design_variables.get("length", 1.5)
        w = c.design_variables.get("width", 0.2)
        h = c.design_variables.get("height", 0.2)
        # Larger dimensions mean more surface area and thus higher structural weight
        mass_est = l * (w + h) * 4.0
        return float(normalize_value(mass_est, 0.5, 5.0))

    def _calc_aerodynamic_efficiency(self, c: OptimizationCandidate, ctx: OptimizationContext) -> float:
        # Proximity of Fineness Ratio to optimal L/D value of 8.0
        fr = c.design_variables.get("fineness_ratio", 8.0)
        dev = abs(fr - 8.0) / 8.0
        return float(max(0.0, 1.0 - dev))

    def _calc_manufacturability(self, c: OptimizationCandidate, ctx: OptimizationContext) -> float:
        # Shapes: Circular = 1.0, Rounded Rectangle = 0.9, Rectangular = 0.8, Oval = 0.7
        shape = c.design_variables.get("cross_section", "Circular")
        shape_scores = {
            "Circular": 1.0,
            "Rounded Rectangle": 0.9,
            "Rectangular": 0.8,
            "Oval": 0.7
        }
        return float(shape_scores.get(shape, 0.5))

    def _calc_cg_margin(self, c: OptimizationCandidate, ctx: OptimizationContext) -> float:
        res = c.derived_variables.get("fuselage_result")
        if not res or not res.component_placement:
            return 1.0
        margin = getattr(res.component_placement, "static_margin_pct", 15.0)
        # Proximity to 15.0% target
        dev = abs(margin - 15.0) / 15.0
        return float(max(0.0, 1.0 - dev))

    def _calc_mission_suitability(self, c: OptimizationCandidate, ctx: OptimizationContext) -> float:
        # Conventional fits standard mission categories
        res = c.derived_variables.get("fuselage_result")
        if not res:
            return 1.0
        # If no warnings, suitability is high
        warnings_penalty = len(res.warnings)
        return float(max(0.0, 1.0 - 0.2 * warnings_penalty))
