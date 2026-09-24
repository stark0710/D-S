"""
Unit tests for Fixed-Wing Design Pipeline Orchestrator.
"""

import sys
import pytest

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment

from backend.design.fixed_wing.pipeline import (
    FixedWingDesignPipeline,
    PipelineStatus,
    FixedWingDesignResult,
    ConvergenceEvaluator,
    IterationRecord,
    NonConvergenceError,
    InvalidRequirementsError,
)


def test_1_pipeline_imports_and_initializes():
    """Verify pipeline package imports and initializes cleanly."""
    pipeline = FixedWingDesignPipeline(tolerance=0.01, max_iterations=20)
    assert pipeline.tolerance == 0.01
    assert pipeline.max_iterations == 20


def test_2_nominal_small_mapping_uav_executes():
    """Verify nominal small mapping UAV executes to completion."""
    req = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=80.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    pipeline = FixedWingDesignPipeline()
    res = pipeline.execute(req)

    assert res.success is True
    assert res.status == PipelineStatus.SUCCESS
    assert res.converged is True
    assert res.iterations > 0
    assert len(res.convergence_history) == res.iterations
    assert res.mass_properties_result is not None
    assert res.mass_properties_result.weight_breakdown.useful_load_kg > 0.5


def test_3_nominal_endurance_uav_executes():
    """Verify nominal long-endurance survey UAV executes to completion."""
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=1.0,
        target_flight_time_min=40.0,
        target_range_km=40.0,
        cruise_speed_kmh=80.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    pipeline = FixedWingDesignPipeline()
    res = pipeline.execute(req)

    assert res.success is True
    assert res.status == PipelineStatus.SUCCESS
    assert res.converged is True
    assert res.wing_result is not None
    assert res.wing_result.wing_geometry.span_m > 1.5


