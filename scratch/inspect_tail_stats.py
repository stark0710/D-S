import numpy as np
from backend.design.fixed_wing.tail.optimization.tail_optimizer import TailOptimizer
from backend.design.fixed_wing.tail.optimization.candidate_generator import GridSearchCandidateGenerator
from backend.design.fixed_wing.tail.optimization.candidate_evaluator import CandidateEvaluator
from backend.design.fixed_wing.tail.optimization.constraints import build_tail_constraints
from backend.design.fixed_wing.tail.optimization.objective_function import TailObjectiveFunction
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment

def inspect_tail_candidates():
    # Set up mock tail context similar to unit test
    from tests.design.fixed_wing.tail.optimization.test_tail_optimization import mock_tail_context
    # Let's run TailOptimizer on mock_tail_context
    # We will instantiate mock_tail_context directly
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

    optimizer = TailOptimizer()
    optimizer.initialize(context)
    candidates = optimizer.generate_candidates(context)
    print(f"Total candidates generated: {len(candidates)}")
    feasible = []
    for c in candidates:
        if optimizer.apply_constraints(c, context):
            optimizer.evaluate_candidate(c, context)
            optimizer.score_candidate(c, context)
            feasible.append(c)

    print(f"Feasible candidates: {len(feasible)}")
    
    # Collect term statistics across feasible candidates
    term_names = [t.name for t in optimizer.objective._terms]
    stats = {t: [] for t in term_names}
    weighted_contribs = {t: [] for t in term_names}
    
    for c in feasible:
        for t in optimizer.objective._terms:
            val = c.objective_scores[t.name]
            stats[t.name].append(val)
            mult = 1.0 if t.minimize else -1.0
            weighted_contribs[t.name].append(t.weight * val * mult)

    print("\n--- TERM VALUE AUDIT (RAW) ---")
    for t in optimizer.objective._terms:
        vals = stats[t.name]
        w_vals = weighted_contribs[t.name]
        min_v, max_v, mean_v = min(vals), max(vals), sum(vals)/len(vals)
        min_w, max_w, mean_w = min(w_vals), max(w_vals), sum(w_vals)/len(w_vals)
        print(f"Term: {t.name:<25} | weight={t.weight:.2f} | min={t.minimize} | raw=[{min_v:.4f}, {max_v:.4f}] avg={mean_v:.4f} | weighted=[{min_w:.4f}, {max_w:.4f}] avg={mean_w:.4f}")

    winner = optimizer.select_best_candidate(feasible, context)
    print("\n--- WINNING CANDIDATE UNDER CURRENT OBJECTIVE ---")
    print(f"Overall score: {winner.overall_score:.4f}")
    print(f"Config: {winner.design_variables['tail_configuration']}, V_h={winner.derived_variables.get('V_h_actual')}, V_v={winner.derived_variables.get('V_v_actual')}, arm={winner.derived_variables.get('tail_arm_m')}")
    for t in optimizer.objective._terms:
        val = winner.objective_scores[t.name]
        mult = 1.0 if t.minimize else -1.0
        w_c = t.weight * val * mult
        print(f"  {t.name:<25}: raw={val:8.4f} | weight={t.weight:.2f} | contrib={w_c:8.4f}")

if __name__ == "__main__":
    inspect_tail_candidates()
