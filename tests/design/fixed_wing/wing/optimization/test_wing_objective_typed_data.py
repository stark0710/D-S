"""
Unit and regression test suite for Phase 6B-4: Wing Objective Typed-Data Refactor.

Verifies:
1. Numerical score equivalence between legacy parsed logic and typed-data logic.
2. Note-mutation and format robustness (modifying or erasing notes does not alter optimization scores).
3. End-to-end typed data trace through CandidateEvaluator and WingPlanformOptimizer.
4. Controlled fallback behavior when typed attributes are absent on synthetic mock objects.
5. Continued compatibility with OptimizationPriority weights.
6. Preservation of wing feasibility and hard constraints.
"""

import pytest
import math
from backend.design.fixed_wing.mission.mission_requirements import (
    MissionCategory,
    LaunchMethod,
    LandingMethod,
    EnvironmentType,
    AutonomyLevel,
)
from backend.design.fixed_wing.mission.mission_constraints import MissionConstraints
from backend.design.fixed_wing.mission.mission_profile import MissionProfile
from backend.design.fixed_wing.mission.mission_result import MissionResult
from backend.design.fixed_wing.configuration.configuration_result import ConfigurationResult
from backend.design.fixed_wing.wing.wing_requirements import WingRequirements
from backend.design.fixed_wing.wing.wing_geometry import WingGeometry
from backend.design.fixed_wing.wing.wing_result import WingResult
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.fixed_wing.wing.optimization.models import WingPlanformSpecification
from backend.design.fixed_wing.wing.optimization.objective_function import WingObjectiveFunction
from backend.design.fixed_wing.wing.optimization.wing_planform_optimizer import WingPlanformOptimizer
from backend.design.fixed_wing.wing.optimization.candidate_evaluator import CandidateEvaluator
from backend.design.fixed_wing.optimization.optimization_objective import WeightedMultiObjective
from backend.design.fixed_wing.optimization.optimization_constraints import OptimizationConstraints
from backend.design.fixed_wing.optimization.optimization_models import PlanformCandidate


