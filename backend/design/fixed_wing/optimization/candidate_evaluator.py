"""
Fixed-Wing Wing Planform Candidate Evaluator

Coordinates with WingEngine to run complete multidisciplinary evaluations of a candidate.
"""

import math
from typing import Dict, Any, Type
from backend.design.fixed_wing.wing.wing_requirements import WingRequirements, PlanformType
from backend.design.fixed_wing.wing.wing_planform import PlanformGeometryService
from backend.design.fixed_wing.wing.wing_registry import WingStrategyRegistry
from backend.design.fixed_wing.wing.wing_strategy import WingStrategy
from backend.design.fixed_wing.wing.wing_engine import WingEngine
from backend.design.fixed_wing.wing.wing_result import WingResult
from backend.design.fixed_wing.optimization.optimization_models import PlanformCandidate

class OptimizedPlanformGeometryService(PlanformGeometryService):
    """
    Overridden planform service that injects optimized taper ratios and sweep angles.
    """
    def __init__(self, override_taper_ratio: float | None = None, override_sweep_deg: float | None = None) -> None:
        super().__init__()
        self.override_taper_ratio = override_taper_ratio
        self.override_sweep_deg = override_sweep_deg

    def calculate_planform_dimensions(
        self,
        planform: PlanformType,
        area_m2: float,
        aspect_ratio: float,
        sweep_angle_deg: float = 0.0,
    ) -> Dict[str, float]:
        sweep = self.override_sweep_deg if self.override_sweep_deg is not None else sweep_angle_deg
        dims = super().calculate_planform_dimensions(planform, area_m2, aspect_ratio, sweep)
        
        if self.override_taper_ratio is not None and planform != PlanformType.RECTANGULAR:
            taper = self.override_taper_ratio
            span = dims["span_m"]
            root_chord = (2.0 * area_m2) / (span * (1.0 + taper))
            tip_chord = taper * root_chord
            mac = (2.0 / 3.0) * root_chord * (1.0 + taper + taper**2) / (1.0 + taper)
            
            sweep_rad = math.radians(sweep)
            y_mac = (span / 6.0) * (1.0 + 2.0 * taper) / (1.0 + taper)
            quarter_chord_x = 0.25 * mac + y_mac * math.tan(sweep_rad)
            
            dims["root_chord_m"] = round(root_chord, 4)
            dims["tip_chord_m"] = round(tip_chord, 4)
            dims["taper_ratio"] = round(taper, 4)
            dims["mean_aerodynamic_chord_m"] = round(mac, 4)
            dims["quarter_chord_x_m"] = round(quarter_chord_x, 4)
            
        return dims

class CandidateEvaluator:
    """
    Evaluates a planform candidate by executing the standard WingEngine flow.
    """
    def __init__(self, engine: WingEngine | None = None) -> None:
        self._engine = engine if engine else WingEngine()

    def evaluate(self, candidate: PlanformCandidate, base_requirements: WingRequirements) -> WingResult:
        reqs = WingRequirements(
            mission_result=base_requirements.mission_result,
            configuration_result=base_requirements.configuration_result,
            preferred_planform=base_requirements.preferred_planform,
            preferred_aspect_ratio=candidate.aspect_ratio,
            preferred_wing_loading=candidate.wing_loading_kg_m2,
            metadata=base_requirements.metadata.copy()
        )

        category = base_requirements.mission_result.mission_profile.mission_category
        strategy_name = category.value if hasattr(category, 'value') else str(category)
        
        orig_strategy_cls = WingStrategyRegistry._registry.get(strategy_name.lower())
        if orig_strategy_cls is None:
            from backend.design.fixed_wing.wing.wing_strategy import BalancedWingStrategy
            orig_strategy_cls = BalancedWingStrategy

        class DynamicOverrideStrategy(orig_strategy_cls):
            def get_sweep_and_dihedral(self, requirements: WingRequirements):
                sweep, dihedral, incidence = super().get_sweep_and_dihedral(requirements)
                if candidate.sweep_angle_deg is not None:
                    sweep = candidate.sweep_angle_deg
                return sweep, dihedral, incidence

        WingStrategyRegistry.register(strategy_name, DynamicOverrideStrategy)
        
        orig_planform_service = self._engine._planform_service
        self._engine._planform_service = OptimizedPlanformGeometryService(
            override_taper_ratio=candidate.taper_ratio,
            override_sweep_deg=candidate.sweep_angle_deg
        )

        try:
            result = self._engine.process_wing_design(reqs)
            return result
        finally:
            WingStrategyRegistry.register(strategy_name, orig_strategy_cls)
            self._engine._planform_service = orig_planform_service
