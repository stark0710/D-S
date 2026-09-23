"""
Fixed-Wing Payload Packaging Sizing Objective Function

Calculates candidate packaging score metrics based on layout characteristics.
"""

from backend.design.common.optimization.objective_function import ObjectiveFunction
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.optimization_utils import normalize_value

class PayloadObjectiveFunction(ObjectiveFunction):
    """
    Weighted multi-objective aggregator for payload layout optimization.
    """
    def __init__(
        self,
        w_pkg: float = 0.30,
        w_service: float = 0.20,
        w_routing: float = 0.20,
        w_cooling: float = 0.15,
        w_cg_flex: float = 0.15
    ) -> None:
        super().__init__()
        self.w_pkg = w_pkg
        self.w_service = w_service
        self.w_routing = w_routing
        self.w_cooling = w_cooling
        self.w_cg_flex = w_cg_flex

        # Lower score is better. Register targets.
        self.add_objective("packaging", self._calc_packaging_efficiency, weight=w_pkg, minimize=False)
        self.add_objective("serviceability", self._calc_serviceability, weight=w_service, minimize=False)
        self.add_objective("routing", self._calc_cable_routing, weight=w_routing, minimize=False)
        self.add_objective("cooling", self._calc_cooling, weight=w_cooling, minimize=False)
        self.add_objective("cg_flexibility", self._calc_cg_flexibility, weight=w_cg_flex, minimize=False)

    def _calc_packaging_efficiency(self, c: OptimizationCandidate, ctx: OptimizationContext) -> float:
        return float(c.derived_variables.get("packing_efficiency", 0.75))

    def _calc_serviceability(self, c: OptimizationCandidate, ctx: OptimizationContext) -> float:
        # Side-mounted or non-stacked electronics are easier to access and maintain
        e_mode = c.design_variables.get("electronics_layout_mode", "Side Mounted")
        scores = {
            "Side Mounted": 0.95,
            "Stacked Above": 0.80,
            "Stacked Below": 0.60
        }
        return float(scores.get(e_mode, 0.70))

    def _calc_cable_routing(self, c: OptimizationCandidate, ctx: OptimizationContext) -> float:
        # Having battery and electronics clustered reduces cabling lengths
        p_mode = c.design_variables.get("payload_position_mode")
        b_mode = c.design_variables.get("battery_position_mode")
        
        # If payload is forward, and battery is mid, routing is clean
        if p_mode == "Forward" and b_mode == "Mid":
            return 0.90
        return 0.70

    def _calc_cooling(self, c: OptimizationCandidate, ctx: OptimizationContext) -> float:
        # Stacked components block airflow, side-mounted cooling is best
        e_mode = c.design_variables.get("electronics_layout_mode", "Side Mounted")
        scores = {
            "Side Mounted": 0.90,
            "Stacked Above": 0.75,
            "Stacked Below": 0.65
        }
        return float(scores.get(e_mode, 0.70))

    def _calc_cg_flexibility(self, c: OptimizationCandidate, ctx: OptimizationContext) -> float:
        # Having battery in the center allows larger battery swapping without moving the center of gravity
        b_mode = c.design_variables.get("battery_position_mode")
        if b_mode == "Central" or b_mode == "Mid":
            return 0.95
        return 0.60
