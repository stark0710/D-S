"""
Unit tests for Drone Structural Engineering Framework.
"""

import pytest
from backend.design.common.requirements import MissionType
from backend.design.drone.mission import DroneMissionProfile
from backend.design.drone.configuration import ConfigurationEngine
from backend.design.drone.structure import (
    ArmGeometry,
    LandingGear,
    MountingLayout,
    FrameProfile,
    FrameConstraints,
    FrameResult,
    FrameValidator,
    FrameAnalysis,
    FrameSelector,
    StructureEngine,
)


def test_frame_analysis_calculations():
    """Verify FrameAnalysis wheelbase, arm length, and max propeller diameter calculations."""
    analysis = FrameAnalysis()

    # Hexacopter 6 kg AUW
    wb = analysis.calculate_wheelbase(rotor_count=6, estimated_auw_kg=6.0, coaxial=False)
    arm_len = analysis.calculate_arm_length(wheelbase_mm=wb, rotor_count=6)
    max_prop = analysis.calculate_max_propeller_inch(wheelbase_mm=wb, rotor_count=6)
    fw = analysis.estimate_frame_weight(wheelbase_mm=wb, rotor_count=6)

    assert wb == 680.0
    assert arm_len == 340.0
    assert max_prop > 10.0
    assert fw > 200.0


def test_frame_selector_strategy_picking():
    """Verify FrameSelector picks HeavyLift for heavy payload and Lightweight for ultralight endurance."""
    selector = FrameSelector()

    # Heavy payload (10 kg) -> HeavyLiftFrameStrategy
    m_heavy = DroneMissionProfile(MissionType.CARGO if hasattr(MissionType, 'CARGO') else MissionType.DELIVERY, 10.0, 15.0, 15.0, 15.0, 50.0)
    config_engine = ConfigurationEngine()
    cfg_heavy = config_engine.evaluate_configurations(m_heavy)

    s_heavy = selector.select_frame_strategy(m_heavy, cfg_heavy)
    assert s_heavy == "HeavyLiftFrameStrategy"

    # Lightweight (0.5 kg, 40 min flight time) -> LightweightFrameStrategy
    m_light = DroneMissionProfile(MissionType.SURVEY, 0.5, 20.0, 20.0, 15.0, 40.0)
    cfg_light = config_engine.evaluate_configurations(m_light)

    s_light = selector.select_frame_strategy(m_light, cfg_light)
    assert s_light == "LightweightFrameStrategy"


def test_structure_engine_execution():
    """Verify StructureEngine designs physical frame, arm geometry, mounting layout, and landing gear."""
    mission = DroneMissionProfile(
        mission_type=MissionType.AGRICULTURE,
        payload_weight_kg=3.0,
        target_hover_time_min=15.0,
        target_cruise_time_min=15.0,
        target_range_km=15.0,
        cruise_speed_kmh=50.0
    )

    config_engine = ConfigurationEngine()
    cfg_result = config_engine.evaluate_configurations(mission)

    engine = StructureEngine()
    frame_result = engine.design_structure(mission, cfg_result)

    assert isinstance(frame_result, FrameResult)
    assert frame_result.selected_frame.wheelbase_mm > 0
    assert frame_result.arm_geometry.arm_length_mm > 0
    assert frame_result.landing_gear.ground_clearance_mm >= 120.0
    assert frame_result.mounting_layout.flight_controller_pattern_mm != ""
    assert frame_result.estimated_structure_weight_g > 0
