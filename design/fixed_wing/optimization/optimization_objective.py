"""
Fixed-Wing Wing Planform Optimization Objective

Defines the scoring objective functions to evaluate and rank wing design candidates.
"""

from backend.design.fixed_wing.wing.wing_result import WingResult
from backend.design.fixed_wing.optimization.optimization_models import PlanformCandidate

class OptimizationObjective:
    """
    Base class for calculating planform candidate optimization scores.
    """
    def calculate_score(self, candidate: PlanformCandidate, result: WingResult) -> float:
        raise NotImplementedError("Subclasses must implement calculate_score().")

class WeightedMultiObjective(OptimizationObjective):
    """
    Calculates a composite cost score where lower is better.
    Balances structural mass minimization with aerodynamic efficiency (L/D) maximization.
    """
    def __init__(self, w_mass: float = 10.0, w_ld: float = 1.0, w_warnings: float = 5.0) -> None:
        self.w_mass = w_mass
        self.w_ld = w_ld
        self.w_warnings = w_warnings

    def calculate_score(self, candidate: PlanformCandidate, result: WingResult) -> float:
        # 1. Obtain wing weight from typed attributes
        wing_weight = getattr(result, "estimated_wing_weight_kg", None)
        if wing_weight is None:
            if hasattr(result, "wing_geometry") and result.wing_geometry:
                from backend.design.fixed_wing.wing.wing_sizer import DefaultWingStructure
                wing_weight = DefaultWingStructure().estimate_wing_weight_kg(result.wing_geometry, design_load_factor=4.0)
            else:
                wing_weight = 0.5

        # 2. Extract Lift-to-Drag ratio estimation from aerodynamic analysis
        ld_ratio = 10.0
        if hasattr(result, "analysis") and result.analysis:
            cl = getattr(result.analysis, "lift_coefficient_cruise", 0.5)
            cd = getattr(result.analysis, "drag_coefficient_cruise", 0.05)
            ld_ratio = cl / max(0.001, cd)

        # 3. Warning penalties
        warnings_count = len(result.warnings)

        # Compute cost (lower is better)
        cost = (self.w_mass * wing_weight) - (self.w_ld * ld_ratio) + (self.w_warnings * warnings_count)
        return float(cost)
