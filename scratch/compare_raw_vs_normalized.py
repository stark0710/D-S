from tests.design.fixed_wing.tail.optimization.test_tail_optimization import mock_tail_context
from backend.design.fixed_wing.tail.optimization.tail_optimizer import TailOptimizer
from backend.design.fixed_wing.tail.optimization.objective_function import TailObjectiveFunction
from scratch.test_normalized_obj import test_proposed_normalization

def compare_raw_vs_normalized():
    # Setup mock tail context
    from tests.design.fixed_wing.tail.optimization.test_tail_optimization import (
        mock_tail_context,
    )
    # We will build context
    from backend.design.fixed_wing.mission.mission_requirements import (
        MissionCategory, LaunchMethod, LandingMethod, EnvironmentType, AutonomyLevel
    )
    from backend.design.fixed_wing.mission.mission_profile import MissionProfile
    from backend.design.fixed_wing.mission.mission_result import MissionResult
    from backend.design.fixed_wing.configuration.configuration_result import ConfigurationResult
    from backend.design.fixed_wing.wing.wing_geometry import WingGeometry
    from backend.design.fixed_wing.wing.wing_result import WingResult
    from backend.design.fixed_wing.airfoil.polar_analysis import PolarData
    from backend.design.fixed_wing.airfoil.performance_map import PerformanceMap
    from backend.design.fixed_wing.airfoil.reynolds_analysis import ReynoldsAnalysis
    from backend.design.fixed_wing.airfoil.airfoil_result import AirfoilResult
    from backend.design.fixed_wing.tail.tail_requirements import TailRequirements, TailConfigType
    from backend.design.fixed_wing.fuselage.optimization.models import FuselageSpecification
    from backend.design.fixed_wing.optimization.optimization_models import WingPlanformSpecification
    from backend.design.common.optimization.optimization_context import OptimizationContext
    from backend.design.common.requirements.optimization_priority import OptimizationPriority

    profile = MissionProfile(
        mission_category=MissionCategory.SURVEY,
        payload_kg=2.0, flight_time_min=60.0, cruise_speed_kmh=80.0,
        stall_speed_target_kmh=45.0, maximum_takeoff_weight_limit_kg=10.0,
        operational_altitude_m=150.0, mission_range_km=40.0,
        launch_method=LaunchMethod.CATAPULT, landing_method=LandingMethod.PARACHUTE,
        budget=10000.0, environment=EnvironmentType.RURAL,
        autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS, air_density_kg_m3=1.2,
        energy_demand_kwh=0.5, cruise_emphasis=0.7, payload_emphasis=0.3,
        launch_recovery_complexity=0.5, environmental_complexity=0.3,
        operational_risk_score=0.4, mission_summary="Survey mission",
    )
    m_result = MissionResult(
        mission_profile=profile, mission_category=MissionCategory.SURVEY,
        mission_score=85.0, complexity="Medium", engineering_requirements={},
        constraints=None, recommendations=[], warnings=[], metadata={},
    )
    c_result = ConfigurationResult(
        selected_configuration={
            "wing_position": "High Wing", "propulsion_layout": "Tractor",
            "tail_configuration": "Conventional", "landing_gear_configuration": "Tricycle",
        },
        configuration_score=85.0, wing_configuration="High Wing",
        propulsion_configuration="Tractor", tail_configuration="Conventional",
        landing_gear_configuration="Tricycle", engineering_rationale="Rationale",
        alternative_configurations=[],
    )
    wing_geom = WingGeometry(
        span_m=2.0, area_m2=0.4, aspect_ratio=10.0, wing_loading_kg_m2=20.0,
        root_chord_m=0.25, tip_chord_m=0.15, taper_ratio=0.6,
        sweep_angle_deg=0.0, dihedral_angle_deg=2.0, wing_incidence_deg=2.0,
        mean_aerodynamic_chord_m=0.22, quarter_chord_x_m=0.08, reference_area_m2=0.4,
    )
    w_result = WingResult(
        wing_geometry=wing_geom, planform="Tapered", reference_area=0.4,
        aspect_ratio=10.0, wing_loading=20.0, mean_aerodynamic_chord=0.22,
        quarter_chord_location=0.08, analysis=None,
    )
    polar = PolarData(
        airfoil_name="Clark Y", cruise_cl=0.45, cruise_cd=0.010, cruise_l_d=45.0,
        max_l_d=50.0, max_l_d_cl=0.5, max_lift_coeff=1.35, stall_angle_deg=14.0,
        pitching_moment_c_m0=-0.05,
    )
    perf_map = PerformanceMap("Clark Y", [], [], [], [])
    reynolds = ReynoldsAnalysis(0, 0, 0, 0, 0, "")
    a_result = AirfoilResult(
        selected_root_airfoil="Clark Y", selected_tip_airfoil="NACA 0012",
        airfoil_distribution="", polar_data=polar,
        performance_map=perf_map, reynolds_analysis=reynolds,
    )
    reqs = TailRequirements(
        mission_result=m_result, configuration_result=c_result,
        wing_result=w_result, airfoil_result=a_result,
    )
    wing_spec = WingPlanformSpecification(
        span_m=2.0, area_m2=0.4, aspect_ratio=10.0,
        mean_aerodynamic_chord_m=0.22, taper_ratio=0.6, sweep_angle_deg=0.0,
    )
    fuse_spec = FuselageSpecification(
        overall_length=1.3, width=0.20, height=0.20,
        nose_length=0.23, cabin_length=0.55, tail_cone_length=0.52,
        cross_section="Circular", fineness_ratio=8.0,
        wing_mount_position=0.416, payload_bay={}, battery_bay={},
        avionics_bay={}, bulkhead_locations=[],
        optimization_score=0.9, reasoning="Mock",
    )
    context = OptimizationContext(
        requirements=reqs,
        configuration=c_result,
        previous_specifications={
            "WingPlanformOptimizer": wing_spec,
            "FuselageOptimizer": fuse_spec,
        },
        optimization_priority=OptimizationPriority.BALANCED
    )

    # 1. Original Objective
    opt_orig = TailOptimizer()
    opt_orig.initialize(context)
    cands_orig = opt_orig.generate_candidates(context)
    feasible_orig = []
    for c in cands_orig:
        if opt_orig.apply_constraints(c, context):
            opt_orig.evaluate_candidate(c, context)
            opt_orig.score_candidate(c, context)
            feasible_orig.append(c)
    winner_orig = opt_orig.select_best_candidate(feasible_orig, context)

    # 2. Normalized Objective
    from scratch.test_normalized_obj import test_proposed_normalization
    # We define the normalized objective function instance
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

    opt_norm = TailOptimizer()
    opt_norm.objective = NormalizedTailObjectiveFunction()
    opt_norm.initialize(context)
    cands_norm = opt_norm.generate_candidates(context)
    feasible_norm = []
    for c in cands_norm:
        if opt_norm.apply_constraints(c, context):
            opt_norm.evaluate_candidate(c, context)
            opt_norm.score_candidate(c, context)
            feasible_norm.append(c)
    winner_norm = opt_norm.select_best_candidate(feasible_norm, context)

    print("=== COMPARISON TABLE ===")
    print(f"{'Objective Term':<25} | {'Weight':<6} | {'Original Raw':<14} | {'Orig Contrib':<14} | {'Norm Score':<12} | {'Norm Contrib':<14}")
    print("-" * 95)
    
    orig_contribs = []
    norm_contribs = []
    for t in opt_orig.objective._terms:
        mult = 1.0 if t.minimize else -1.0
        r_val = winner_orig.objective_scores[t.name]
        r_contrib = t.weight * r_val * mult
        orig_contribs.append(abs(r_contrib))

        n_val = winner_norm.objective_scores[t.name]
        n_contrib = t.weight * n_val * mult
        norm_contribs.append(abs(n_contrib))

        print(f"{t.name:<25} | {t.weight:<6.2f} | {r_val:<14.4f} | {r_contrib:<14.4f} | {n_val:<12.4f} | {n_contrib:<14.4f}")

    print("\nOriginal Contrib: min={:.4f}, max={:.4f}, ratio={:.1f}x".format(
        min(orig_contribs), max(orig_contribs), max(orig_contribs)/max(1e-9, min(orig_contribs))
    ))
    print("Normalized Contrib: min={:.4f}, max={:.4f}, ratio={:.1f}x".format(
        min(norm_contribs), max(norm_contribs), max(norm_contribs)/max(1e-9, min(norm_contribs))
    ))

if __name__ == "__main__":
    compare_raw_vs_normalized()
