"""
Unit tests for Drone Mission Engineering Framework.
"""

import pytest
from backend.design.common.requirements import MissionType
from backend.design.drone.mission import (
    DroneMissionProfile,
    DroneMissionRequirements,
    DroneMissionConstraints,
    DroneMissionResult,
    DroneMissionValidator,
    DroneMissionAnalysis,
    DroneMissionEngine,
)


def test_drone_mission_engine_normal_profile():
    """Verify DroneMissionEngine processes a standard multirotor delivery mission."""
    profile = DroneMissionProfile(
        mission_type=MissionType.DELIVERY,
        payload_weight_kg=2.0,
        target_hover_time_min=10.0,
        target_cruise_time_min=20.0,
        target_range_km=15.0,
        cruise_speed_kmh=50.0,
        max_wind_speed_m_s=8.0
    )

    engine = DroneMissionEngine()
    result = engine.process_mission(profile)

    assert isinstance(result, DroneMissionResult)
    assert result.engineering_requirements.required_payload_kg == 2.0
    assert result.engineering_requirements.estimated_auw_target_kg > 6.0
    assert result.engineering_requirements.flight_time_target_min == 30.0
    assert result.constraints.max_takeoff_weight_kg > result.engineering_requirements.estimated_auw_target_kg
    assert len(result.warnings) == 0


def test_drone_mission_validator_warnings():
    """Verify DroneMissionValidator issues warnings for extreme mission profiles."""
    profile_extreme = DroneMissionProfile(
        mission_type=MissionType.MILITARY,
        payload_weight_kg=20.0,  # High payload
        target_hover_time_min=30.0,
        target_cruise_time_min=45.0,  # Total 75 min exceeds battery density
        target_range_km=50.0,
        cruise_speed_kmh=60.0,
        max_wind_speed_m_s=18.0  # High wind
    )

    validator = DroneMissionValidator()
    warnings = validator.validate_mission(profile_extreme)

    assert len(warnings) >= 3
    assert any("flight time" in w for w in warnings)
    assert any("High payload mass" in w for w in warnings)
    assert any("High operational wind tolerance" in w for w in warnings)


def test_drone_mission_analysis_derivation():
    """Verify DroneMissionAnalysis derives estimated AUW targets and hover power margins."""
    profile = DroneMissionProfile(
        mission_type=MissionType.AGRICULTURE,
        payload_weight_kg=5.0,
        target_hover_time_min=15.0,
        target_cruise_time_min=15.0,
        target_range_km=10.0,
        cruise_speed_kmh=40.0,
        max_wind_speed_m_s=10.0
    )

    analysis = DroneMissionAnalysis()
    reqs = analysis.derive_requirements(profile)
    constraints = analysis.derive_constraints(profile, reqs)

    assert reqs.estimated_auw_target_kg == round(5.0 * 3.3, 2)
    assert reqs.hover_power_margin_min >= 1.8
    assert constraints.max_takeoff_weight_kg > reqs.estimated_auw_target_kg
