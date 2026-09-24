"""
Fixed-Wing Tail Optimization Candidate Evaluator

Evaluates tail candidates by running them through the existing TailEngine sizing pipeline
via temporary strategy registry and sizer injections.
"""

from typing import Tuple
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.candidate_evaluator_base import CandidateEvaluatorBase
from backend.design.fixed_wing.tail.tail_sizer import TailSizer
from backend.design.fixed_wing.tail.tail_requirements import TailRequirements, TailConfigType
from backend.design.fixed_wing.tail.tail_registry import TailStrategyRegistry
from backend.design.fixed_wing.tail.tail_engine import TailEngine


class OptimizedTailSizer(TailSizer):
    """
    Overridden Tail Sizer that injects custom optimized tail arms.
    """
    def __init__(self, override_tail_arm_m: float | None = None) -> None:
        super().__init__()
        self.override_tail_arm_m = override_tail_arm_m

    def size_tail_arm(self, span_m: float, tail_style: TailConfigType, default_ratio: float) -> float:
        if self.override_tail_arm_m is not None:
            return self.override_tail_arm_m
        return super().size_tail_arm(span_m, tail_style, default_ratio)


class CandidateEvaluator(CandidateEvaluatorBase):
    """
    Evaluator that delegates engineering calculations to the existing TailEngine
    backend and populates the candidate's derived_variables.
    """

    def __init__(self, engine: TailEngine | None = None) -> None:
        self._engine = engine if engine else TailEngine()

    def evaluate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        dv = candidate.design_variables

        # ---- Extract upstream specifications ----
        wing_spec = None
        if context.previous_specifications:
            wing_spec = context.previous_specifications.get("WingPlanformOptimizer")
        wingspan = getattr(wing_spec, "span_m", 2.0)

        # ---- Resolve tail configuration enum ----
        config_str = dv["tail_configuration"]
        config_map = {
            "Conventional": TailConfigType.CONVENTIONAL,
            "T-Tail": TailConfigType.T_TAIL,
            "V-Tail": TailConfigType.V_TAIL,
            # Inverted V-Tail uses the same sizing math as V-Tail;
            # the dihedral sign (negative) distinguishes orientation.
            "Inverted V-Tail": TailConfigType.V_TAIL,
            "Twin Boom": TailConfigType.TWIN_BOOM,
        }
        tail_style = config_map.get(config_str, TailConfigType.CONVENTIONAL)

        # ---- Tail arm ----
        tail_arm = dv["tail_arm_ratio"] * wingspan

        # ---- Build cloned TailRequirements context ----
        base_reqs = context.requirements
        reqs = TailRequirements(
            mission_result=base_reqs.mission_result,
            configuration_result=base_reqs.configuration_result,
            wing_result=base_reqs.wing_result,
            airfoil_result=base_reqs.airfoil_result,
            preferred_tail_configuration=tail_style,
            metadata=base_reqs.metadata.copy() if base_reqs.metadata else {},
        )

        category = base_reqs.mission_result.mission_profile.mission_category
        strategy_name = category.value if hasattr(category, 'value') else str(category)

        orig_strategy_cls = TailStrategyRegistry._registry.get(strategy_name.lower())
        if orig_strategy_cls is None:
            from backend.design.fixed_wing.tail.tail_strategy import BalancedTailStrategy
            orig_strategy_cls = BalancedTailStrategy

        # Subclass the concrete strategy to inject candidate properties
        class DynamicOverrideTailStrategy(orig_strategy_cls):
            def get_target_volume_coefficients(self) -> Tuple[float, float]:
                return dv["horizontal_V_h"], dv["vertical_V_v"]

            def get_typical_aspect_ratios(self) -> Tuple[float, float]:
                return dv["horiz_ar"], dv["vert_ar"]

            def get_sweep_and_taper(self) -> Tuple[float, float, float, float]:
                return dv["horiz_sweep"], dv["horiz_taper"], dv["vert_sweep"], dv["vert_taper"]

        # Register dynamic strategy
        TailStrategyRegistry.register(strategy_name, DynamicOverrideTailStrategy)

        # Inject sizer override
        orig_sizer = self._engine._sizer
        self._engine._sizer = OptimizedTailSizer(override_tail_arm_m=tail_arm)

        try:
            result = self._engine.process_tail_design(reqs)
            h_tail = result.horizontal_tail
            v_tail = result.vertical_tail
            analysis = result.tail_analysis

            # Populate derived variables from the engine result
            candidate.derived_variables.update({
                "tail_arm_m": round(tail_arm, 3),
                "h_area_m2": h_tail.area_m2,
                "v_area_m2": v_tail.area_m2,
                "h_span_m": h_tail.span_m,
                "h_root_chord_m": h_tail.chord_root_m,
                "h_tip_chord_m": h_tail.chord_tip_m,
                "v_height_m": v_tail.height_m,
                "v_root_chord_m": v_tail.chord_root_m,
                "v_tip_chord_m": v_tail.chord_tip_m,
                "V_h_actual": analysis.horizontal_volume_coefficient,
                "V_v_actual": analysis.vertical_volume_coefficient,
                "pitch_stability_rating": analysis.pitch_stability_rating,
                "yaw_stability_rating": analysis.yaw_stability_rating,
                "pitch_control_authority": analysis.pitch_control_authority,
                "yaw_control_authority": analysis.yaw_control_authority,
                "trim_capability": analysis.trim_capability,
                "structural_simplicity_score": analysis.structural_simplicity_score,
                "manufacturability_score": analysis.manufacturability_score,
                "mission_suitability": analysis.mission_suitability,
            })
            candidate.derived_variables["tail_result"] = result
        finally:
            # Restore strategy and sizer
            TailStrategyRegistry.register(strategy_name, orig_strategy_cls)
            self._engine._sizer = orig_sizer
