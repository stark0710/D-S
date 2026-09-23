"""
Unit and Integration Test Suite for VTOL Phase 4:
Energy, Battery & Electrical Integration.

Validates:
    1. Basic mission energy calculation
    2. Hover energy across takeoff, climb, descent, landing
    3. Direct hover power reuse from Phase 2 AuthoritativeHoverResult
    4. Direct transition energy reuse from Phase 3 AuthoritativeTransitionResult
    5. Reverse-transition energy reuse (TRANSITION_TO_VTOL)
    6. Cruise energy reuse from Fixed-Wing adapter
    7. Mission energy summation over all 10 phases
    8. Reserve energy accounting
    9. Usable vs nominal battery energy sizing
    10. Capacity calculation (Ah = Wh / V)
    11. Current calculation (I = P / V)
    12. Peak current determination
    13. Continuous current determination
    14. C-rate calculations (continuous & peak)
    15. Lift + Cruise propulsion bus separation
    16. Simultaneous transition load on shared battery
    17. Double-counting detection & validation
    18. Invalid negative duration rejection
    19. Invalid negative power rejection
    20. Missing voltage handling (unresolved Ah, no crash)
    21. Missing specific energy handling (unresolved mass, deferred to Phase 5)
    22. Full recursive serialization to dict and JSON
    23. Pre-convergence MTOW semantics (is_converged_mtow = False)
    24. Configuration-driven lift motor count (N = 4, 6, 8)
    25. End-to-end regression through VTOLDesignPipeline with status IMPLEMENTED
"""

import pytest
import json
from dataclasses import dataclass
from typing import Dict, Any

from backend.design.vtol.mission.mission_state import (
    VTOLMissionPhase,
    VTOLMissionProfileSequence,
    VTOLMissionSegment,
)
from backend.design.vtol.hover_performance.authoritative_hover import (
    AuthoritativeHoverModel,
    AuthoritativeHoverResult,
)
from backend.design.vtol.transition.authoritative_transition import (
    AuthoritativeTransitionModel,
    AuthoritativeTransitionResult,
)
from backend.design.vtol.fixed_wing_interface.fixed_wing_adapter import (
    FixedWingSubsystemResult,
)
from backend.design.vtol.electrical.authoritative_energy import (
    AuthoritativeEnergyModel,
    AuthoritativeEnergyResult,
    MissionEnergyLedger,
    BatterySizingRequirements,
    ElectricalEnvelope,
    EnergyLedgerValidationError,
    DEFAULT_RESERVE_FRACTION,
    DEFAULT_USABLE_DOD_FRACTION,
)
from backend.design.vtol.electrical.electrical_requirements import ElectricalRequirements
from backend.design.vtol.electrical.electrical_engine import ElectricalEngine
from backend.design.vtol.electrical.electrical_validator import (
    ElectricalValidator,
    ElectricalValidationError,
)
from backend.design.vtol.pipeline.vtol_design_pipeline import VTOLDesignPipeline
from backend.design.vtol.requirements.vtol_requirement_model import VTOLRequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.vtol.mission.mission_requirements import VTOLType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.design_mode import DesignMode


# =========================================================================
# FIXTURES
# =========================================================================

@pytest.fixture
def standard_hover_result():
    """Authoritative Phase 2 hover result for a 15 kg QuadPlane."""
    return AuthoritativeHoverModel.calculate_hover_state(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        rotor_diameter_m=0.55,
        system_voltage_v=44.4,
        hover_thrust_to_weight_target=1.20,
    )


@pytest.fixture
def standard_transition_result():
    """Authoritative Phase 3 forward transition result for a 15 kg QuadPlane."""
    return AuthoritativeTransitionModel.calculate_transition_corridor(
        sizing_mass_kg=15.0,
        wing_area_m2=0.85,
        lift_motor_count=4,
        preferred_transition_duration_s=18.0,
        preferred_transition_speed_kmh=65.0,
        direction="TRANSITION_TO_CRUISE",
    )


@pytest.fixture
def standard_reverse_transition_result():
    """Authoritative Phase 3 reverse transition result for a 15 kg QuadPlane."""
    return AuthoritativeTransitionModel.calculate_transition_corridor(
        sizing_mass_kg=15.0,
        wing_area_m2=0.85,
        lift_motor_count=4,
        preferred_transition_duration_s=18.0,
        preferred_transition_speed_kmh=65.0,
        direction="TRANSITION_TO_VTOL",
    )


