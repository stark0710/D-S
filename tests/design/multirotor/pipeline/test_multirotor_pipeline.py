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

from backend.design.multirotor.pipeline.multirotor_design_pipeline import MultirotorDesignPipeline, MultirotorDesignEngine
from backend.design.multirotor.pipeline.pipeline_result import PipelineStatus


@pytest.fixture
def base_requirements():
    return RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=1.2,
        target_flight_time_min=25.0,
        target_range_km=15.0,
        cruise_speed_kmh=45.0,
        environment=OperatingEnvironment.RURAL,
        metadata={
            "payload_dimensions_m": (0.12, 0.10, 0.08),
            "redundancy_required": False,
            "maximum_frame_size_m": 0.8
        }
    )


def test_pipeline_construction_and_registration():
    """Verify that MultirotorDesignEngine implements DesignEngine and registers properly."""
    registry = DesignEngineRegistry()
    engine = MultirotorDesignEngine()
    
    assert engine.engine_id == "MultirotorDesignEngine"
    assert AircraftType.QUADCOPTER in engine.supported_aircraft_types
    assert AircraftType.HEXACOPTER in engine.supported_aircraft_types
    assert AircraftType.OCTOCOPTER in engine.supported_aircraft_types
    
    registry.register_engine(engine)
    assert registry.get_engine_by_id("MultirotorDesignEngine") == engine
    assert registry.get_engine_by_aircraft_type(AircraftType.QUADCOPTER) == engine


def test_design_routing_and_execution(base_requirements):
    """Verify that DesignEngineRouter correctly dispatches and runs multirotor design."""
    registry = DesignEngineRegistry()
    engine = MultirotorDesignEngine()
    registry.register_engine(engine)
    
    router = DesignEngineRouter(registry=registry)
    ctx = DesignContext(
        requirement_model=base_requirements,
        selected_aircraft_type=AircraftType.QUADCOPTER
    )
    
    updated_ctx = router.route(ctx)
    assert updated_ctx.selected_design_engine == "MultirotorDesignEngine"
    
    # Execute design
    final_ctx = engine.execute_design(updated_ctx)
    assert final_ctx.current_status == DesignStatus.COMPLETED
    assert "multirotor_aircraft_specification" in final_ctx.design_data
    
    spec = final_ctx.design_data["multirotor_aircraft_specification"]
    assert spec.mtow_kg > 0.0
    assert spec.empty_weight_kg > 0.0
    assert spec.layout_class == "Quadcopter X"


def test_end_to_end_synthesis_flow(base_requirements):
    """Verify the entire sequential sizing, convergence, verification, and output package pipeline."""
    pipeline = MultirotorDesignPipeline()
    res = pipeline.execute(base_requirements)
    
    assert res.success is True
    assert res.status == PipelineStatus.SUCCESS
    assert res.iterations >= 1
    assert res.converged is True
    
    spec = res.final_specification
    assert spec is not None
    
    # Verify sizer specifications are consolidated
    assert spec.mission_strategy is not None
    assert spec.frame is not None
    assert spec.propulsion_assembly is not None
    assert spec.electrical is not None
    assert spec.layout_spec is not None
    assert spec.mass_properties is not None
    assert spec.performance is not None
    assert spec.verification is not None
    
    # Verify catalog frame selected
    assert spec.frame.approach_type == "Catalog Selection"
    
    # Verify compatibility mappings exist in propulsion assembly
    assert spec.propulsion_assembly.motor.weight_kg > 0.0
    assert spec.propulsion_assembly.propeller.diameter_m > 0.0
    assert spec.propulsion_assembly.esc.continuous_current_a > 0.0
    assert spec.propulsion_assembly.battery.capacity_mah > 0.0
    
    # Verify electrical sizer outputs
    assert spec.electrical.power_distribution is not None
    assert "Main Battery Wire" in spec.electrical.wire_gauge_summary
    
    # Verify layout sizer outputs
    assert isinstance(spec.layout_spec.payload_mount, str)
    
    # Verify performance result
    assert spec.performance.flight_time_min > 0.0
    assert spec.performance.range_km > 0.0
    
    # Verify BOM populated
    assert len(spec.bom_data) > 0
    categories = [item["Category"] for item in spec.bom_data]
    assert "Frame" in categories
    assert "Motor" in categories
    assert "Propeller" in categories
    assert "ESC" in categories
    assert "Battery" in categories
    assert "Flight Controller" in categories
    
    # Verify build instructions generated
    assert "POWER HARNESS CONNECTIONS" in spec.build_instructions
    assert "CONTROL SIGNAL CONNECTIONS" in spec.build_instructions
    
    # Verify report exports wrote to directory
    assert os.path.exists("reports/multirotor_specification.json")
    assert os.path.exists("reports/multirotor_bom.csv")
    assert os.path.exists("reports/multirotor_build_specification.txt")
    assert os.path.exists("reports/multirotor_engineering_report.md")


def test_deterministic_execution(base_requirements):
    """Verify that multiple synthesis runs return exactly identical specs for same input."""
    pipeline = MultirotorDesignPipeline()
    res1 = pipeline.execute(base_requirements)
    res2 = pipeline.execute(base_requirements)
    
    assert res1.success is True
    assert res2.success is True
    
    spec1 = res1.final_specification
    spec2 = res2.final_specification
    
    assert spec1.mass_properties.total_mass_kg == spec2.mass_properties.total_mass_kg
    assert spec1.propulsion_assembly.motor.model == spec2.propulsion_assembly.motor.model
    assert spec1.propulsion_assembly.battery.model == spec2.propulsion_assembly.battery.model
    assert spec1.performance.flight_time_min == spec2.performance.flight_time_min


def test_invalid_requirements():
    """Verify that invalid requirements return a failure status code."""
    bad_req = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=-1.0,  # invalid
        target_flight_time_min=0.0,  # invalid
        target_range_km=15.0,
        cruise_speed_kmh=45.0,
        environment=OperatingEnvironment.RURAL
    )
    pipeline = MultirotorDesignPipeline()
    res = pipeline.execute(bad_req)
    
    assert res.success is False
    assert res.status == PipelineStatus.INVALID_REQUIREMENTS
    assert len(res.errors) > 0
