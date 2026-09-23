"""
Integration and regression test suite for Torq Wings Fixed-Wing Multi-Engine Propulsion,
Downstream Mass/Power Propagation, JSON Serialization, and Pareto Runner Access.

Covers Tests 1 through 17 as mandated by the Integration Correction Specification.
"""

import json
import pytest
import math

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.design_mode import DesignMode
from backend.design.common.requirements.aircraft_type import AircraftType

from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline, PipelineStatus
from backend.design.fixed_wing.optimization.pareto.dominance import check_dominance
from backend.design.fixed_wing.optimization.pareto.extractor import self_check_pareto_front
from scripts.run_fixed_wing_pipeline import to_dict, audit_mass_accounting


@pytest.fixture(scope="module")
def delivery_requirements():
    """Exact manual case that exposed the multi-engine inconsistency."""
    return RequirementModel(
        mission_type=MissionType.DELIVERY,
        payload_weight_kg=1.0,
        target_flight_time_min=45.0,
        target_range_km=40.0,
        cruise_speed_kmh=80.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
        design_mode=DesignMode.ENGINEERING_ADVISOR,
        aircraft_type=AircraftType.FIXED_WING,
    )


@pytest.fixture(scope="module")
def survey_requirements():
    """Representative single-engine baseline requirement."""
    return RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
        design_mode=DesignMode.ENGINEERING_ADVISOR,
        aircraft_type=AircraftType.FIXED_WING,
    )


# ==============================================================================
# TEST 1: Single-engine architecture (engine_count = 1)
# ==============================================================================
def test_1_single_engine_architecture(survey_requirements):
    """Verify single-engine architecture sizes exactly 1 propulsion unit."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=True)
    res = pipeline.execute(survey_requirements)

    assert res.success is True
    assert res.converged is True

    # Configuration inspection
    cfg = res.configuration_result.selected_configuration
    assert int(cfg.get("engine_count", 1)) == 1

    # Propulsion inspection
    prop = res.propulsion_result
    pa = prop.power_analysis
    assert pa.metadata.get("engine_count", 1) == 1

    # Subsystem specification check
    spec = res.final_specification.propulsion_specification
    assert getattr(spec, "engine_count", 1) == 1


# ==============================================================================
# TEST 2: Twin-engine architecture (engine_count = 2)
# ==============================================================================
def test_2_twin_engine_architecture(delivery_requirements):
    """Verify twin-engine architecture sizes 2 motors, 2 propellers, 2 ESCs."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=True)
    res = pipeline.execute(delivery_requirements)

    assert res.success is True
    assert res.converged is True

    # Configuration layout
    cfg = res.configuration_result.selected_configuration
    assert int(cfg.get("engine_count", 1)) == 2
    assert "Twin" in cfg.get("architecture", "")
    assert "Twin" in cfg.get("propulsion_layout", "")

    # Propulsion inspection
    pa = res.propulsion_result.power_analysis
    assert pa.metadata.get("engine_count") == 2

    # Final specification check
    prop_spec = res.final_specification.propulsion_specification
    assert prop_spec.engine_count == 2
    assert "2x" in prop_spec.reasoning


# ==============================================================================
# TEST 3: Twin thrust scaling
# ==============================================================================
def test_3_twin_thrust(delivery_requirements):
    """Verify total static thrust = per-unit thrust * engine_count."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=True)
    res = pipeline.execute(delivery_requirements)

    ta = res.propulsion_result.thrust_analysis
    pa = res.propulsion_result.power_analysis
    per_motor_thrust = pa.metadata.get("per_motor_static_thrust_n")
    engine_count = pa.metadata.get("engine_count", 2)

    assert engine_count == 2
    assert per_motor_thrust is not None
    assert math.isclose(ta.estimated_static_thrust_n, per_motor_thrust * 2, rel_tol=1e-2)
    # Total thrust for 2x AT3520 should be ~71.1 N
    assert ta.estimated_static_thrust_n > 50.0


# ==============================================================================
# ==============================================================================
# TEST 4: Twin propulsion mass scaling
# ==============================================================================
def test_4_twin_propulsion_mass(delivery_requirements):
    """Verify propulsion mass scales correctly with 2 units."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=True)
    res = pipeline.execute(delivery_requirements)

    wb = res.mass_properties_result.weight_breakdown
    motor_comp = next((c for c in res.mass_properties_result.component_masses if c.name == "Motor"), None)
    prop_comp = next((c for c in res.mass_properties_result.component_masses if c.name == "Propeller"), None)
    esc_comp = next((c for c in res.mass_properties_result.component_masses if c.name == "ESC"), None)

    assert motor_comp is not None
    assert prop_comp is not None
    assert esc_comp is not None

    # Motor mass should be 2x per-motor mass (2 * 0.310 = 0.620 kg)
    # Prop mass should be 2x per-propeller mass (2 * 0.065 = 0.130 kg)
    # ESC mass should be 2x per-ESC mass (2 * 0.080 = 0.160 kg)
    assert math.isclose(motor_comp.mass_kg, 0.620, rel_tol=1e-2)
    assert math.isclose(prop_comp.mass_kg, 0.130, rel_tol=1e-2)
    assert math.isclose(esc_comp.mass_kg, 0.160, rel_tol=1e-2)

    propulsion_weight_kg = wb.propulsion_weight_kg
    assert math.isclose(propulsion_weight_kg, motor_comp.mass_kg + prop_comp.mass_kg + esc_comp.mass_kg, rel_tol=1e-3)
    assert propulsion_weight_kg > 0.60