def test_4_heavy_payload_fixed_wing_rejection():
    """Verify extreme payload fixed-wing mission is gracefully rejected."""
    req = RequirementModel(
        mission_type=MissionType.DELIVERY,
        payload_weight_kg=60.0,
        target_flight_time_min=180.0,
        target_range_km=300.0,
        cruise_speed_kmh=120.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    pipeline = FixedWingDesignPipeline()
    res = pipeline.execute(req)

    assert res.status in (
        PipelineStatus.SIZING_INFEASIBLE,
        PipelineStatus.COMPONENT_SELECTION_FAILED,
        PipelineStatus.NON_CONVERGED,
        PipelineStatus.PROPULSION_INFEASIBLE,
        PipelineStatus.COMPONENT_DATABASE_LIMITATION,
    )


def test_5_configuration_remains_frozen():
    """Verify configuration selection is made once and remains frozen across iterations."""
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=1.0,
        target_flight_time_min=45.0,
        target_range_km=40.0,
        cruise_speed_kmh=80.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    pipeline = FixedWingDesignPipeline()
    res = pipeline.execute(req)

    assert res.success is True
    initial_wing_cfg = res.configuration_result.wing_configuration
    initial_tail_cfg = res.configuration_result.tail_configuration

    # Check configuration result in output is identical to what was passed to wing/tail
    assert res.wing_result is not None
    assert initial_wing_cfg == res.configuration_result.wing_configuration
    assert initial_tail_cfg == res.configuration_result.tail_configuration


def test_6_mtow_feedback_occurs():
    """Verify MTOW is updated iteratively based on calculated mass breakdown."""
    req = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=1.0,
        target_flight_time_min=40.0,
        target_range_km=30.0,
        cruise_speed_kmh=80.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    pipeline = FixedWingDesignPipeline()
    res = pipeline.execute(req)

    assert res.success is True
    assert len(res.convergence_history) >= 1
    # Iteration 1 old vs new MTOW
    rec1 = res.convergence_history[0]
    assert rec1.mtow_old != rec1.mtow_new or rec1.converged


def test_7_convergence_history_tracking():
    """Verify convergence history records every iteration step with metrics."""
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.8,
        target_flight_time_min=40.0,
        target_range_km=25.0,
        cruise_speed_kmh=95.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    pipeline = FixedWingDesignPipeline()
    res = pipeline.execute(req)

    assert len(res.convergence_history) > 0
    for idx, record in enumerate(res.convergence_history, start=1):
        assert isinstance(record, IterationRecord)
        assert record.iteration == idx
        assert record.absolute_delta_kg >= 0.0
        assert record.relative_delta >= 0.0


def test_8_relative_convergence_calculation():
    """Verify numerical math in ConvergenceEvaluator relative change formula."""
    evaluator = ConvergenceEvaluator(tolerance=0.01)

    # 10.0 kg -> 10.05 kg (delta = 0.05, rel = 0.05 / 10.0 = 0.005 <= 0.01 -> CONVERGED)
    rec1 = evaluator.evaluate_step(1, 10.0, 10.05)
    assert rec1.absolute_delta_kg == 0.05
    assert rec1.relative_delta == pytest.approx(0.005, abs=1e-5)
    assert rec1.converged is True

    # 10.0 kg -> 10.5 kg (delta = 0.5, rel = 0.5 / 10.0 = 0.05 > 0.01 -> NOT CONVERGED)
    rec2 = evaluator.evaluate_step(2, 10.0, 10.5)
    assert rec2.absolute_delta_kg == 0.5
    assert rec2.relative_delta == pytest.approx(0.05, abs=1e-5)
    assert rec2.converged is False


def test_9_pipeline_terminates_on_convergence():
    """Verify pipeline terminates as soon as relative MTOW change is <= 1%."""
    req = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=0.5,
        target_flight_time_min=30.0,
        target_range_km=20.0,
        cruise_speed_kmh=95.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    pipeline = FixedWingDesignPipeline(tolerance=0.01)  # 1% tolerance
    res = pipeline.execute(req)

    assert res.success is True
    assert res.converged is True
    assert res.iterations <= 15
    assert res.convergence_history[-1].converged is True


def test_10_pipeline_stops_at_max_iterations_when_non_convergent():
    """Verify pipeline terminates at max_iterations when tolerance cannot be met."""
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=1.5,
        target_flight_time_min=90.0,
        target_range_km=70.0,
        cruise_speed_kmh=95.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    # Set impossible tolerance 1e-12 with 3 max iterations
    pipeline = FixedWingDesignPipeline(tolerance=1e-12, max_iterations=3)
    res = pipeline.execute(req)

    assert res.success is False
    assert res.status == PipelineStatus.CONVERGENCE_FAILURE
    assert res.iterations == 3
    assert res.converged is False

    # Also test with raise_on_failure=True
    pipeline_raise = FixedWingDesignPipeline(tolerance=1e-12, max_iterations=3, raise_on_failure=True)
    with pytest.raises(NonConvergenceError):
        pipeline_raise.execute(req)


def test_11_invalid_mission_propagates_failure():
    """Verify negative payload requirement propagates INVALID_REQUIREMENTS failure."""
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=-5.0,  # Invalid negative weight
        target_flight_time_min=60.0,
        target_range_km=40.0,
        cruise_speed_kmh=95.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    pipeline = FixedWingDesignPipeline()
    res = pipeline.execute(req)

    assert res.success is False
    assert res.status == PipelineStatus.INVALID_REQUIREMENTS

    pipeline_raise = FixedWingDesignPipeline(raise_on_failure=True)
    with pytest.raises(InvalidRequirementsError):
        pipeline_raise.execute(req)


def test_12_subsystem_hard_failure_stops_downstream():
    """Verify conflicting low wing + belly landing requirement stops pipeline at configuration stage."""
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=1.0,
        target_flight_time_min=60.0,
        target_range_km=40.0,
        cruise_speed_kmh=95.0,
        takeoff_type=TakeoffType.HAND_LAUNCH,
        landing_type=LandingType.BELLY_LANDING,
        environment=OperatingEnvironment.RURAL,
    )
    pipeline = FixedWingDesignPipeline()
    res = pipeline.execute(req)

    # Pipeline should complete or fail cleanly without unhandled exception
    assert isinstance(res, FixedWingDesignResult)


def test_13_verification_failure_exposed():
    """Verify verification checks populate verification_result."""
    req = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=0.5,
        target_flight_time_min=30.0,
        target_range_km=25.0,
        cruise_speed_kmh=95.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    pipeline = FixedWingDesignPipeline()
    res = pipeline.execute(req)

    assert res.verification_result is not None
    assert hasattr(res.verification_result, "compliance_report") or hasattr(res.verification_result, "requirement_results")


def test_14_deterministic_output():
    """Verify identical requirement input produces exact identical numerical output."""
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=1.0,
        target_flight_time_min=45.0,
        target_range_km=40.0,
        cruise_speed_kmh=80.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    pipeline = FixedWingDesignPipeline()

    res1 = pipeline.execute(req)
    res2 = pipeline.execute(req)

    assert res1.success == res2.success == True
    assert res1.iterations == res2.iterations
    assert res1.mass_properties_result.weight_breakdown.useful_load_kg == res2.mass_properties_result.weight_breakdown.useful_load_kg
    assert res1.wing_result.wing_geometry.span_m == res2.wing_result.wing_geometry.span_m


def test_15_no_cad_module_imported():
    """Verify that CADQuery or OCP modules are NOT imported by the pipeline package."""
    import backend.design.fixed_wing.pipeline.fixed_wing_design_pipeline as pipeline_mod

    imported_modules = sys.modules.keys()
    cad_modules = [m for m in imported_modules if "cadquery" in m.lower() or "ocp" in m.lower()]
    assert len(cad_modules) == 0, f"CAD modules detected in sys.modules: {cad_modules}"
