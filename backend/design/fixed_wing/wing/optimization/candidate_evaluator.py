"""
Fixed-Wing Wing Planform Sizing Candidate Evaluator

Evaluates candidate parameters by calling standard WingEngine logic with injected overrides.
"""

from typing import Dict, Any
from backend.design.fixed_wing.wing.wing_requirements import WingRequirements
from backend.design.fixed_wing.wing.wing_planform import PlanformGeometryService
from backend.design.fixed_wing.wing.wing_registry import WingStrategyRegistry
from backend.design.fixed_wing.wing.wing_engine import WingEngine
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.candidate_evaluator_base import CandidateEvaluatorBase
from backend.design.fixed_wing.optimization.candidate_evaluator import OptimizedPlanformGeometryService

class CandidateEvaluator(CandidateEvaluatorBase):
    """
    Candidate evaluator interfacing with the production WingEngine framework.
    """
    def __init__(self, engine: WingEngine | None = None) -> None:
        self._engine = engine if engine else WingEngine()

    def evaluate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        # Get baseline requirements
        base_reqs = context.requirements
        
        ar = candidate.design_variables["aspect_ratio"]
        taper = candidate.design_variables["taper_ratio"]
        sweep = candidate.design_variables["sweep_angle_deg"]
        dihedral = candidate.design_variables["dihedral_angle_deg"]
        
        # Clone requirements and apply aspect ratio override
        reqs = WingRequirements(
            mission_result=base_reqs.mission_result,
            configuration_result=base_reqs.configuration_result,
            preferred_planform=base_reqs.preferred_planform,
            preferred_aspect_ratio=ar,
            preferred_wing_loading=base_reqs.preferred_wing_loading,
            metadata=base_reqs.metadata.copy()
        )

        category = base_reqs.mission_result.mission_profile.mission_category
        strategy_name = category.value if hasattr(category, 'value') else str(category)
        
        orig_strategy_cls = WingStrategyRegistry._registry.get(strategy_name.lower())
        if orig_strategy_cls is None:
            from backend.design.fixed_wing.wing.wing_strategy import BalancedWingStrategy
            orig_strategy_cls = BalancedWingStrategy

        # Override strategy sweep and dihedral angles
        class DynamicOverrideStrategy(orig_strategy_cls):
            def get_sweep_and_dihedral(self, requirements: WingRequirements):
                _, _, incidence = super().get_sweep_and_dihedral(requirements)
                return sweep, dihedral, incidence

        # Inject overrides
        WingStrategyRegistry.register(strategy_name, DynamicOverrideStrategy)
        
        orig_planform_service = self._engine._planform_service
        self._engine._planform_service = OptimizedPlanformGeometryService(
            override_taper_ratio=taper,
            override_sweep_deg=sweep
        )

        try:
            # Run wing design sizing
            result = self._engine.process_wing_design(reqs)
            
            # Map sizing outputs to derived variables
            geom = result.wing_geometry
            candidate.derived_variables["wing_span"] = geom.span_m
            candidate.derived_variables["wing_area"] = geom.area_m2
            candidate.derived_variables["root_chord"] = geom.root_chord_m
            candidate.derived_variables["tip_chord"] = geom.tip_chord_m
            candidate.derived_variables["mac"] = geom.mean_aerodynamic_chord_m
            candidate.derived_variables["wing_loading"] = geom.wing_loading_kg_m2
            candidate.derived_variables["wing_result"] = result
            candidate.derived_variables["estimated_mtow_kg"] = result.estimated_mtow_kg
            candidate.derived_variables["estimated_wing_weight_kg"] = result.estimated_wing_weight_kg
        finally:
            # Revert modifications
            WingStrategyRegistry.register(strategy_name, orig_strategy_cls)
            self._engine._planform_service = orig_planform_service
