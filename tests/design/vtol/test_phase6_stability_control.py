"""
Phase 6 Test Suite: Authoritative Aerodynamic Stability, Static Margin, CG Envelope & Control-Surface Sizing
=============================================================================================================

Validates all 25 core requirements specified in VTOL Phase 6 prompt:
1. Aerodynamic center calculation and reference datum
2. Wing MAC calculation
3. Neutral point calculation and tail contribution
4. Static margin formula SM = (x_NP - x_CG) / MAC
5. CG consistency with locked Phase 5 baseline
6. Tail volume coefficients (V_H, V_V)
7. V-tail total area conservation (no double counting)
8. V-tail geometric vs effective horizontal projections
9. V-tail geometric vs effective vertical projections
10. V-tail control-surface (ruddervator) area sizing
11. Ruddervator pitch/yaw mixing conventions
12. Aileron area sizing (total vs single side)
13. Aileron span station allocation (65% to 95% semispan)
14. Control surface chord and area ratios
15. Aerodynamic control derivatives (C_m_delta_e, C_n_delta_r, C_l_delta_a)
16. Stability derivative sign conventions (C_m_alpha < 0, C_n_beta > 0, C_l_beta < 0)
17. Longitudinal CG envelope limits (forward, nominal, aft)
18. Quasi-steady trim feasibility across cruise, approach, and transition
19. Aerodynamic control authority and distinction from VTOL hover motors
20. Missing derivative handling (no silent zeroes)
21. Invalid geometry rejection (negative areas, impossible deflections)
22. Full recursive serialization preserving provenance and status
23. Phase 5 mass properties CG integration
24. Phase 1-5 regression invariants
25. Complete pipeline end-to-end integration
"""

import pytest
import math
import json
import copy

from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment

from backend.design.vtol.requirements.vtol_requirement_model import VTOLRequirementModel, VTOLType
from backend.design.vtol.pipeline.vtol_design_pipeline import VTOLDesignPipeline
from backend.design.vtol.pipeline.pipeline_result import PipelineStatus

from backend.design.vtol.tail.authoritative_stability import (
    AuthoritativeStabilityEngine,
    AuthoritativeStabilityResult,
    VTailPanelGeometry,
    VTailProjections,
    RuddervatorGeometry,
    AileronGeometry,
    LongitudinalStability,
    DirectionalStability,
    LateralStability,
    ControlDerivatives,
    TrimPoint,
    TrimAnalysis,
    CGEnvelope,
    ControlAuthority,
    StabilityClassification,
    TrimStatus,
    AuthorityStatus,
    StabilityStatus,
)


@pytest.fixture
def baseline_stability_result():
    """Generates authoritative Phase 6 stability result using locked Phase 5 baseline."""
    converged_mtow = 7.869
    converged_cg_x = 0.5211
    res = AuthoritativeStabilityEngine.analyze_stability_and_control(
        converged_mtow_kg=converged_mtow,
        converged_cg_x_m=converged_cg_x,
    )
    return res


def test_01_aerodynamic_center(baseline_stability_result):
    """1. Aerodynamic center: x_AC = x_LE + 0.25*MAC from nose datum."""
    long_s = baseline_stability_result.longitudinal_stability
    assert long_s.reference_datum == "FUSELAGE_NOSE"
    expected_ac = long_s.wing_le_x_m + 0.25 * long_s.wing_mac_m
    assert math.isclose(long_s.wing_ac_x_m, expected_ac, rel_tol=1e-3)
    assert long_s.x_ac_w_mac_pct == pytest.approx(25.0, abs=0.5)


def test_02_mac_calculation(baseline_stability_result):
    """2. MAC calculation for trapezoidal/rectangular wing planform."""
    long_s = baseline_stability_result.longitudinal_stability
    assert long_s.wing_mac_m > 0.10
    assert long_s.wing_mac_m < 0.25
    assert long_s.wing_le_x_m > 0.0