# =========================================================================
# TEST CASES
# =========================================================================

def test_01_basic_mission_energy_calculation(standard_hover_result, standard_transition_result):
    """1. Verify basic mission energy calculation produces positive non-zero energy."""
    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        transition_result=standard_transition_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=44.4,
    )
    assert res is not None
    assert res.ledger.total_mission_energy_wh > 0.0
    assert res.battery_sizing.required_usable_energy_wh > res.ledger.total_mission_energy_wh


def test_02_hover_energy_across_phases(standard_hover_result):
    """2. Verify hover energy is calculated for takeoff, climb, descent, and landing."""
    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=44.4,
    )
    takeoff = res.ledger.get_segment(VTOLMissionPhase.VTOL_TAKEOFF)
    climb = res.ledger.get_segment(VTOLMissionPhase.HOVER_CLIMB)
    descent = res.ledger.get_segment(VTOLMissionPhase.HOVER_DESCENT)
    landing = res.ledger.get_segment(VTOLMissionPhase.VTOL_LANDING)

    for seg in (takeoff, climb, descent, landing):
        assert seg is not None
        assert seg.energy_wh > 0.0
        assert seg.propulsion_power_w > 0.0
        # Check energy formula: E = P * t / 3600
        expected_e = seg.average_power_w * seg.duration_s / 3600.0
        assert pytest.approx(seg.energy_wh, rel=1e-5) == expected_e


def test_03_hover_power_reuse_from_phase2(standard_hover_result):
    """3. Verify hover propulsion power strictly reuses Phase 2 AuthoritativeHoverResult."""
    p_hover_expected = standard_hover_result.hover_electrical_power_w
    assert p_hover_expected is not None and p_hover_expected > 0.0

    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=44.4,
    )
    climb_seg = res.ledger.get_segment(VTOLMissionPhase.HOVER_CLIMB)
    assert pytest.approx(climb_seg.propulsion_power_w, rel=1e-4) == p_hover_expected
    assert climb_seg.calculation_source == "PHASE_2_HOVER_MODEL"


def test_04_transition_energy_reuse_from_phase3(standard_hover_result, standard_transition_result):
    """4. Verify transition energy strictly reuses Phase 3 integrated trapezoidal corridor energy."""
    e_trans_kwh_expected = standard_transition_result.total_energy_kwh
    e_trans_wh_expected = e_trans_kwh_expected * 1000.0

    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        transition_result=standard_transition_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=44.4,
    )
    trans_seg = res.ledger.get_segment(VTOLMissionPhase.TRANSITION_TO_CRUISE)
    assert pytest.approx(trans_seg.propulsion_power_w * trans_seg.duration_s / 3600.0, rel=1e-4) == e_trans_wh_expected
    assert trans_seg.calculation_source == "PHASE_3_TRANSITION_MODEL"


def test_05_reverse_transition_energy_reuse(
    standard_hover_result, standard_transition_result, standard_reverse_transition_result
):
    """5. Verify reverse transition energy reuses Phase 3 TRANSITION_TO_VTOL corridor energy."""
    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        transition_result=standard_transition_result,
        reverse_transition_result=standard_reverse_transition_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=44.4,
    )
    rev_seg = res.ledger.get_segment(VTOLMissionPhase.TRANSITION_TO_VTOL)
    assert rev_seg is not None
    assert rev_seg.energy_wh > 0.0
    expected_wh = standard_reverse_transition_result.total_energy_kwh * 1000.0
    assert pytest.approx(rev_seg.propulsion_power_w * rev_seg.duration_s / 3600.0, rel=1e-4) == expected_wh


def test_06_cruise_energy_through_fixed_wing_adapter(standard_hover_result, standard_transition_result):
    """6. Verify cruise energy uses cruise propulsion power from Fixed-Wing adapter interface."""
    fw_cruise_p_w = 420.0
    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        transition_result=standard_transition_result,
        cruise_propulsion_power_w=fw_cruise_p_w,
        system_voltage_v=44.4,
    )
    cruise_seg = res.ledger.get_segment(VTOLMissionPhase.FIXED_WING_CRUISE)
    assert pytest.approx(cruise_seg.propulsion_power_w, rel=1e-5) == fw_cruise_p_w
    assert cruise_seg.calculation_source == "FIXED_WING_ADAPTER"


