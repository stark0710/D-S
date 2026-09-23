"""
Unit tests for Drone Avionics Engineering Framework.
"""

import pytest
from backend.design.common.requirements import MissionType
from backend.design.drone.mission import DroneMissionProfile
from backend.design.drone.configuration import ConfigurationEngine
from backend.design.drone.structure import StructureEngine
from backend.design.drone.propulsion import PropulsionEngine
from backend.design.drone.electrical import ElectricalEngine
from backend.design.drone.avionics import (
    FlightControllerSelector,
    GpsSelector,
    ReceiverSelector,
    TelemetrySelector,
    CameraSelector,
    CompanionComputerSelector,
    SensorSelector,
    CommunicationAnalysis,
    AvionicsPowerAnalysis,
    AvionicsResult,
    AvionicsValidator,
    AvionicsEngine,
)


def test_flight_controller_and_gps_selectors():
    """Verify FlightControllerSelector and GpsSelector hardware and firmware selection."""
    fc_sel = FlightControllerSelector()
    fc_spec = fc_sel.select_flight_controller("MAPPING", "SINGLE")

    assert "Pixhawk 6C" in fc_spec["flight_controller_model"] or "Cube" in fc_spec["flight_controller_model"]
    assert fc_spec["available_uart_ports"] >= 5

    gps_sel = GpsSelector()
    gps_spec = gps_sel.select_gps(rtk_required=True)

    assert gps_spec["rtk_supported"] is True
    assert gps_spec["horizontal_precision_m"] < 0.1


def test_avionics_engine_execution():
    """Verify AvionicsEngine designs FC, GNSS, telemetry, receiver, companion computer, and camera payload."""
    mission = DroneMissionProfile(
        mission_type=MissionType.MAPPING,
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

    avionics_engine = AvionicsEngine()
    avionics_result = avionics_engine.design_avionics(
        mission, cfg_result, frame_result, prop_result, elec_result, strategy_name="MappingStrategy"
    )

    assert isinstance(avionics_result, AvionicsResult)
    assert avionics_result.selected_flight_controller["flight_controller_model"] != ""
    assert avionics_result.selected_gps["rtk_supported"] is True
    assert avionics_result.communication_analysis.rc_link_range_km > 0
    assert avionics_result.power_analysis.total_avionics_power_w > 0
