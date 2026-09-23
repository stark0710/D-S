import math
from backend.design.fixed_wing.tail.optimization.tail_optimizer import TailOptimizer
from backend.design.fixed_wing.tail.optimization.candidate_generator import GridSearchCandidateGenerator
from backend.design.fixed_wing.tail.optimization.candidate_evaluator import CandidateEvaluator
from backend.design.fixed_wing.tail.optimization.constraints import build_tail_constraints
from backend.design.fixed_wing.tail.optimization.objective_function import TailObjectiveFunction
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.design_mode import DesignMode
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline

def test_proposed_normalization():
    class NormalizedTailObjectiveFunction(TailObjectiveFunction):
        @staticmethod
        def _calc_longitudinal_stability(c, ctx):
            V_h = c.derived_variables.get("V_h_actual", c.design_variables.get("horizontal_V_h", 0.55))
            target = 0.55
            max_dev = 0.35  # V_h range [0.35, 0.90]
            dev = abs(V_h - target)
            return min(1.0, dev / max_dev)

        @staticmethod
        def _calc_directional_stability(c, ctx):
            V_v = c.derived_variables.get("V_v_actual", c.design_variables.get("vertical_V_v", 0.04))
            target = 0.04
            max_dev = 0.04  # V_v range [0.02, 0.08]
            dev = abs(V_v - target)
            return min(1.0, dev / max_dev)

        @staticmethod
        def _calc_drag_penalty(c, ctx):
            h_area = c.derived_variables.get("h_area_m2", 0.0)
            v_area = c.derived_variables.get("v_area_m2", 0.0)
            total_area = float(h_area + v_area)
            wing_spec = ctx.previous_specifications.get("WingPlanformOptimizer") if ctx.previous_specifications else None
            wing_area = getattr(wing_spec, "wing_area", getattr(wing_spec, "area_m2", 0.4)) if wing_spec else 0.4
            if wing_area <= 0:
                wing_area = 0.4
            area_ratio = total_area / wing_area
            # Ratio typically 0.10 to 0.40
            min_ratio, max_ratio = 0.10, 0.40
            return max(0.0, min(1.0, (area_ratio - min_ratio) / (max_ratio - min_ratio)))

        @staticmethod
        def _calc_structural_weight(c, ctx):
            h_area = c.derived_variables.get("h_area_m2", 0.0)
            v_area = c.derived_variables.get("v_area_m2", 0.0)
            arm = c.derived_variables.get("tail_arm_m", 1.0)
            total_vol = float((h_area + v_area) * arm)
            wing_spec = ctx.previous_specifications.get("WingPlanformOptimizer") if ctx.previous_specifications else None
            wing_area = getattr(wing_spec, "wing_area", getattr(wing_spec, "area_m2", 0.4)) if wing_spec else 0.4
            wingspan = getattr(wing_spec, "wing_span", getattr(wing_spec, "span_m", 2.0)) if wing_spec else 2.0
            ref_vol = wing_area * wingspan
            if ref_vol <= 0:
                ref_vol = 0.8
            vol_ratio = total_vol / ref_vol
            # vol_ratio typically 0.05 to 0.20
            min_vol, max_vol = 0.05, 0.20
            return max(0.0, min(1.0, (vol_ratio - min_vol) / (max_vol - min_vol)))

        @staticmethod
        def _calc_cg_robustness(c, ctx):
            V_h = c.derived_variables.get("V_h_actual", c.design_variables.get("horizontal_V_h", 0.55))
            arm_ratio = c.design_variables.get("tail_arm_ratio", 0.55)
            deficit = float(max(0.0, 0.80 - V_h) + max(0.0, 0.65 - arm_ratio))
            max_deficit = 0.70
            return min(1.0, deficit / max_deficit)

    # Let's inspect term stats on mock tail context with this normalized objective
    from tests.design.fixed_wing.tail.optimization.test_tail_optimization import mock_tail_context
    # Run audit on mock context
    from scratch.inspect_tail_stats import inspect_tail_candidates
    # We can inject NormalizedTailObjectiveFunction into TailOptimizer
    orig_TailObjectiveFunction = TailOptimizer.__init__
    
    optimizer = TailOptimizer()
    optimizer.objective = NormalizedTailObjectiveFunction()
    
    from scratch.inspect_tail_stats import inspect_tail_candidates
    # Let's test on mock context
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED
    )
    pipeline = FixedWingDesignPipeline()
    # Temporarily monkeypatch TailOptimizer.objective
    import backend.design.fixed_wing.tail.optimization.tail_optimizer as to_mod
    orig_to_init = to_mod.TailOptimizer.__init__
    def patched_init(self):
        orig_to_init(self)
        self.objective = NormalizedTailObjectiveFunction()
    to_mod.TailOptimizer.__init__ = patched_init
    
    try:
        res = pipeline.execute(req)
        spec = res.final_specification
        print("NORMALIZED OBJECTIVE SURVEY 0.5kg RESULT:")
        print(f"Success: {res.success}, MTOW: {spec.mass_properties.maximum_takeoff_weight_kg:.4f}")
        print(f"Tail: {spec.tail.tail_configuration}, Vh={spec.tail.horizontal_volume_coefficient}, Vv={spec.tail.vertical_volume_coefficient}, Sh={spec.tail.horizontal_tail_area_m2}, Sv={spec.tail.vertical_tail_area_m2}, arm={spec.tail.tail_arm_m}, score={spec.tail.optimization_score}")
    finally:
        to_mod.TailOptimizer.__init__ = orig_to_init

if __name__ == "__main__":
    test_proposed_normalization()
