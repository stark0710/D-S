"""
Sprint 25 — Tail Optimization Engine Unit Tests

Tests candidate generation, constraint validation, objective scoring,
optimizer lifecycle, and determinism.
"""

import pytest
from backend.design.fixed_wing.mission.mission_requirements import (
    MissionCategory,
    LaunchMethod,
    LandingMethod,
    EnvironmentType,
    AutonomyLevel,
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
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate

from backend.design.fixed_wing.tail.optimization.models import TailSpecification
from backend.design.fixed_wing.tail.optimization.candidate_generator import GridSearchCandidateGenerator
from backend.design.fixed_wing.tail.optimization.constraints import build_tail_constraints
from backend.design.fixed_wing.tail.optimization.objective_function import TailObjectiveFunction
from backend.design.fixed_wing.tail.optimization.tail_optimizer import TailOptimizer


@pytest.fixture
def mock_tail_context():
    """Builds an OptimizationContext representative of a survey UAV."""
    profile = MissionProfile(
        mission_category=MissionCategory.SURVEY,
        payload_kg=2.0,
        flight_time_min=60.0,
        cruise_speed_kmh=80.0,
        stall_speed_target_kmh=45.0,
        maximum_takeoff_weight_limit_kg=10.0,
        operational_altitude_m=150.0,
        mission_range_km=40.0,
        launch_method=LaunchMethod.CATAPULT,
        landing_method=LandingMethod.PARACHUTE,
        budget=10000.0,
        environment=EnvironmentType.RURAL,
        autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
        air_density_kg_m3=1.2,
        energy_demand_kwh=0.5,
        cruise_emphasis=0.7,
        payload_emphasis=0.3,
        launch_recovery_complexity=0.5,
        environmental_complexity=0.3,
        operational_risk_score=0.4,
        mission_summary="Survey mission",
    )
    m_result = MissionResult(
        mission_profile=profile,
        mission_category=MissionCategory.SURVEY,
        mission_score=85.0,
        complexity="Medium",
        engineering_requirements={},
        constraints=None,
        recommendations=[],
        warnings=[],
        metadata={},
    )
    c_result = ConfigurationResult(
        selected_configuration={
            "wing_position": "High Wing",
            "propulsion_layout": "Tractor",
            "tail_configuration": "Conventional",
            "landing_gear_configuration": "Tricycle",
        },
        configuration_score=85.0,
        wing_configuration="High Wing",
        propulsion_configuration="Tractor",
        tail_configuration="Conventional",
        landing_gear_configuration="Tricycle",
        engineering_rationale="Rationale",
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
        mission_result=m_result,
        configuration_result=c_result,
        wing_result=w_result,
        airfoil_result=a_result,
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

    return OptimizationContext(
        requirements=reqs,
        configuration=c_result,
        previous_specifications={
            "WingPlanformOptimizer": wing_spec,
            "FuselageOptimizer": fuse_spec,
        },
    )


# ------------------------------------------------------------------
#  Tests
# ------------------------------------------------------------------


def test_sprint25_candidate_generation(mock_tail_context):
    """Verify that candidate generator produces the expected grid count."""
    gen = GridSearchCandidateGenerator()
    cands = gen.generate_candidates(mock_tail_context)

    # 3 Conventional + 3 T-Tail + 6 V-Tail + 6 Inverted V-Tail + 3 Twin Boom dihedrals/configs
    # = 7 configuration-dihedral combinations.
    # 7 × 3 V_h × 3 V_v × 3 arm × 2 h_ar × 2 v_ar × 2 h_taper × 2 v_taper × 2 h_sweep × 2 v_sweep
    expected_count = 7 * 3 * 3 * 3 * 2 * 2 * 2 * 2 * 2 * 2
    assert len(cands) == expected_count

    # Verify structure of the first candidate
    first = cands[0]
    assert "tail_configuration" in first.design_variables
    assert "horizontal_V_h" in first.design_variables
    assert "vertical_V_v" in first.design_variables
    assert "tail_arm_ratio" in first.design_variables
    assert "tail_dihedral_deg" in first.design_variables
    assert first.design_variables["tail_configuration"] in [
        "Conventional", "T-Tail", "V-Tail", "Inverted V-Tail", "Twin Boom"
    ]


def test_sprint25_constraints(mock_tail_context):
    """Verify constraint functions reject infeasible tail designs."""
    manager = build_tail_constraints()

    # 1. Configuration incompatibility — declared is Conventional,
    #    so V-Tail should be rejected
    cand_incompat = OptimizationCandidate(
        design_variables={
            "tail_configuration": "V-Tail",
            "horizontal_V_h": 0.55,
            "vertical_V_v": 0.04,
            "tail_arm_ratio": 0.55,
            "horiz_ar": 4.0,
            "vert_ar": 1.8,
            "horiz_taper": 0.6,
            "vert_taper": 0.6,
            "horiz_sweep": 0.0,
            "vert_sweep": 0.0,
            "tail_dihedral_deg": 40.0,
        }
    )
    assert manager.evaluate_constraints(cand_incompat, mock_tail_context) is False
    assert cand_incompat.constraint_results["configuration_compatibility"]["status"] == "FAIL"

    # 2. V_h too low — should fail static margin check
    cand_low_vh = OptimizationCandidate(
        design_variables={
            "tail_configuration": "Conventional",
            "horizontal_V_h": 0.20,
            "vertical_V_v": 0.04,
            "tail_arm_ratio": 0.55,
            "horiz_ar": 4.0,
            "vert_ar": 1.8,
            "horiz_taper": 0.6,
            "vert_taper": 0.6,
            "horiz_sweep": 0.0,
            "vert_sweep": 0.0,
            "tail_dihedral_deg": 0.0,
        }
    )
    assert manager.evaluate_constraints(cand_low_vh, mock_tail_context) is False
    assert cand_low_vh.constraint_results["static_margin"]["status"] == "FAIL"

    # 3. Propeller clearance violation (Pusher layout with short tail arm)
    mock_tail_context.configuration.propulsion_configuration = "Pusher"
    mock_tail_context.configuration.selected_configuration["propulsion_layout"] = "Pusher"
    cand_close_prop = OptimizationCandidate(
        design_variables={
            "tail_configuration": "Conventional",
            "horizontal_V_h": 0.55,
            "vertical_V_v": 0.04,
            "tail_arm_ratio": 0.45,
            "horiz_ar": 4.0,
            "vert_ar": 1.8,
            "horiz_taper": 0.6,
            "vert_taper": 0.6,
            "horiz_sweep": 0.0,
            "vert_sweep": 0.0,
            "tail_dihedral_deg": 0.0,
        }
    )
    assert manager.evaluate_constraints(cand_close_prop, mock_tail_context) is False
    assert cand_close_prop.constraint_results["tail_to_propeller"]["status"] == "FAIL"

    # Restore Tractor propulsion config
    mock_tail_context.configuration.propulsion_configuration = "Tractor"
    mock_tail_context.configuration.selected_configuration["propulsion_layout"] = "Tractor"

    # 4. Valid Conventional candidate — should pass
    cand_valid = OptimizationCandidate(
        design_variables={
            "tail_configuration": "Conventional",
            "horizontal_V_h": 0.55,
            "vertical_V_v": 0.04,
            "tail_arm_ratio": 0.55,
            "horiz_ar": 4.0,
            "vert_ar": 1.8,
            "horiz_taper": 0.6,
            "vert_taper": 0.6,
            "horiz_sweep": 0.0,
            "vert_sweep": 0.0,
            "tail_dihedral_deg": 0.0,
        }
    )
    assert manager.evaluate_constraints(cand_valid, mock_tail_context) is True


def test_sprint25_objective_function(mock_tail_context):
    """Verify weighted multi-objective scoring produces a finite score."""
    cand = OptimizationCandidate(
        design_variables={
            "tail_configuration": "Conventional",
            "horizontal_V_h": 0.55,
            "vertical_V_v": 0.04,
            "tail_arm_ratio": 0.55,
            "horiz_ar": 4.0,
            "vert_ar": 1.8,
            "horiz_taper": 0.6,
            "vert_taper": 0.6,
            "horiz_sweep": 0.0,
            "vert_sweep": 0.0,
            "tail_dihedral_deg": 0.0,
        }
    )
    # Simulate derived variables from evaluation
    cand.derived_variables = {
        "V_h_actual": 0.55,
        "V_v_actual": 0.04,
        "h_area_m2": 0.05,
        "v_area_m2": 0.02,
        "tail_arm_m": 1.1,
        "manufacturability_score": 95.0,
        "mission_suitability": 85.0,
    }

    obj = TailObjectiveFunction()
    score = obj.calculate_scores(cand, mock_tail_context)
    assert isinstance(score, float)
    assert cand.overall_score == score
    assert cand.objective_scores["longitudinal_stability"] == pytest.approx(0.0)
    assert cand.objective_scores["directional_stability"] == pytest.approx(0.0)
    assert "cg_robustness" in cand.objective_scores


def test_sprint25_optimizer_flow_and_determinism(mock_tail_context):
    """Verify optimizer lifecycle executes cleanly and produces deterministic results."""
    optimizer = TailOptimizer()
    res1 = optimizer.optimize(mock_tail_context)

    assert res1.success is True
    assert res1.evaluated_count > 0
    assert res1.feasible_count > 0
    assert isinstance(res1.generated_specification, TailSpecification)

    spec = res1.generated_specification
    assert spec.tail_configuration == "Conventional"
    assert spec.horizontal_tail_area_m2 > 0
    assert spec.vertical_tail_area_m2 > 0
    assert spec.tail_arm_m > 0
    assert spec.tail_dihedral_deg == 0.0

    # Determinism — run again
    res2 = optimizer.optimize(mock_tail_context)
    assert res2.success is True
    assert res2.winning_candidate.design_variables == res1.winning_candidate.design_variables
    assert res2.winning_candidate.overall_score == res1.winning_candidate.overall_score