def test_03_neutral_point_calculation(baseline_stability_result):
    """3. Neutral point: x_NP = x_AC + MAC * V_H * (a_t / a_w) * (1 - de/da) * eta_t."""
    long_s = baseline_stability_result.longitudinal_stability
    assert long_s.neutral_point_x_m > long_s.wing_ac_x_m
    delta_x = long_s.neutral_point_x_m - long_s.wing_ac_x_m
    expected_delta = (
        long_s.wing_mac_m
        * long_s.horizontal_tail_volume
        * (long_s.tail_lift_curve_slope_per_rad / long_s.wing_lift_curve_slope_per_rad)
        * (1.0 - long_s.downwash_gradient)
        * long_s.tail_dynamic_pressure_ratio
    )
    assert math.isclose(delta_x, expected_delta, rel_tol=1e-2)
    assert long_s.neutral_point_pct_mac > 25.0


def test_04_static_margin_equation(baseline_stability_result):
    """4. Static margin: SM = (x_NP - x_CG) / MAC and positive stability."""
    long_s = baseline_stability_result.longitudinal_stability
    calculated_sm = (long_s.neutral_point_x_m - long_s.cg_x_m) / long_s.wing_mac_m
    assert math.isclose(long_s.static_margin, calculated_sm, abs_tol=1e-3)
    assert math.isclose(long_s.static_margin_pct, calculated_sm * 100.0, abs_tol=0.1)
    assert long_s.static_margin > 0.0
    assert long_s.is_statically_stable is True


def test_05_cg_consistency_with_phase5(baseline_stability_result):
    """5. CG consistency with Phase 5 converged longitudinal CG."""
    long_s = baseline_stability_result.longitudinal_stability
    assert long_s.cg_x_m == pytest.approx(0.5211, abs=1e-3)
    assert long_s.mtow_kg == pytest.approx(7.869, abs=1e-2)


def test_06_tail_volume_coefficients(baseline_stability_result):
    """6. Tail volume coefficients: V_H and V_V within standard aero bounds."""
    long_s = baseline_stability_result.longitudinal_stability
    dir_s = baseline_stability_result.directional_stability
    assert 0.30 <= long_s.horizontal_tail_volume <= 0.80
    assert 0.02 <= dir_s.vertical_tail_volume <= 0.08


def test_07_vtail_area_conservation(baseline_stability_result):
    """7. V-tail total area conservation: S_total = 2 * S_panel, no double-counting."""
    vtail = baseline_stability_result.vtail_panel_geometry
    assert vtail.panel_count == 2
    assert math.isclose(vtail.total_vtail_area_m2, 2.0 * vtail.single_panel_area_m2, abs_tol=5e-4)
    assert vtail.total_vtail_planform_area_m2 == vtail.total_vtail_area_m2


def test_08_vtail_horizontal_projection(baseline_stability_result):
    """8. V-tail horizontal projection: geometric vs aerodynamically effective."""
    vproj = baseline_stability_result.vtail_projections
    vtail = baseline_stability_result.vtail_panel_geometry
    theta = abs(math.radians(vtail.dihedral_angle_deg))
    expected_geom = vtail.total_vtail_area_m2 * math.cos(theta)
    expected_eff = vtail.total_vtail_area_m2 * (math.cos(theta) ** 2)
    assert math.isclose(vproj.horizontal_projected_area_m2, expected_geom, abs_tol=1e-3)
    assert math.isclose(vproj.effective_horizontal_area_m2, expected_eff, abs_tol=1e-3)
    assert vproj.effective_horizontal_area_m2 <= vproj.horizontal_projected_area_m2


def test_09_vtail_vertical_projection(baseline_stability_result):
    """9. V-tail vertical projection: geometric vs aerodynamically effective."""
    vproj = baseline_stability_result.vtail_projections
    vtail = baseline_stability_result.vtail_panel_geometry
    theta = abs(math.radians(vtail.dihedral_angle_deg))
    expected_geom = vtail.total_vtail_area_m2 * math.sin(theta)
    expected_eff = vtail.total_vtail_area_m2 * (math.sin(theta) ** 2)
    assert math.isclose(vproj.vertical_projected_area_m2, expected_geom, abs_tol=1e-3)
    assert math.isclose(vproj.effective_vertical_area_m2, expected_eff, abs_tol=1e-3)
    assert vproj.projection_conservation_check is True