# ==============================================================================
# TEST 5: Twin power propagation
# ==============================================================================
def test_5_twin_power(delivery_requirements):
    """Verify total power and cruise current are correctly propagated."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=True)
    res = pipeline.execute(delivery_requirements)

    pa = res.propulsion_result.power_analysis
    per_motor_cruise = pa.metadata.get("per_motor_cruise_power_w", 0.0)
    total_cruise = pa.required_cruise_power_w

    assert per_motor_cruise > 0.0
    assert math.isclose(total_cruise, per_motor_cruise * 2, rel_tol=1e-2)

    # Current draw check: Total cruise current = total_power / voltage
    voltage_v = pa.metadata.get("voltage_v", 22.2)
    expected_current = total_cruise / voltage_v
    assert math.isclose(pa.current_draw_cruise_a, expected_current, rel_tol=1e-2)


# ==============================================================================
# TEST 6: Twin battery sizing responds to corrected power
# ==============================================================================
def test_6_twin_battery(delivery_requirements):
    """Verify battery sizing uses corrected mission energy demand."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=True)
    res = pipeline.execute(delivery_requirements)

    prop_spec = res.final_specification.propulsion_specification
    # Total required energy Wh must reflect 2 engines + avionics/payload
    p_cruise = prop_spec.cruise_power_w
    target_min = delivery_requirements.target_flight_time_min
    expected_min_energy_wh = p_cruise * (target_min / 60.0)

    assert prop_spec.required_energy_wh >= expected_min_energy_wh * 0.95
    assert res.mass_properties_result.weight_breakdown.battery_fuel_weight_kg > 0.5


# ==============================================================================
# TEST 7: Twin mass conservation
# ==============================================================================
def test_7_twin_mass_conservation(delivery_requirements):
    """Verify sum(component masses) == MTOW to numerical tolerance."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=True)
    res = pipeline.execute(delivery_requirements)

    audit = audit_mass_accounting(res)
    assert audit["is_consistent"] is True
    assert audit["relative_error_pct"] < 0.1  # Within 0.1% tolerance
    assert audit["delta_kg"] < 0.005


# ==============================================================================
# TEST 8: Twin T/W uses total aircraft static thrust
# ==============================================================================
def test_8_twin_tw(delivery_requirements):
    """Verify aircraft-level T/W uses total aircraft static thrust."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=True)
    res = pipeline.execute(delivery_requirements)

    ta = res.propulsion_result.thrust_analysis
    mtow = sum(c.mass_kg for c in res.mass_properties_result.component_masses)
    g = 9.80665
    expected_tw = ta.estimated_static_thrust_n / (mtow * g)

    assert math.isclose(ta.thrust_to_weight_ratio, expected_tw, rel_tol=1e-2)
    # T/W must be significantly above single-engine 0.86 due to 2x engines (~1.3-1.6)
    assert ta.thrust_to_weight_ratio > 1.0