@pytest.fixture
def mock_wing_context():
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
    constraints = MissionConstraints(
        minimum_payload_kg=2.0,
        minimum_range_km=40.0,
        minimum_endurance_min=60.0,
        target_cruise_speed_kmh=80.0,
        maximum_stall_speed_kmh=45.0,
        maximum_takeoff_weight_kg=10.0,
        budget_limit=10000.0,
        required_launch_method=LaunchMethod.CATAPULT,
        required_landing_method=LandingMethod.PARACHUTE,
        operating_environment=EnvironmentType.RURAL,
        required_autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
    )
    m_result = MissionResult(
        mission_profile=profile,
        mission_category=MissionCategory.SURVEY,
        mission_score=85.0,
        complexity="Medium",
        engineering_requirements={},
        constraints=constraints,
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
    reqs = WingRequirements(
        mission_result=m_result,
        configuration_result=c_result,
        metadata={"max_wingspan_m": 3.0},
    )
    return OptimizationContext(requirements=reqs, configuration=c_result)


def test_score_equivalence(mock_wing_context):
    """
    Section 11: Exact Score Equivalence Test.
    Proves that the new typed-data calculation yields the exact same numerical
    objective score as the legacy string-parsing logic.
    """
    geom = WingGeometry(
        span_m=1.80, area_m2=0.324, aspect_ratio=10.0, wing_loading_kg_m2=13.48,
        root_chord_m=0.267, tip_chord_m=0.133, taper_ratio=0.5, sweep_angle_deg=0.0,
        dihedral_angle_deg=2.0, wing_incidence_deg=1.5, mean_aerodynamic_chord_m=0.205,
        quarter_chord_x_m=0.051, reference_area_m2=0.324,
    )

    class MockAnalysis:
        lift_coefficient_cruise = 0.55
        drag_coefficient_cruise = 0.045

    mtow_val = 4.367
    wing_weight_val = 0.532

    # 1. Candidate using typed data
    res_typed = WingResult(
        wing_geometry=geom, planform="Tapered", reference_area=0.324, aspect_ratio=10.0,
        wing_loading=13.48, mean_aerodynamic_chord=0.205, quarter_chord_location=0.051,
        analysis=MockAnalysis(), engineering_notes=[], recommendations=[], warnings=[],
        estimated_mtow_kg=mtow_val, estimated_wing_weight_kg=wing_weight_val,
    )
    cand_typed = OptimizationCandidate(design_variables={"aspect_ratio": 10.0, "taper_ratio": 0.5, "sweep_angle_deg": 0.0})
    cand_typed.derived_variables["wing_result"] = res_typed
    cand_typed.derived_variables["wing_span"] = 1.80

    # 2. Legacy formula calculation directly from values:
    # fraction = wing_weight / max(0.1, mtow)
    # norm(fraction, 0.05, 0.25)
    legacy_fraction = wing_weight_val / max(0.1, mtow_val)
    from backend.design.common.optimization.optimization_utils import normalize_value
    expected_struct_score = float(normalize_value(legacy_fraction, 0.05, 0.25))

    obj = WingObjectiveFunction()
    actual_struct_score = obj._calc_structures(cand_typed, mock_wing_context)

    assert actual_struct_score == pytest.approx(expected_struct_score, rel=1e-6)

    # Also check full overall score
    overall_score = obj.calculate_scores(cand_typed, mock_wing_context)
    assert isinstance(overall_score, float)
    assert cand_typed.overall_score == overall_score


def test_string_format_robustness(mock_wing_context):
    """
    Section 18: Mutation / Format Robustness Test.
    Proves that altering, corrupting, or wiping human-readable notes does NOT
    change the optimization objective score in any way.
    """
    geom = WingGeometry(
        span_m=2.0, area_m2=0.5, aspect_ratio=8.0, wing_loading_kg_m2=20.0,
        root_chord_m=0.3, tip_chord_m=0.2, taper_ratio=0.6, sweep_angle_deg=0.0,
        dihedral_angle_deg=0.0, wing_incidence_deg=0.0, mean_aerodynamic_chord_m=0.25,
        quarter_chord_x_m=0.06, reference_area_m2=0.5,
    )

    class MockAnalysis:
        lift_coefficient_cruise = 0.5
        drag_coefficient_cruise = 0.05

    mtow_val = 5.25
    wing_weight_val = 0.65

    # Base candidate with standard notes
    res_standard = WingResult(
        wing_geometry=geom, planform="Tapered", reference_area=0.5, aspect_ratio=8.0,
        wing_loading=20.0, mean_aerodynamic_chord=0.25, quarter_chord_location=0.06,
        analysis=MockAnalysis(),
        engineering_notes=[
            f"Estimated MTOW: {mtow_val:.2f} kg, Cruise Lift Coefficient: 0.500.",
            f"Estimated Wing weight: {wing_weight_val:.3f} kg.",
        ],
        recommendations=[], warnings=[],
        estimated_mtow_kg=mtow_val, estimated_wing_weight_kg=wing_weight_val,
    )
    cand_standard = OptimizationCandidate(design_variables={"aspect_ratio": 8.0, "taper_ratio": 0.6, "sweep_angle_deg": 0.0})
    cand_standard.derived_variables["wing_result"] = res_standard
    cand_standard.derived_variables["wing_span"] = 2.0

    # Candidate with completely modified / rewritten notes
    res_mutated = WingResult(
        wing_geometry=geom, planform="Tapered", reference_area=0.5, aspect_ratio=8.0,
        wing_loading=20.0, mean_aerodynamic_chord=0.25, quarter_chord_location=0.06,
        analysis=MockAnalysis(),
        engineering_notes=[
            "MTOW estimate available in engineering data model.",
            "Wing mass calculated by mass subsystem.",
            "Custom note that previously broke string splitting: Estimated MTOW is not here kg.",
        ],
        recommendations=[], warnings=[],
        estimated_mtow_kg=mtow_val, estimated_wing_weight_kg=wing_weight_val,
    )
    cand_mutated = OptimizationCandidate(design_variables={"aspect_ratio": 8.0, "taper_ratio": 0.6, "sweep_angle_deg": 0.0})
    cand_mutated.derived_variables["wing_result"] = res_mutated
    cand_mutated.derived_variables["wing_span"] = 2.0

    # Candidate with empty notes
    res_empty = WingResult(
        wing_geometry=geom, planform="Tapered", reference_area=0.5, aspect_ratio=8.0,
        wing_loading=20.0, mean_aerodynamic_chord=0.25, quarter_chord_location=0.06,
        analysis=MockAnalysis(),
        engineering_notes=[],
        recommendations=[], warnings=[],
        estimated_mtow_kg=mtow_val, estimated_wing_weight_kg=wing_weight_val,
    )
    cand_empty = OptimizationCandidate(design_variables={"aspect_ratio": 8.0, "taper_ratio": 0.6, "sweep_angle_deg": 0.0})
    cand_empty.derived_variables["wing_result"] = res_empty
    cand_empty.derived_variables["wing_span"] = 2.0

    obj = WingObjectiveFunction()
    score_standard = obj.calculate_scores(cand_standard, mock_wing_context)
    score_mutated = obj.calculate_scores(cand_mutated, mock_wing_context)
    score_empty = obj.calculate_scores(cand_empty, mock_wing_context)

    # Exact equality across all note variations
    assert score_standard == pytest.approx(score_mutated, abs=1e-12)
    assert score_standard == pytest.approx(score_empty, abs=1e-12)


def test_typed_data_trace_through_pipeline(mock_wing_context):
    """
    Section 17: Typed-Data Trace Test.
    Verifies that CandidateEvaluator and WingPlanformOptimizer produce and carry
    typed estimated_mtow_kg and estimated_wing_weight_kg through derived variables
    and into WingPlanformSpecification without string parsing.
    """
    evaluator = CandidateEvaluator()
    cand = OptimizationCandidate(
        design_variables={
            "aspect_ratio": 9.0,
            "taper_ratio": 0.5,
            "sweep_angle_deg": 0.0,
            "dihedral_angle_deg": 1.0,
            "wing_position": "High Wing",
        }
    )

    evaluator.evaluate(cand, mock_wing_context)

    # Verify derived variables received typed floats
    assert "estimated_mtow_kg" in cand.derived_variables
    assert "estimated_wing_weight_kg" in cand.derived_variables

    mtow = cand.derived_variables["estimated_mtow_kg"]
    wing_weight = cand.derived_variables["estimated_wing_weight_kg"]

    assert isinstance(mtow, float)
    assert mtow > 0.0
    assert isinstance(wing_weight, float)
    assert wing_weight > 0.0

    # Verify WingResult also holds the typed fields
    wing_res = cand.derived_variables["wing_result"]
    assert wing_res.estimated_mtow_kg == mtow
    assert wing_res.estimated_wing_weight_kg == wing_weight

    # Verify WingPlanformOptimizer builds specification with typed fields
    optimizer = WingPlanformOptimizer()
    cand.overall_score = 0.25
    spec = optimizer.build_specification(cand, mock_wing_context)

    assert isinstance(spec, WingPlanformSpecification)
    assert spec.estimated_mtow_kg == mtow
    assert spec.estimated_wing_weight_kg == wing_weight


def test_missing_data_fallbacks(mock_wing_context):
    """
    Section 15: Missing Data & Controlled Fallback Test.
    Verifies deterministic fallback behavior when typed attributes are None on mock objects.
    """
    geom = WingGeometry(
        span_m=2.0, area_m2=0.5, aspect_ratio=8.0, wing_loading_kg_m2=20.0,
        root_chord_m=0.3, tip_chord_m=0.2, taper_ratio=0.6, sweep_angle_deg=0.0,
        dihedral_angle_deg=0.0, wing_incidence_deg=0.0, mean_aerodynamic_chord_m=0.25,
        quarter_chord_x_m=0.06, reference_area_m2=0.5,
    )

    # Mock result with None for both typed fields and NO notes
    res_none = WingResult(
        wing_geometry=geom, planform="Tapered", reference_area=0.5, aspect_ratio=8.0,
        wing_loading=20.0, mean_aerodynamic_chord=0.25, quarter_chord_location=0.06,
        analysis=None, engineering_notes=[], recommendations=[], warnings=[],
        estimated_mtow_kg=None, estimated_wing_weight_kg=None,
    )
    cand = OptimizationCandidate(design_variables={"aspect_ratio": 8.0, "taper_ratio": 0.6, "sweep_angle_deg": 0.0})
    cand.derived_variables["wing_result"] = res_none

    obj = WingObjectiveFunction()
    struct_score = obj._calc_structures(cand, mock_wing_context)

    # Must produce a valid float, falling back to structural calculation from geometry
    assert isinstance(struct_score, float)
    assert 0.0 <= struct_score <= 1.0


def test_priority_compatibility(mock_wing_context):
    """
    Section 16: OptimizationPriority Compatibility Test.
    Verifies that all 7 optimization priorities continue to wire weights to
    WingObjectiveFunction properly.
    """
    from backend.design.common.optimization.priority_policy import OptimizationPriority

    optimizer = WingPlanformOptimizer()

    priorities = [
        OptimizationPriority.BALANCED,
        OptimizationPriority.LOWEST_WEIGHT,
        OptimizationPriority.MAXIMUM_ENDURANCE,
        OptimizationPriority.MAXIMUM_RANGE,
        OptimizationPriority.HIGHEST_EFFICIENCY,
        OptimizationPriority.LOWEST_COST,
        OptimizationPriority.MAXIMUM_PAYLOAD,
    ]

    for p in priorities:
        mock_wing_context.optimization_priority = p
        optimizer.initialize(mock_wing_context)

        # Check that weights are populated and non-empty
        assert len(optimizer.objective._terms) == 6
        weights = {term.name: term.weight for term in optimizer.objective._terms}

        if p == OptimizationPriority.LOWEST_WEIGHT:
            assert weights["structures"] > weights["packaging"]
        elif p == OptimizationPriority.HIGHEST_EFFICIENCY:
            assert weights["aerodynamics"] >= 0.30


def test_hard_constraints_preservation():
    """
    Section 19: Hard Constraint Proof.
    Verifies that OptimizationConstraints continues to enforce span, chord, and
    wing fraction limits without string parsing.
    """
    geom_invalid = WingGeometry(
        span_m=3.5, area_m2=1.0, aspect_ratio=12.25, wing_loading_kg_m2=20.0,
        root_chord_m=0.04,  # below 0.05 min chord
        tip_chord_m=0.03,   # below 0.05 min chord
        taper_ratio=0.75, sweep_angle_deg=0.0, dihedral_angle_deg=0.0,
        wing_incidence_deg=0.0, mean_aerodynamic_chord_m=0.25,
        quarter_chord_x_m=0.06, reference_area_m2=1.0,
    )

    res_invalid = WingResult(
        wing_geometry=geom_invalid, planform="Tapered", reference_area=1.0,
        aspect_ratio=12.25, wing_loading=20.0, mean_aerodynamic_chord=0.25,
        quarter_chord_location=0.06, analysis=None, engineering_notes=[],
        recommendations=[], warnings=[],
        estimated_mtow_kg=10.0,
        estimated_wing_weight_kg=3.5,  # 35% > 25% max fraction
    )

    cand = PlanformCandidate(12.25, 0.75, 0.0, 20.0)
    cons = OptimizationConstraints(max_wingspan_m=3.0, min_chord_m=0.05, max_wing_mass_fraction=0.25)

    passed, violations = cons.check_constraints(cand, res_invalid)

    assert passed is False
    assert len(violations) == 4
    assert any("Wingspan" in v for v in violations)
    assert any("Root chord" in v for v in violations)
    assert any("Tip chord" in v for v in violations)
    assert any("Wing weight fraction" in v for v in violations)