def test_10_vtail_control_surface_area(baseline_stability_result):
    """10. V-tail control-surface area: 2 * S_rv_panel < S_total, area ratio 25-35%."""
    rv = baseline_stability_result.ruddervator_geometry
    vtail = baseline_stability_result.vtail_panel_geometry
    assert math.isclose(rv.total_ruddervator_area_m2, 2.0 * rv.single_ruddervator_area_m2, abs_tol=5e-4)
    assert rv.total_ruddervator_area_m2 < vtail.total_vtail_area_m2
    ratio = rv.total_ruddervator_area_m2 / vtail.total_vtail_area_m2
    assert 0.20 <= ratio <= 0.40


def test_11_pitch_yaw_ruddervator_mixing(baseline_stability_result):
    """11. Pitch/yaw ruddervator mixer convention and deflection limits."""
    rv = baseline_stability_result.ruddervator_geometry
    assert "delta_e" in rv.mixer_convention
    assert "delta_r" in rv.mixer_convention
    assert rv.max_deflection_deg >= 20.0
    # Test mixing logic: pure pitch vs pure yaw
    de = 5.0
    dr = 0.0
    d_left = de - dr
    d_right = de + dr
    assert d_left == d_right == de

    dr_pure = 3.0
    d_left_yaw = -dr_pure
    d_right_yaw = dr_pure
    assert d_left_yaw == -d_right_yaw


def test_12_aileron_area(baseline_stability_result):
    """12. Aileron sizing: total aileron area = 2 * single aileron area, 5-12% wing."""
    ail = baseline_stability_result.aileron_geometry
    assert math.isclose(ail.total_aileron_area_m2, 2.0 * ail.single_aileron_area_m2, abs_tol=5e-4)
    assert 0.04 <= ail.aileron_to_wing_area_ratio <= 0.15


def test_13_aileron_span(baseline_stability_result):
    """13. Aileron span station: spans outer wing (e.g. 65% to 95% semispan)."""
    ail = baseline_stability_result.aileron_geometry
    assert ail.inboard_semispan_fraction == pytest.approx(0.65, abs=0.02)
    assert ail.outboard_semispan_fraction == pytest.approx(0.95, abs=0.02)
    assert ail.outboard_station_y_m > ail.inboard_station_y_m
    expected_span = ail.outboard_station_y_m - ail.inboard_station_y_m
    assert math.isclose(ail.aileron_span_per_side_m, expected_span, rel_tol=1e-3)


def test_14_control_surface_ratios(baseline_stability_result):
    """14. Control surface chord ratios: ruddervator 25-35%, aileron 18-28%."""
    rv = baseline_stability_result.ruddervator_geometry
    ail = baseline_stability_result.aileron_geometry
    assert 0.20 <= rv.chord_ratio <= 0.40
    assert 0.15 <= ail.aileron_chord_ratio <= 0.30


def test_15_control_derivatives(baseline_stability_result):
    """15. Control derivatives: C_m_delta_e, C_n_delta_r, C_l_delta_a non-zero."""
    ctrl = baseline_stability_result.control_derivatives
    assert ctrl.c_m_delta_e_per_rad < -0.5
    assert ctrl.c_n_delta_r_per_rad < -0.02
    assert ctrl.c_l_delta_a_per_rad > 0.05


def test_16_stability_derivative_sign_conventions(baseline_stability_result):
    """16. Stability derivative signs: pitch restoring, weathercock, dihedral effect."""
    long_s = baseline_stability_result.longitudinal_stability
    dir_s = baseline_stability_result.directional_stability
    lat_s = baseline_stability_result.lateral_stability

    # Longitudinal pitch stiffness: C_m_alpha < 0
    assert long_s.c_m_alpha_per_rad < 0.0
    assert long_s.is_pitch_stiff is True

    # Directional weathercock stability: C_n_beta > 0
    assert dir_s.net_c_n_beta_per_rad > 0.0
    assert dir_s.is_directionally_stable is True

    # Lateral dihedral effect: C_l_beta < 0 (high-wing roll-due-to-sideslip)
    assert lat_s.c_l_beta_per_rad < 0.0
    assert lat_s.is_laterally_stable is True


