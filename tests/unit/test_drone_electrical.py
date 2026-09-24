"""
Unit tests for Drone Electrical Power Engineering Framework.
"""

import pytest
from backend.design.common.requirements import MissionType
from backend.design.drone.mission import DroneMissionProfile
from backend.design.drone.configuration import ConfigurationEngine
from backend.design.drone.structure import StructureEngine
from backend.design.drone.propulsion import PropulsionEngine
from backend.design.drone.electrical import (
    BatterySelector,
    EscSelector,
    PdbSelector,
    BecSelector,
    ConnectorSelector,
    WireSelector,
    PowerBudget,
    CurrentAnalysis,
    VoltageAnalysis,
    ElectricalResult,
    ElectricalValidator,
    ElectricalEngine,
)


def test_battery_and_esc_selectors():
    """Verify BatterySelector and EscSelector sizing and parameter calculations."""
    bat_sel = BatterySelector()
    bat_spec = bat_sel.select_battery(voltage_v=22.2, target_endurance_min=20.0, hover_power_w=350.0, chemistry="LiPo")

    assert bat_spec["cell_count_s"] == 6
    assert bat_spec["capacity_mah"] > 0
    assert bat_spec["estimated_battery_weight_g"] > 0

    esc_sel = EscSelector()
    esc_spec = esc_sel.select_escs(peak_current_per_motor_a=35.0, cell_count_s=6, rotor_count=6)

    assert esc_spec["continuous_current_a"] >= 45.0
    assert esc_spec["topology"] != ""


def test_electrical_engine_execution():
    """Verify ElectricalEngine designs battery, ESCs, PDB, BEC, connectors, wiring, and power budget."""
    mission = DroneMissionProfile(
        mission_type=MissionType.DELIVERY,
        payload_weight_kg=2.0,
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

    assert isinstance(elec_result, ElectricalResult)
    assert elec_result.selected_battery["capacity_mah"] > 0
    assert elec_result.selected_escs["continuous_current_a"] > 0
    assert elec_result.selected_connectors["main_connector_type"] != ""
    assert elec_result.selected_wiring["main_battery_wire_awg"] in (8, 10, 12, 14, 16)
    assert elec_result.power_budget.total_hover_power_w > 0
    assert elec_result.estimated_endurance_min > 0
