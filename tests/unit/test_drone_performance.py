"""
Unit tests for Drone Flight Performance Engineering Framework.
"""

import pytest
from backend.design.common.requirements import MissionType
from backend.design.drone.mission import DroneMissionProfile
from backend.design.drone.configuration import ConfigurationEngine
from backend.design.drone.structure import StructureEngine
from backend.design.drone.propulsion import PropulsionEngine
from backend.design.drone.electrical import ElectricalEngine
from backend.design.drone.avionics import AvionicsEngine
from backend.design.drone.payload import PayloadEngine
from backend.design.drone.mass_properties import MassPropertiesEngine
from backend.design.drone.performance import (
    HoverPerformance,
    ClimbPerformance,
    DescentPerformance,
    CruisePerformance,
    StabilityAnalysis,
    WindAnalysis,
    EnergyAnalysis,
    PerformanceResult,
    PerformanceValidator,
    PerformanceEngine,
)


def test_performance_physics_modules():
    """Verify HoverPerformance, ClimbPerformance, DescentPerformance, CruisePerformance, WindAnalysis, EnergyAnalysis."""
    hover_engine = HoverPerformance()
    hover_res = hover_engine.analyze_hover(total_mass_kg=6.0, rotor_count=6, propeller_diameter_inch=13.0, hover_power_w=350.0, actual_tw_ratio=2.0, hover_throttle_percent=50.0)
    assert hover_res.disk_loading_kg_m2 > 0

    climb_engine = ClimbPerformance()
    climb_res = climb_engine.analyze_climb(total_mass_kg=6.0, hover_power_w=350.0, max_power_w=1200.0, actual_tw_ratio=2.0)
    assert climb_res.max_climb_rate_m_s > 0

    descent_engine = DescentPerformance()
    descent_res = descent_engine.analyze_descent(disk_loading_kg_m2=hover_res.disk_loading_kg_m2)
    assert descent_res.max_descent_rate_m_s <= 5.0

    cruise_engine = CruisePerformance()
    cruise_res = cruise_engine.analyze_cruise(total_mass_kg=6.0, hover_power_w=350.0, max_power_w=1200.0, target_cruise_speed_kmh=50.0)
    assert cruise_res.max_horizontal_speed_kmh >= 50.0

    wind_engine = WindAnalysis()
    wind_res = wind_engine.analyze_wind(actual_tw_ratio=2.0, cruise_speed_kmh=50.0)
    assert wind_res.max_wind_tolerance_m_s > 0

    energy_engine = EnergyAnalysis()
    energy_res = energy_engine.analyze_energy(capacity_mah=10000.0, nominal_voltage_v=22.2, hover_power_w=350.0, cruise_power_w=300.0)
    assert energy_res.usable_energy_wh > 0


def test_performance_engine_execution():
    """Verify PerformanceEngine evaluates complete flight performance across all disciplines."""
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

    avionics_engine = AvionicsEngine()
    avionics_result = avionics_engine.design_avionics(mission, cfg_result, frame_result, prop_result, elec_result)

    payload_engine = PayloadEngine()
    payload_result = payload_engine.integrate_payload(
        mission, cfg_result, frame_result, prop_result, elec_result, avionics_result
    )

    mass_engine = MassPropertiesEngine()
    mass_result = mass_engine.analyze_mass_properties(
        frame_result, prop_result, elec_result, avionics_result, payload_result
    )

    perf_engine = PerformanceEngine()
    perf_result = perf_engine.evaluate_performance(
        mission, cfg_result, frame_result, prop_result, elec_result, avionics_result, payload_result, mass_result
    )

    assert isinstance(perf_result, PerformanceResult)
    assert perf_result.flight_time_min > 0
    assert perf_result.max_hover_time_min > 0
    assert perf_result.range_km > 0
    assert perf_result.cruise_speed_kmh == 50.0
    assert perf_result.maximum_speed_kmh > 50.0
    assert perf_result.hover_performance.hover_power_w > 0
    assert perf_result.climb_performance.max_climb_rate_m_s > 0
    assert perf_result.wind_analysis.max_wind_tolerance_m_s > 0