def test_07_mission_energy_summation_all_10_phases(standard_hover_result, standard_transition_result):
    """7. Verify total mission energy equals the exact sum of all 10 individual segment energies."""
    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        transition_result=standard_transition_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=44.4,
    )
    assert len(res.ledger.segments) == 10
    sum_segments = sum(s.energy_wh for s in res.ledger.segments)
    assert pytest.approx(res.ledger.total_mission_energy_wh, abs=1e-6) == sum_segments


def test_08_reserve_energy_accounting(standard_hover_result, standard_transition_result):
    """8. Verify reserve energy equals configured reserve_fraction * mission_energy."""
    f_res = 0.25
    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        transition_result=standard_transition_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=44.4,
        reserve_fraction=f_res,
    )
    expected_reserve = res.ledger.total_mission_energy_wh * f_res
    assert pytest.approx(res.battery_sizing.reserve_energy_wh, rel=1e-5) == expected_reserve
    assert pytest.approx(res.battery_sizing.required_usable_energy_wh, rel=1e-5) == (
        res.ledger.total_mission_energy_wh + expected_reserve
    )


def test_09_usable_vs_nominal_battery_energy(standard_hover_result, standard_transition_result):
    """9. Verify nominal battery energy sizes for allowable depth-of-discharge: E_nom = E_usable / DoD."""
    dod = 0.80
    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        transition_result=standard_transition_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=44.4,
        usable_fraction=dod,
    )
    expected_nominal = res.battery_sizing.required_usable_energy_wh / dod
    assert pytest.approx(res.battery_sizing.required_nominal_battery_energy_wh, rel=1e-5) == expected_nominal


def test_10_capacity_calculation_ah(standard_hover_result, standard_transition_result):
    """10. Verify capacity in Amp-hours satisfies Ah = Wh / V_nom."""
    v_nom = 48.0
    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        transition_result=standard_transition_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=v_nom,
    )
    expected_nom_ah = res.battery_sizing.required_nominal_battery_energy_wh / v_nom
    expected_usable_ah = res.battery_sizing.required_usable_energy_wh / v_nom
    assert pytest.approx(res.battery_sizing.required_nominal_capacity_ah, rel=1e-5) == expected_nom_ah
    assert pytest.approx(res.battery_sizing.required_usable_capacity_ah, rel=1e-5) == expected_usable_ah


def test_11_current_calculation_i_equals_p_over_v(standard_hover_result, standard_transition_result):
    """11. Verify electrical currents satisfy I = P / V for continuous and peak loads."""
    v_nom = 44.4
    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        transition_result=standard_transition_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=v_nom,
    )
    assert res.envelope.continuous_current_a is not None
    expected_cont_i = res.envelope.maximum_continuous_power_w / v_nom
    assert pytest.approx(res.envelope.continuous_current_a, rel=1e-5) == expected_cont_i


def test_12_peak_current_determination(standard_hover_result, standard_transition_result):
    """12. Verify peak current is determined from maximum peak segment load (transition/takeoff)."""
    v_nom = 44.4
    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        transition_result=standard_transition_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=v_nom,
    )
    assert res.envelope.peak_current_a is not None
    expected_peak_i = res.envelope.maximum_peak_power_w / v_nom
    assert pytest.approx(res.envelope.peak_current_a, rel=1e-5) == expected_peak_i
    assert res.envelope.peak_current_a >= res.envelope.continuous_current_a


def test_13_continuous_vs_peak_separation(standard_hover_result, standard_transition_result):
    """13. Verify continuous power/current and peak power/current are strictly separated."""
    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        transition_result=standard_transition_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=44.4,
    )
    assert res.envelope.maximum_continuous_power_w < res.envelope.maximum_peak_power_w
    assert res.envelope.continuous_current_a < res.envelope.peak_current_a


def test_14_c_rate_calculations(standard_hover_result, standard_transition_result):
    """14. Verify continuous and peak C-rates satisfy C = I / Ah."""
    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        transition_result=standard_transition_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=44.4,
        max_allowable_c_rate=25.0,
    )
    nom_ah = res.battery_sizing.required_nominal_capacity_ah
    expected_cont_c = res.envelope.continuous_current_a / nom_ah
    expected_peak_c = res.envelope.peak_current_a / nom_ah

    assert pytest.approx(res.envelope.continuous_c_rate, rel=1e-4) == expected_cont_c
    assert pytest.approx(res.envelope.peak_c_rate, rel=1e-4) == expected_peak_c
    assert res.envelope.is_c_rate_compliant is True


