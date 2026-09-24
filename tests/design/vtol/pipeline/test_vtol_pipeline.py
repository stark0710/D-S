import pytest
import os
import json
import csv
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.aircraft_type import AircraftType
from backend.design.common.context.design_context import DesignContext
from backend.design.common.context.design_status import DesignStatus
from backend.design.router.design_engine_registry import DesignEngineRegistry
from backend.design.router.design_engine_router import DesignEngineRouter

from backend.design.vtol.pipeline.vtol_design_pipeline import VTOLDesignPipeline, VTOLDesignEngine
from backend.design.vtol.pipeline.pipeline_result import PipelineStatus


@pytest.fixture
def base_requirements():
    return RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=3.5,
        target_flight_time_min=30.0,
        target_range_km=45.0,
        cruise_speed_kmh=90.0,
        environment=OperatingEnvironment.RURAL,
        metadata={
            "hover_duration_min": 4.0,
            "transition_speed_kmh": 65.0,
            "preferred_vtol_type": "Lift + Cruise"
        }
    )


def test_pipeline_construction_and_registration():
    """Verify that VTOLDesignEngine implements DesignEngine and registers properly."""
    registry = DesignEngineRegistry()
    engine = VTOLDesignEngine()
    
    assert engine.engine_id == "VTOLDesignEngine"
    assert AircraftType.VTOL in engine.supported_aircraft_types
    
    registry.register_engine(engine)
    assert registry.get_engine_by_id("VTOLDesignEngine") == engine
    assert registry.get_engine_by_aircraft_type(AircraftType.VTOL) == engine


def test_design_routing_and_execution(base_requirements):
    """Verify that DesignEngineRouter correctly dispatches and runs VTOL design."""
    registry = DesignEngineRegistry()
    engine = VTOLDesignEngine()
    registry.register_engine(engine)
    
    router = DesignEngineRouter(registry=registry)
    ctx = DesignContext(
        requirement_model=base_requirements,
        selected_aircraft_type=AircraftType.VTOL
    )
    
    updated_ctx = router.route(ctx)
    assert updated_ctx.selected_design_engine == "VTOLDesignEngine"
    
    # Execute design
    final_ctx = engine.execute_design(updated_ctx)
    assert final_ctx.current_status == DesignStatus.COMPLETED
    assert "vtol_aircraft_specification" in final_ctx.design_data
    
    spec = final_ctx.design_data["vtol_aircraft_specification"]
    assert spec.mtow_kg > 0.0
    assert spec.empty_weight_kg > 0.0
    assert spec.payload_weight_kg == 3.5
    assert spec.estimated_endurance_min > 0.0
    assert spec.estimated_range_km > 0.0
    
    # Verify subsystem outputs exist
    assert spec.mission is not None
    assert spec.configuration is not None
    assert spec.wing is not None
    assert spec.airfoil is not None
    assert spec.tail is not None
    assert spec.fuselage is not None
    assert spec.lift_system is not None
    assert spec.forward_propulsion is not None
    assert spec.electrical is not None
    assert spec.avionics is not None
    assert spec.payload is not None
    assert spec.mass_properties is not None
    assert spec.hover_performance is not None
    assert spec.transition is not None
    assert spec.cruise_performance is not None
    assert spec.verification is not None
    assert spec.cad is not None
    assert spec.manufacturing is not None
    assert spec.report is not None

    # Verify report exports wrote to directory
    assert os.path.exists("reports/vtol_specification.json")
    assert os.path.exists("reports/vtol_bom.csv")
    assert os.path.exists("reports/vtol_build_specification.txt")
    assert os.path.exists("reports/vtol_engineering_report.md")


def test_vtol_pipeline_invalid_requirements():
    """Verify pipeline detects invalid inputs and returns appropriate status."""
    pipeline = VTOLDesignPipeline()
    
    # Payload zero
    reqs = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.0,
        target_flight_time_min=30.0,
        target_range_km=45.0,
        cruise_speed_kmh=90.0
    )
    res = pipeline.execute(reqs)
    assert res.success is False
    assert res.status == PipelineStatus.INVALID_REQUIREMENTS
    assert len(res.errors) > 0


def test_vtol_pipeline_propulsion_infeasible(base_requirements):
    """Verify that LiftSystemValidationError maps to PROPULSION_INFEASIBLE."""
    pipeline = VTOLDesignPipeline()
    base_requirements.mission_type = MissionType.DELIVERY
    
    # Set extreme max_battery_c_rate constraint to force lift system sizing failure
    base_requirements.metadata["max_battery_c_rate"] = 0.01
    
    res = pipeline.execute(base_requirements)
    assert res.success is False
    assert res.status == PipelineStatus.PROPULSION_INFEASIBLE
    assert len(res.errors) > 0


def test_vtol_pipeline_battery_infeasible(base_requirements):
    """Verify that ElectricalValidationError maps to BATTERY_INFEASIBLE."""
    pipeline = VTOLDesignPipeline()
    base_requirements.mission_type = MissionType.SURVEY
    
    # Set extreme min_reserve_energy_fraction constraint to force electrical sizing failure
    base_requirements.metadata["min_reserve_energy_fraction"] = 9.0
    
    res = pipeline.execute(base_requirements)
    assert res.success is False
    assert res.status == PipelineStatus.BATTERY_INFEASIBLE
    assert len(res.errors) > 0
