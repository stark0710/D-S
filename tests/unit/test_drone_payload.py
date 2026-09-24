"""
Unit tests for Drone Payload Integration Engineering Framework.
"""

import pytest
from backend.design.common.requirements import MissionType
from backend.design.drone.mission import DroneMissionProfile
from backend.design.drone.configuration import ConfigurationEngine
from backend.design.drone.structure import StructureEngine
from backend.design.drone.propulsion import PropulsionEngine
from backend.design.drone.electrical import ElectricalEngine
from backend.design.drone.avionics import AvionicsEngine
from backend.design.drone.payload import (
    PayloadSelector,
    PayloadMount,
    PayloadInterface,
    PayloadPowerAnalysis,
    PayloadBalanceAnalysis,
    PayloadVibrationAnalysis,
    PayloadResult,
    PayloadValidator,
    PayloadConstraints,
    PayloadEngine,
)


def test_payload_selector_supported_types():
    """Verify PayloadSelector selects RGB, LiDAR, Sprayer, Delivery Box, Thermal, and Custom payloads."""
    selector = PayloadSelector()

    rgb_spec = selector.select_payload("MAPPING")
    assert rgb_spec["payload_type"] == "RGB_CAMERA"

    lidar_spec = selector.select_payload("LIDAR")
    assert lidar_spec["payload_type"] == "LIDAR"

    sprayer_spec = selector.select_payload("AGRICULTURE")
    assert sprayer_spec["payload_type"] == "SPRAYER"

    delivery_spec = selector.select_payload("DELIVERY")
    assert delivery_spec["payload_type"] == "DELIVERY_BOX"

    custom_spec = selector.select_payload("CUSTOM", custom_payload_spec={"name": "Gas Sensor", "mass_kg": 0.5})
    assert custom_spec["payload_type"] == "CUSTOM"
    assert custom_spec["payload_name"] == "Gas Sensor"


def test_payload_physics_analyses():
    """Verify PayloadPowerAnalysis, PayloadBalanceAnalysis, and PayloadVibrationAnalysis."""
    pwr_analysis = PayloadPowerAnalysis()
    pwr_res = pwr_analysis.analyze_power(payload_power_w=12.0, voltage_v=12.0, total_hover_power_w=300.0)

    assert pwr_res.current_draw_a == 1.0
    assert pwr_res.percentage_of_total_power == 4.0

    bal_analysis = PayloadBalanceAnalysis()
    bal_res = bal_analysis.analyze_balance(payload_mass_kg=2.0, offset_x_mm=10.0, offset_y_mm=0.0, offset_z_mm=100.0)

    assert bal_res.pitch_moment_arm_n_m > 0
    assert bal_res.roll_moment_arm_n_m == 0.0

    vib_analysis = PayloadVibrationAnalysis()
    vib_res = vib_analysis.analyze_vibration(payload_mass_kg=2.0, sensitive_imaging=True)

    assert vib_res.vibration_attenuation_db < 0


def test_payload_engine_execution():
    """Verify PayloadEngine integrates mission payload, mount, interface, power, balance, and vibration."""
    mission = DroneMissionProfile(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=1.5,
        target_hover_time_min=15.0,
        target_cruise_time_min=15.0,
        target_range_km=15.0,
        cruise_speed_kmh=50.0
    )

    config_engine = ConfigurationEngine()
    cfg_result = config_engine.evaluate_configurations(mission)

    structure_engine = StructureEngine()
    frame_result = structure_engine.design_structure(mission, cfg_result)

    propulsion_engine = PropulsionEngine()
    prop_result = propulsion_engine.design_propulsion(mission, cfg_result, frame_result)

    electrical_engine = ElectricalEngine()
    elec_result = electrical_engine.design_electrical(mission, cfg_result, frame_result, prop_result)

    avionics_engine = AvionicsEngine()
    avionics_result = avionics_engine.design_avionics(mission, cfg_result, frame_result, prop_result, elec_result)

    payload_engine = PayloadEngine()
    payload_result = payload_engine.integrate_payload(
        mission, cfg_result, frame_result, prop_result, elec_result, avionics_result, strategy_name="MappingPayloadStrategy"
    )

    assert isinstance(payload_result, PayloadResult)
    assert payload_result.selected_payload.payload_name != ""
    assert payload_result.mounting_solution.mount_type != ""
    assert payload_result.interface_definition.power_connector != ""
    assert payload_result.power_analysis.payload_power_w > 0
    assert payload_result.balance_analysis.cg_offset_z_mm > 0
    assert payload_result.vibration_analysis.isolation_frequency_hz > 0