def test_15_lift_and_cruise_bus_accounting(standard_hover_result, standard_transition_result):
    """15. Verify explicit separation of Lift Propulsion Bus and Cruise Propulsion Bus."""
    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        transition_result=standard_transition_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=44.4,
    )
    lift_bus = res.envelope.lift_bus
    cruise_bus = res.envelope.cruise_bus

    assert lift_bus is not None
    assert lift_bus.motor_count == 4
    assert lift_bus.continuous_power_w > 0.0
    assert lift_bus.per_motor_current_a == pytest.approx(lift_bus.continuous_current_a / 4.0, rel=1e-4)

    assert cruise_bus is not None
    assert cruise_bus.motor_count == 1
    assert cruise_bus.continuous_power_w == pytest.approx(350.0, rel=1e-4)


def test_16_simultaneous_transition_load_on_shared_battery(
    standard_hover_result, standard_transition_result
):
    """16. Verify transition simultaneous lift + cruise peak load is reflected on shared battery."""
    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        transition_result=standard_transition_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=44.4,
    )
    p_trans_peak = standard_transition_result.peak_electrical_power_w
    # Simultaneous transition peak power includes avionics + transition peak
    assert res.envelope.simultaneous_transition_power_w >= p_trans_peak


def test_17_no_double_counting_validation(standard_hover_result, standard_transition_result):
    """17. Verify double-counting check detects duplicate states or overlapping accounting."""
    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        transition_result=standard_transition_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=44.4,
    )
    assert res.ledger.has_double_counting is False
    assert res.ledger.is_complete is True


def test_18_invalid_duration_rejection():
    """18. Verify validation rejects invalid negative segment durations."""
    with pytest.raises(EnergyLedgerValidationError) as excinfo:
        AuthoritativeEnergyModel.calculate_mission_energy(
            sizing_mass_kg=15.0,
            lift_motor_count=4,
            custom_segment_durations_s={VTOLMissionPhase.HOVER_CLIMB: -30.0},
        )
    assert "Negative duration" in str(excinfo.value)


def test_19_invalid_power_or_mass_rejection():
    """19. Verify validation rejects negative sizing mass or invalid reserve parameters."""
    with pytest.raises(EnergyLedgerValidationError) as exc1:
        AuthoritativeEnergyModel.calculate_mission_energy(sizing_mass_kg=-10.0)
    assert "Invalid sizing mass" in str(exc1.value)

    with pytest.raises(EnergyLedgerValidationError) as exc2:
        AuthoritativeEnergyModel.calculate_mission_energy(sizing_mass_kg=15.0, reserve_fraction=-0.2)
    assert "Invalid reserve fraction" in str(exc2.value)


def test_20_missing_voltage_handling(standard_hover_result, standard_transition_result):
    """20. Verify missing voltage reports missing input (status PARTIAL) without crashing."""
    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        transition_result=standard_transition_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=None,  # Missing voltage
    )
    assert res.status == "PARTIAL"
    assert res.battery_sizing.nominal_voltage_v is None
    assert res.battery_sizing.required_nominal_capacity_ah is None
    assert res.envelope.continuous_current_a is None
    assert any("voltage" in w.lower() for w in res.warnings)


def test_21_missing_battery_specific_energy_handling(standard_hover_result, standard_transition_result):
    """21. Verify missing specific energy marks mass UNRESOLVED and defers to Phase 5 without fabricating mass."""
    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        transition_result=standard_transition_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=44.4,
        specific_energy_wh_kg=None,  # Undefined specific energy
    )
    assert res.battery_sizing.battery_mass_status == "UNRESOLVED_DEFERRED_TO_PHASE5"
    assert res.battery_sizing.estimated_battery_mass_kg is None


def test_22_serialization_to_dict_and_json(standard_hover_result, standard_transition_result):
    """22. Verify recursive serialization to dict and valid JSON."""
    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        transition_result=standard_transition_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=44.4,
    )
    d = res.to_dict()
    assert isinstance(d, dict)
    assert "ledger" in d
    assert "battery_sizing" in d
    assert "envelope" in d
    assert len(d["ledger"]["segments"]) == 10

    # Test roundtrip json dumps
    json_str = json.dumps(d)
    assert len(json_str) > 500


def test_23_pre_convergence_mtow_semantics(standard_hover_result, standard_transition_result):
    """23. Verify pre-convergence MTOW boundary semantics (is_converged_mtow = False)."""
    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        transition_result=standard_transition_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=44.4,
    )
    assert res.is_converged_mtow is False
    assert res.mtow_status == "PRE_CONVERGENCE_SIZING"
    assert res.sizing_mass_kg == 15.0


