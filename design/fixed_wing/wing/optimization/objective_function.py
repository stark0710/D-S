"""
Fixed-Wing Wing Planform Sizing Objective Function

Evaluates multi-objective scores across Aerodynamics, Structures, Mission,
Stability, Manufacturability, and Packaging parameters.
"""

from backend.design.common.optimization.objective_function import ObjectiveFunction
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.optimization_utils import normalize_value

class WingObjectiveFunction(ObjectiveFunction):
    """
    Weighted scoring aggregator for fixed-wing optimization goals.
    """
    def __init__(
        self,
        w_aero: float = 0.30,
        w_struct: float = 0.20,
        w_mission: float = 0.20,
        w_stability: float = 0.15,
        w_mfg: float = 0.10,
        w_pkg: float = 0.05
    ) -> None:
        super().__init__()
        self.w_aero = w_aero
        self.w_struct = w_struct
        self.w_mission = w_mission
        self.w_stability = w_stability
        self.w_mfg = w_mfg
        self.w_pkg = w_pkg

        # Register objectives. Lower overall score is better.
        self.add_objective("aerodynamics", self._calc_aerodynamics, weight=w_aero, minimize=False)
        self.add_objective("structures", self._calc_structures, weight=w_struct, minimize=True)
        self.add_objective("mission", self._calc_mission_suitability, weight=w_mission, minimize=False)
        self.add_objective("stability", self._calc_stability, weight=w_stability, minimize=False)
        self.add_objective("manufacturability", self._calc_manufacturability, weight=w_mfg, minimize=False)
        self.add_objective("packaging", self._calc_packaging, weight=w_pkg, minimize=False)

    def _calc_aerodynamics(self, c: OptimizationCandidate, ctx: OptimizationContext) -> float:
        res = c.derived_variables.get("wing_result")
        if not res or not res.analysis:
            return 10.0
        cl = getattr(res.analysis, "lift_coefficient_cruise", 0.5)
        cd = getattr(res.analysis, "drag_coefficient_cruise", 0.05)
        ld = cl / max(0.001, cd)
        return float(normalize_value(ld, 5.0, 25.0))

    def _calc_structures(self, c: OptimizationCandidate, ctx: OptimizationContext) -> float:
        res = c.derived_variables.get("wing_result")
        if not res:
            return 0.1

        # 1. Obtain MTOW from typed attributes
        mtow = getattr(res, "estimated_mtow_kg", None)
        if mtow is None:
            mtow = c.derived_variables.get("estimated_mtow_kg")
        if mtow is None:
            mtow = 5.0

        # 2. Obtain Wing weight from typed attributes
        wing_weight = getattr(res, "estimated_wing_weight_kg", None)
        if wing_weight is None:
            wing_weight = c.derived_variables.get("estimated_wing_weight_kg")
        if wing_weight is None:
            if hasattr(res, "wing_geometry") and res.wing_geometry:
                from backend.design.fixed_wing.wing.wing_sizer import DefaultWingStructure
                wing_weight = DefaultWingStructure().estimate_wing_weight_kg(res.wing_geometry, design_load_factor=4.0)
            else:
                wing_weight = 0.5

        fraction = wing_weight / max(0.1, mtow)
        return float(normalize_value(fraction, 0.05, 0.25))

    def _calc_mission_suitability(self, c: OptimizationCandidate, ctx: OptimizationContext) -> float:
        reqs = ctx.requirements
        if not reqs:
            return 1.0
        from backend.design.fixed_wing.wing.wing_registry import WingStrategyRegistry
        category = reqs.mission_result.mission_profile.mission_category
        strategy_name = category.value if hasattr(category, 'value') else str(category)
        strategy = WingStrategyRegistry.get(strategy_name)
        target_ar = strategy.get_target_aspect_ratio()
        
        ar = c.design_variables["aspect_ratio"]
        dev = abs(ar - target_ar) / max(1.0, target_ar)
        return float(max(0.0, 1.0 - dev))

    def _calc_stability(self, c: OptimizationCandidate, ctx: OptimizationContext) -> float:
        res = c.derived_variables.get("wing_result")
        if not res:
            return 1.0
        warnings_penalty = len(res.warnings)
        return float(max(0.0, 1.0 - 0.2 * warnings_penalty))

    def _calc_manufacturability(self, c: OptimizationCandidate, ctx: OptimizationContext) -> float:
        ar = c.design_variables["aspect_ratio"]
        sweep = c.design_variables["sweep_angle_deg"]
        ar_pen = (ar - 8.0) / 8.0
        sweep_pen = sweep / 10.0
        mfg_pen = 0.5 * max(0.0, ar_pen) + 0.5 * max(0.0, sweep_pen)
        return float(max(0.0, 1.0 - mfg_pen))

    def _calc_packaging(self, c: OptimizationCandidate, ctx: OptimizationContext) -> float:
        span = c.derived_variables.get("wing_span", 2.0)
        return float(max(0.0, 1.0 - (span / 4.0)))