# ==============================================================================
# TEST 9: Configuration consistency
# ==============================================================================
def test_9_configuration_consistency(delivery_requirements):
    """Verify architecture, engine_count, and propulsion result fully agree."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=True)
    res = pipeline.execute(delivery_requirements)

    cfg = res.configuration_result.selected_configuration
    prop_res = res.propulsion_result
    spec = res.final_specification

    # Config says Twin
    assert "Twin" in cfg["architecture"]
    assert cfg["engine_count"] == "2"

    # Propulsion result agrees
    assert prop_res.power_analysis.metadata["engine_count"] == 2
    assert "2x" in prop_res.engineering_notes[3]
    assert "Total static thrust" in prop_res.engineering_notes[5]

    # Specification agrees
    assert spec.propulsion_specification.engine_count == 2


# ==============================================================================
# TEST 10: Single-engine regression preservation
# ==============================================================================
def test_10_single_engine_regression(survey_requirements):
    """Existing single-engine baseline must remain numerically unchanged."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=True)
    res = pipeline.execute(survey_requirements)

    assert res.success is True
    assert res.converged is True

    # Compare with established Phase 6B-4 / 6B-6 baseline: MTOW ~ 3.655 kg
    mtow = sum(c.mass_kg for c in res.mass_properties_result.component_masses)
    assert math.isclose(mtow, 3.655, abs_tol=0.010)

    # Static thrust should match single motor ~35.55 N
    ta = res.propulsion_result.thrust_analysis
    assert math.isclose(ta.estimated_static_thrust_n, 35.55, abs_tol=0.5)


# ==============================================================================
# TEST 11: Delivery real case execution
# ==============================================================================
def test_11_delivery_real_case(delivery_requirements):
    """Run the exact 1 kg / 45 min / 40 km Delivery case."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=True)
    res = pipeline.execute(delivery_requirements)

    assert res.success is True
    assert res.converged is True
    assert res.status == PipelineStatus.SUCCESS
    assert res.verification_result is not None


# ==============================================================================
# TEST 12: JSON serialization (final_specification is NOT {})
# ==============================================================================
def test_12_json_serialization(delivery_requirements):
    """Verify serialized final_specification is NOT empty and contains engineering sections."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=True)
    res = pipeline.execute(delivery_requirements)

    serialized_spec = to_dict(res.final_specification)
    assert isinstance(serialized_spec, dict)
    assert len(serialized_spec) > 0
    assert serialized_spec != {}

    # Check that required engineering sections are present
    expected_sections = [
        "configuration",
        "wing",
        "fuselage",
        "tail",
        "propulsion",
        "electrical",
        "mass_properties",
        "performance",
        "convergence_report",
    ]
    for section in expected_sections:
        assert section in serialized_spec, f"Section '{section}' missing from serialized final_specification"


# ==============================================================================
# TEST 13: JSON contains propulsion details
# ==============================================================================
def test_13_json_propulsion_details(delivery_requirements):
    """Verify JSON output contains full propulsion details."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=True)
    res = pipeline.execute(delivery_requirements)

    data = to_dict(res)
    prop_data = data.get("propulsion_result") or data.get("final_specification", {}).get("propulsion")

    assert prop_data is not None
    thrust = prop_data.get("thrust_analysis", {})
    assert thrust.get("estimated_static_thrust_n", 0.0) > 50.0


# ==============================================================================
# TEST 14: JSON contains complete mass accounting
# ==============================================================================
def test_14_json_mass_accounting(delivery_requirements):
    """Verify JSON output contains complete mass accounting."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=True)
    res = pipeline.execute(delivery_requirements)

    audit = audit_mass_accounting(res)
    audit_dict = to_dict(audit)

    assert audit_dict["is_consistent"] is True
    assert audit_dict["reported_mtow_kg"] > 0.0
    assert audit_dict["structural_mass_kg"] > 0.0
    assert audit_dict["propulsion_mass_kg"] > 0.0
    assert audit_dict["battery_mass_kg"] > 0.0


# ==============================================================================
# TEST 15: Pareto disabled behavior
# ==============================================================================
def test_15_pareto_disabled(delivery_requirements):
    """When pareto=False, pareto_front is None and pipeline behavior is unaffected."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=True)
    res = pipeline.execute(delivery_requirements, pareto=False)

    assert res.pareto_front is None
    assert res.success is True


# ==============================================================================
# TEST 16: Pareto enabled behavior
# ==============================================================================
def test_16_pareto_enabled(survey_requirements):
    """When pareto=True, existing Pareto extractor is invoked and result is populated."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=True)
    res = pipeline.execute(survey_requirements, pareto=True)

    assert res.pareto_front is not None
    assert res.pareto_front.enabled is True
    assert res.pareto_front.front_size >= 1
    assert len(res.pareto_front.front) == res.pareto_front.front_size


# ==============================================================================
# TEST 17: Pareto mathematical self-check
# ==============================================================================
def test_17_pareto_mathematical_self_check(survey_requirements):
    """Every returned Pareto candidate is feasible and mutually nondominated."""
    pipeline = FixedWingDesignPipeline(raise_on_failure=True)
    res = pipeline.execute(survey_requirements, pareto=True)

    pf = res.pareto_front
    is_valid, errors = self_check_pareto_front(pf)
    assert is_valid is True, f"Pareto self-check failed with errors: {errors}"
