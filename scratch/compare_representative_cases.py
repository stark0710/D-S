import json
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.design_mode import DesignMode
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline
import backend.design.fixed_wing.tail.optimization.tail_optimizer as to_mod
from backend.design.fixed_wing.tail.optimization.objective_function import TailObjectiveFunction

class NormalizedTailObjectiveFunction(TailObjectiveFunction):
    @staticmethod
    def _calc_longitudinal_stability(c, ctx):
        V_h = c.derived_variables.get("V_h_actual", c.design_variables.get("horizontal_V_h", 0.55))
        return min(1.0, abs(V_h - 0.55) / 0.35)

    @staticmethod
    def _calc_directional_stability(c, ctx):
        V_v = c.derived_variables.get("V_v_actual", c.design_variables.get("vertical_V_v", 0.04))
        return min(1.0, abs(V_v - 0.04) / 0.04)

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
        return max(0.0, min(1.0, (area_ratio - 0.10) / (0.40 - 0.10)))

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
        return max(0.0, min(1.0, (vol_ratio - 0.05) / (0.20 - 0.05)))

    @staticmethod
    def _calc_cg_robustness(c, ctx):
        V_h = c.derived_variables.get("V_h_actual", c.design_variables.get("horizontal_V_h", 0.55))
        arm_ratio = c.design_variables.get("tail_arm_ratio", 0.55)
        deficit = float(max(0.0, 0.80 - V_h) + max(0.0, 0.65 - arm_ratio))
        return min(1.0, deficit / 0.70)

from scratch.run_representative_cases import CASES

def run_all_cases_comparison():
    with open("scratch/baseline_representative_results.json", "r") as f:
        baseline = json.load(f)

    orig_init = to_mod.TailOptimizer.__init__
    def patched_init(self):
        orig_init(self)
        self.objective = NormalizedTailObjectiveFunction()
    to_mod.TailOptimizer.__init__ = patched_init

    pipeline = FixedWingDesignPipeline()
    normalized_results = {}

    try:
        for name, req in CASES:
            res = pipeline.execute(req)
            spec = res.final_specification
            normalized_results[name] = {
                "success": res.success,
                "status": res.status.name,
                "iterations": res.iterations,
                "mtow": round(spec.mass_properties.maximum_takeoff_weight_kg, 4) if spec else None,
                "wing_area": round(spec.wing.wing_area, 4) if spec else None,
                "wingspan": round(spec.wing.wing_span, 4) if spec else None,
                "aspect_ratio": round(spec.wing.aspect_ratio, 2) if spec else None,
                "root_chord": round(spec.wing.root_chord, 4) if spec else None,
                "tail_config": spec.tail.tail_configuration if spec else None,
                "V_h": spec.tail.horizontal_volume_coefficient if spec else None,
                "V_v": spec.tail.vertical_volume_coefficient if spec else None,
                "tail_area": round(spec.tail.horizontal_tail_area_m2 + spec.tail.vertical_tail_area_m2, 4) if spec else None,
                "tail_s_h": spec.tail.horizontal_tail_area_m2 if spec else None,
                "tail_s_v": spec.tail.vertical_tail_area_m2 if spec else None,
                "tail_arm": spec.tail.tail_arm_m if spec else None,
                "cg_x": round(spec.cg.cg_position[0] if isinstance(spec.cg.cg_position, (list, tuple)) else spec.cg.cg_position, 4) if spec else None,
                "static_margin": round(spec.cg.static_margin, 2) if spec else None,
                "stall_speed": round(spec.performance.stall_speed_kmh, 2) if spec else None,
                "cruise_speed": round(spec.performance.cruise_speed_kmh, 2) if spec else None,
                "endurance_min": round(spec.performance.endurance_min, 2) if spec else None,
                "range_km": round(spec.performance.range_km, 2) if spec else None,
                "score": spec.tail.optimization_score if spec else None,
            }
    finally:
        to_mod.TailOptimizer.__init__ = orig_init

    print("\n=== BEFORE vs AFTER REGRESSION COMPARISON ===")
    all_matched = True
    for name in baseline:
        b = baseline[name]
        n = normalized_results[name]
        diffs = []
        for k in b:
            if k == "score":  # Score definition changed, so it will naturally differ
                continue
            if b[k] != n[k]:
                diffs.append(f"{k}: {b[k]} -> {n[k]}")
        if diffs:
            print(f"[{name}] CHANGED: {', '.join(diffs)}")
            all_matched = False
        else:
            print(f"[{name}] EXACT MATCH! MTOW={n['mtow']} Vh={n['V_h']} Vv={n['V_v']} Sh={n['tail_s_h']} Sv={n['tail_s_v']} arm={n['tail_arm']}")

    with open("scratch/normalized_representative_results.json", "w") as f:
        json.dump(normalized_results, f, indent=2)

if __name__ == "__main__":
    run_all_cases_comparison()