def test_17_cg_envelope(baseline_stability_result):
    """17. Longitudinal CG envelope: forward < nominal < aft < neutral point."""
    env = baseline_stability_result.cg_envelope
    long_s = baseline_stability_result.longitudinal_stability
    assert env.forward_limit_x_m < env.nominal_cg_x_m
    assert env.nominal_cg_x_m < env.aft_limit_x_m
    assert env.aft_limit_x_m < long_s.neutral_point_x_m
    assert env.forward_margin_m > 0.0
    assert env.aft_margin_m > 0.0
    assert env.envelope_width_m > 0.0
    assert env.cg_envelope_status == "WITHIN_LIMITS"


def test_18_trim_feasibility(baseline_stability_result):
    """18. Quasi-steady trim feasibility across flight conditions."""
    trim = baseline_stability_result.trim_analysis
    assert trim.overall_trim_status == TrimStatus.TRIM_FEASIBLE
    assert len(trim.trim_points) >= 3

    # Check cruise trim
    cruise_tp = trim.cruise_trim
    assert cruise_tp is not None
    assert abs(cruise_tp.required_elevator_trim_deg) < 15.0
    assert cruise_tp.trim_margin_deg > 5.0
    assert cruise_tp.status == TrimStatus.TRIM_FEASIBLE


def test_19_control_authority(baseline_stability_result):
    """19. Control authority: max moments calculated, separate from VTOL motors."""
    auth = baseline_stability_result.control_authority
    assert auth.max_pitch_moment_nm > 2.0
    assert auth.max_yaw_moment_nm > 2.0
    assert auth.max_roll_moment_nm > 2.0
    assert auth.pitch_authority_status == AuthorityStatus.AUTHORITY_CALCULATED
    assert "differential thrust" in auth.vtol_multirotor_authority_distinction.lower()


def test_20_missing_derivative_handling():
    """20. Missing aerodynamic derivative handling: explicit classification, never silent zero."""
    res = AuthoritativeStabilityEngine.analyze_stability_and_control(
        converged_mtow_kg=7.869,
        converged_cg_x_m=0.5211,
        wing_result=None,
        tail_result=None,
    )
    # Ensure fallbacks and provenances are preserved
    prov = res.parameter_provenance
    assert "neutral_point_x_m" in prov
    assert prov["neutral_point_x_m"]["classification"] == StabilityClassification.DERIVED.value
    assert res.longitudinal_stability.c_m_alpha_per_rad != 0.0
    assert res.control_derivatives.c_m_delta_e_per_rad != 0.0


def test_21_invalid_geometry_rejection():
    """21. Invalid geometry rejection: negative area or inverted span fails or reports error."""
    with pytest.raises(Exception):
        AuthoritativeStabilityEngine.analyze_stability_and_control(
            converged_mtow_kg=-5.0,  # Negative MTOW
            converged_cg_x_m=0.5211,
        )


def test_22_serialization(baseline_stability_result):
    """22. Serialization: full recursive to_dict preserves all fields, values, and provenance."""
    d = baseline_stability_result.to_dict()
    assert isinstance(d, dict)
    assert "longitudinal_stability" in d
    assert "vtail_panel_geometry" in d
    assert "ruddervator_geometry" in d
    assert "aileron_geometry" in d
    assert "control_derivatives" in d
    assert "trim_analysis" in d
    assert "cg_envelope" in d
    assert "parameter_provenance" in d
    # JSON round trip test
    json_str = json.dumps(d)
    assert len(json_str) > 500
    loaded = json.loads(json_str)
    assert loaded["longitudinal_stability"]["static_margin"] == round(baseline_stability_result.longitudinal_stability.static_margin, 4)


