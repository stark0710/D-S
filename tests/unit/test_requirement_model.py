"""
Unit tests for RequirementModel and requirement enums.
"""

import pytest
from backend.design.common.requirements import (
    MissionType,
    AircraftType,
    TakeoffType,
    LandingType,
    OperatingEnvironment,
    OptimizationPriority,
    DesignMode,
    RequirementModel,
)


def test_requirement_enums():
    """Verify enum members and string value representation."""
    assert MissionType.SURVEY == "SURVEY"
    assert MissionType.AGRICULTURE == "AGRICULTURE"
    assert AircraftType.QUADCOPTER == "QUADCOPTER"
    assert AircraftType.VTOL == "VTOL"
    assert TakeoffType.VERTICAL == "VERTICAL"
    assert TakeoffType.CATAPULT == "CATAPULT"
    assert LandingType.VERTICAL == "VERTICAL"
    assert LandingType.PARACHUTE == "PARACHUTE"
    assert OperatingEnvironment.URBAN == "URBAN"
    assert OperatingEnvironment.RURAL == "RURAL"
    assert OptimizationPriority.BALANCED == "BALANCED"
    assert OptimizationPriority.LOWEST_COST == "LOWEST_COST"
    assert DesignMode.ENGINEERING_ADVISOR == "ENGINEERING_ADVISOR"
    assert DesignMode.MANUAL == "MANUAL"


def test_requirement_model_construction():
    """Verify RequirementModel initialization in Engineering Advisor mode with optional fields."""
    req = RequirementModel(
        mission_type=MissionType.AGRICULTURE,
        payload_weight_kg=2.5,
        target_flight_time_min=45.0,
        target_range_km=40.0,
        cruise_speed_kmh=60.0
    )

    assert req.mission_type == MissionType.AGRICULTURE
    assert req.payload_weight_kg == 2.5
    assert req.target_flight_time_min == 45.0
    assert req.target_range_km == 40.0
    assert req.cruise_speed_kmh == 60.0

    # Defaults
    assert req.aircraft_type is None
    assert req.maximum_takeoff_weight_kg is None
    assert req.budget is None
    assert req.takeoff_type == TakeoffType.VERTICAL
    assert req.landing_type == LandingType.VERTICAL
    assert req.environment == OperatingEnvironment.RURAL
    assert req.optimization_priority == OptimizationPriority.BALANCED
    assert req.design_mode == DesignMode.ENGINEERING_ADVISOR
    assert req.metadata == {}


def test_requirement_model_manual_mode():
    """Verify RequirementModel initialization in Manual mode with specified aircraft type."""
    req = RequirementModel(
        mission_type=MissionType.DELIVERY,
        payload_weight_kg=5.0,
        target_flight_time_min=30.0,
        target_range_km=25.0,
        cruise_speed_kmh=80.0,
        aircraft_type=AircraftType.HEXACOPTER,
        maximum_takeoff_weight_kg=25.0,
        budget=15000.0,
        design_mode=DesignMode.MANUAL,
        metadata={"customer": "Logistics Co"}
    )

    assert req.aircraft_type == AircraftType.HEXACOPTER
    assert req.maximum_takeoff_weight_kg == 25.0
    assert req.budget == 15000.0
    assert req.design_mode == DesignMode.MANUAL
    assert req.metadata == {"customer": "Logistics Co"}


def test_requirement_model_slots():
    """Verify @dataclass(slots=True) prevents setting dynamic arbitrary attributes."""
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=1.0,
        target_flight_time_min=20.0,
        target_range_km=10.0,
        cruise_speed_kmh=50.0
    )

    with pytest.raises(AttributeError):
        req.arbitrary_attribute = "invalid"  # type: ignore