def test_24_configuration_driven_motor_count(standard_hover_result):
    """24. Verify lift motor count is configuration-driven (e.g. Hexacopter N=6)."""
    res_quad = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=44.4,
    )
    res_hex = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=6,
        hover_result=standard_hover_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=44.4,
    )
    assert res_quad.envelope.lift_bus.motor_count == 4
    assert res_hex.envelope.lift_bus.motor_count == 6
    # Per motor current should be lower for hex with same total power
    assert res_hex.envelope.lift_bus.per_motor_current_a < res_quad.envelope.lift_bus.per_motor_current_a


def test_25_pipeline_integration_electrical_sizing():
    """25. Verify VTOLDesignPipeline end-to-end sets electrical_battery_sizing = IMPLEMENTED."""
    req = VTOLRequirementModel.create(
        mission_type=MissionType.SURVEY,
        payload_mass=2.5,
        target_range=35.0,
        target_flight_time=25.0,
        cruise_speed=85.0,
        vtol_type=VTOLType.LIFT_CRUISE,
        hover_duration_min=4.0,
        lift_motor_count=4,
        system_voltage_v=44.4,
    )
    pipeline = VTOLDesignPipeline(raise_on_failure=False)
    result = pipeline.execute(req)

    assert result.is_success is True
    spec = result.final_specification
    assert spec is not None
    assert spec.stage_statuses["electrical_battery_sizing"] == "IMPLEMENTED"
    assert spec.electrical is not None
    assert spec.electrical.battery_sizing is not None
    assert spec.electrical.battery_sizing.mission_energy_wh > 0.0


def test_26_parameter_provenance_matrix_classifications(standard_hover_result, standard_transition_result):
    """26. Verify parameter provenance matrix classifies all parameters into required taxonomy."""
    res = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        transition_result=standard_transition_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=44.4,
        specific_energy_wh_kg=200.0,
    )
    prov = res.parameter_provenance
    assert prov is not None
    assert len(prov) >= 8

    # Check allowed taxonomy
    allowed_classifications = {
        "DERIVED",
        "PROJECT_REQUIREMENT",
        "CONFIGURABLE_ASSUMPTION",
        "UNRESOLVED_INPUT",
        "DEFERRED",
    }

    for param, data in prov.items():
        assert "classification" in data
        assert "value" in data
        assert "provenance_source" in data
        assert data["classification"] in allowed_classifications, f"Invalid classification for {param}: {data['classification']}"

    # Verify specific classifications
    assert prov["hover_electrical_power_w"]["classification"] == "DERIVED"
    assert prov["transition_energy_wh"]["classification"] == "DERIVED"
    assert prov["cruise_electrical_power_w"]["classification"] == "DERIVED"
    assert prov["reserve_fraction"]["classification"] == "PROJECT_REQUIREMENT"
    assert prov["usable_dod_fraction"]["classification"] == "CONFIGURABLE_ASSUMPTION"
    assert prov["avionics_power_w"]["classification"] == "UNRESOLVED_INPUT"  # Fallback used
    assert prov["battery_mass_convergence"]["classification"] == "DEFERRED"

    # Serialization check
    serialized = res.to_dict()
    assert "parameter_provenance" in serialized
    assert serialized["parameter_provenance"]["hover_electrical_power_w"]["classification"] == "DERIVED"


def test_27_dynamic_avionics_power_derivation(standard_hover_result, standard_transition_result):
    """27. Verify avionics power can be explicitly provided or derived with DERIVED provenance."""
    # 1. Configured input
    res_configured = AuthoritativeEnergyModel.calculate_mission_energy(
        sizing_mass_kg=15.0,
        lift_motor_count=4,
        hover_result=standard_hover_result,
        transition_result=standard_transition_result,
        cruise_propulsion_power_w=350.0,
        system_voltage_v=44.4,
        avionics_power_w=28.5,
        avionics_power_provenance="DERIVED",
    )
    assert res_configured.parameter_provenance["avionics_power_w"]["classification"] == "DERIVED"
    assert res_configured.parameter_provenance["avionics_power_w"]["value"] == 28.5
    seg_pre = res_configured.ledger.get_segment(VTOLMissionPhase.GROUND_PREFLIGHT)
    assert seg_pre.avionics_power_w == 28.5
    assert seg_pre.calculation_source == "AVIONICS_SUBSYSTEM_ANALYSIS"

