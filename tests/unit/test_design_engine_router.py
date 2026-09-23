"""
Unit tests for Design Engine Routing Framework.
"""

import pytest
from backend.design.common.requirements import (
    MissionType,
    AircraftType,
    RequirementModel,
)
from backend.design.common.context import (
    DesignStage,
    DesignStatus,
    ContextBuilder,
    DesignContext,
)
from backend.design.router import (
    DesignEngine,
    RoutingResult,
    RoutingContext,
    DesignEngineRegistry,
    DesignEngineRouter,
    EngineNotRegisteredError,
    UnsupportedAircraftTypeError,
    DuplicateRegistrationError,
)


class MockDroneDesignEngine(DesignEngine):
    """Mock engine supporting Quadcopter, Hexacopter, and Octocopter."""

    @property
    def engine_id(self) -> str:
        return "drone_design_studio_v1"

    @property
    def supported_aircraft_types(self) -> list[AircraftType]:
        return [AircraftType.QUADCOPTER, AircraftType.HEXACOPTER, AircraftType.OCTOCOPTER]

    def execute_design(self, context: DesignContext) -> DesignContext:
        context.design_data["drone_sized"] = True
        return context


class MockFixedWingDesignEngine(DesignEngine):
    """Mock engine supporting Fixed-Wing UAVs."""

    @property
    def engine_id(self) -> str:
        return "fixed_wing_design_studio_v1"

    @property
    def supported_aircraft_types(self) -> list[AircraftType]:
        return [AircraftType.FIXED_WING]

    def execute_design(self, context: DesignContext) -> DesignContext:
        context.design_data["fixed_wing_sized"] = True
        return context


def test_registry_registration_and_lookup():
    """Verify registering engines into DesignEngineRegistry and resolving by ID and aircraft type."""
    registry = DesignEngineRegistry()
    drone_engine = MockDroneDesignEngine()
    fw_engine = MockFixedWingDesignEngine()

    registry.register_engine(drone_engine)
    registry.register_engine(fw_engine)

    assert len(registry.registered_engines()) == 2
    assert registry.get_engine_by_id("drone_design_studio_v1") == drone_engine
    assert registry.get_engine_by_aircraft_type(AircraftType.QUADCOPTER) == drone_engine
    assert registry.get_engine_by_aircraft_type(AircraftType.FIXED_WING) == fw_engine


def test_duplicate_registration_raises_error():
    """Verify DuplicateRegistrationError is raised when registering duplicate IDs or aircraft types."""
    registry = DesignEngineRegistry()
    drone_engine1 = MockDroneDesignEngine()
    drone_engine2 = MockDroneDesignEngine()

    registry.register_engine(drone_engine1)

    with pytest.raises(DuplicateRegistrationError):
        registry.register_engine(drone_engine2)


def test_unregistered_engine_lookup_raises_error():
    """Verify EngineNotRegisteredError and UnsupportedAircraftTypeError are raised for missing registrations."""
    registry = DesignEngineRegistry()

    with pytest.raises(EngineNotRegisteredError):
        registry.get_engine_by_id("missing_id")

    with pytest.raises(UnsupportedAircraftTypeError):
        registry.get_engine_by_aircraft_type(AircraftType.VTOL)


def test_design_engine_router_multirotor():
    """Verify DesignEngineRouter dispatches Quadcopter context to drone engine and advances stage to DRONE_DESIGN."""
    registry = DesignEngineRegistry()
    drone_engine = MockDroneDesignEngine()
    registry.register_engine(drone_engine)

    router = DesignEngineRouter(registry=registry)

    req = RequirementModel(
        mission_type=MissionType.AGRICULTURE,
        payload_weight_kg=2.5,
        target_flight_time_min=30.0,
        target_range_km=15.0,
        cruise_speed_kmh=50.0,
        aircraft_type=AircraftType.QUADCOPTER
    )
    context = ContextBuilder.create_context(req)

    routed_context = router.route(context)

    assert routed_context.selected_design_engine == "drone_design_studio_v1"
    assert routed_context.selected_aircraft_type == AircraftType.QUADCOPTER
    assert routed_context.current_stage == DesignStage.DRONE_DESIGN
    assert routed_context.current_status == DesignStatus.IN_PROGRESS
    assert len(routed_context.snapshots) == 2


def test_design_engine_router_fixed_wing():
    """Verify DesignEngineRouter dispatches Fixed-Wing context to fixed-wing engine and advances stage to FIXED_WING_DESIGN."""
    registry = DesignEngineRegistry()
    fw_engine = MockFixedWingDesignEngine()
    registry.register_engine(fw_engine)

    router = DesignEngineRouter(registry=registry)

    req = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=2.0,
        target_flight_time_min=60.0,
        target_range_km=40.0,
        cruise_speed_kmh=70.0
    )
    context = ContextBuilder.create_context(req)
    context.selected_aircraft_type = AircraftType.FIXED_WING

    routed_context = router.route(context)

    assert routed_context.selected_design_engine == "fixed_wing_design_studio_v1"
    assert routed_context.current_stage == DesignStage.FIXED_WING_DESIGN


def test_routing_without_aircraft_type_raises_error():
    """Verify UnsupportedAircraftTypeError is raised when routing context lacking selected_aircraft_type."""
    router = DesignEngineRouter()

    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=1.0,
        target_flight_time_min=20.0,
        target_range_km=10.0,
        cruise_speed_kmh=50.0,
        aircraft_type=None
    )
    context = ContextBuilder.create_context(req)

    with pytest.raises(UnsupportedAircraftTypeError):
        router.route(context)
