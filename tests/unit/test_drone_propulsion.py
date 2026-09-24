"""
Unit tests for Drone Propulsion Engineering Framework.
"""

import pytest
from backend.design.common.requirements import MissionType
from backend.design.drone.mission import DroneMissionProfile
from backend.design.drone.configuration import ConfigurationEngine
from backend.design.drone.structure import StructureEngine
from backend.design.drone.propulsion import (
    ThrustAnalysis,
    PowerAnalysis,
    HoverAnalysis,
    EfficiencyAnalysis,
    MotorSelector,
    PropellerSelector,
    PropulsionResult,
    PropulsionValidator,
    PropulsionConstraints,
    PropulsionEngine,
)


def test_thrust_and_hover_physics_analysis():
    """Verify ThrustAnalysis and HoverAnalysis physics calculations."""
    thrust_engine = ThrustAnalysis()
    thrust_res = thrust_engine.analyze_thrust(auw_kg=6.0, rotor_count=6, target_tw_ratio=2.0)

    assert thrust_res.total_hover_thrust_kg == 6.0
    assert thrust_res.hover_thrust_per_motor_g == 1000.0
    assert thrust_res.max_thrust_per_motor_g == 2000.0
    assert thrust_res.actual_thrust_to_weight_ratio == 2.0

    hover_engine = HoverAnalysis()
    hover_res = hover_engine.analyze_hover(
        auw_kg=6.0,
        hover_thrust_per_motor_g=1000.0,
        max_thrust_per_motor_g=2000.0,
        propeller_diameter_inch=13.0,
        rotor_count=6
    )

    assert hover_res.hover_throttle_percent == 50.0
    assert hover_res.hover_efficiency_g_per_w > 0


def test_motor_and_propeller_selector():
    """Verify MotorSelector and PropellerSelector sizing."""
    motor_sel = MotorSelector()
    motor_spec = motor_sel.select_motor(hover_thrust_per_motor_g=1000.0, max_thrust_per_motor_g=2200.0)

    assert "3510" in motor_spec["stator_size"]

    prop_sel = PropellerSelector()
    prop_spec = prop_sel.select_propeller(motor_spec, max_allowed_diameter_inch=15.0)

    assert prop_spec["diameter_inch"] <= 15.0


def test_propulsion_engine_execution():
    """Verify PropulsionEngine designs motor, propeller, thrust, power, and efficiency subsystems."""
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

    assert isinstance(prop_result, PropulsionResult)
    assert prop_result.selected_motors["motor_class"] != ""
    assert prop_result.selected_propellers["diameter_inch"] > 0
    assert prop_result.thrust_analysis.actual_thrust_to_weight_ratio >= 1.8
    assert prop_result.power_analysis.hover_power_w > 0
    assert prop_result.hover_analysis.hover_throttle_percent > 0