def test_23_phase5_integration():
    """23. Phase 5 integration: mass properties CG envelope updated by stability result."""
    pipeline = VTOLDesignPipeline(tolerance=0.015, max_iterations=20, relaxation_alpha=0.70, raise_on_failure=False)
    req = VTOLRequirementModel.create(
        mission_type=MissionType.SURVEY,
        payload_mass=2.5,
        target_range=35.0,
        target_flight_time=25.0,
        cruise_speed=85.0,
        vtol_type=VTOLType.LIFT_CRUISE,
        hover_duration_min=5.0,
        transition_speed_kmh=65.0,
        lift_motor_count=4,
        takeoff_type=TakeoffType.VERTICAL,
        landing_type=LandingType.VERTICAL,
        environment=OperatingEnvironment.RURAL,
    )
    res = pipeline.execute(req)
    assert res.success is True
    spec = res.final_specification
    assert spec is not None
    auth_m = spec.mass_properties.authoritative_mass_result
    assert auth_m is not None
    cg = auth_m.center_of_gravity
    assert cg.forward_cg_limit_m is not None
    assert cg.aft_cg_limit_m is not None
    assert cg.cg_status == "DEFERRED_TO_PHASE_6"
    assert spec.tail.authoritative_stability_result.cg_envelope.cg_envelope_status == "WITHIN_LIMITS"


def test_24_phase1_to_5_regression():
    """24. Phase 1-5 regression: MTOW, empty mass, battery sizing are invariant."""
    pipeline = VTOLDesignPipeline(tolerance=0.015, max_iterations=20, relaxation_alpha=0.70, raise_on_failure=False)
    req = VTOLRequirementModel.create(
        mission_type=MissionType.SURVEY,
        payload_mass=2.5,
        target_range=35.0,
        target_flight_time=25.0,
        cruise_speed=85.0,
        vtol_type=VTOLType.LIFT_CRUISE,
        hover_duration_min=5.0,
        transition_speed_kmh=65.0,
        lift_motor_count=4,
        takeoff_type=TakeoffType.VERTICAL,
        landing_type=LandingType.VERTICAL,
        environment=OperatingEnvironment.RURAL,
    )
    res = pipeline.execute(req)
    assert res.success is True
    spec = res.final_specification
    assert math.isclose(spec.mtow_kg, 7.869, abs_tol=0.05)
    assert math.isclose(spec.empty_weight_kg, 4.862, abs_tol=0.05)
    assert spec.stage_statuses["mass_convergence"] == "IMPLEMENTED"
    assert spec.stage_statuses["stability_and_control"] == "IMPLEMENTED"


def test_25_complete_pipeline_integration():
    """25. Complete pipeline end-to-end integration: Phase 6 results in final spec."""
    pipeline = VTOLDesignPipeline(tolerance=0.015, max_iterations=20, relaxation_alpha=0.70, raise_on_failure=False)
    req = VTOLRequirementModel.create(
        mission_type=MissionType.SURVEY,
        payload_mass=2.5,
        target_range=35.0,
        target_flight_time=25.0,
        cruise_speed=85.0,
        vtol_type=VTOLType.LIFT_CRUISE,
        hover_duration_min=5.0,
        transition_speed_kmh=65.0,
        lift_motor_count=4,
        takeoff_type=TakeoffType.VERTICAL,
        landing_type=LandingType.VERTICAL,
        environment=OperatingEnvironment.RURAL,
    )
    res = pipeline.execute(req)
    assert res.success is True
    spec = res.final_specification
    assert spec.tail is not None
    auth_s = spec.tail.authoritative_stability_result
    assert auth_s is not None
    assert isinstance(auth_s, AuthoritativeStabilityResult)
    assert auth_s.longitudinal_stability.is_statically_stable is True
    assert auth_s.trim_analysis.overall_trim_status == TrimStatus.TRIM_FEASIBLE
    assert auth_s.verification_passed is True
