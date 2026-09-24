"""
Unit tests for Aircraft Design Studio Foundation.
"""

import pytest
from backend.design.common.requirements import MissionType, RequirementModel
from backend.design.common.context import (
    DesignStage,
    DesignStatus,
    ContextBuilder,
    DesignContext,
)
from backend.design.studio import (
    DesignSession,
    DesignArtifact,
    DesignResult,
    DesignStageManager,
    DesignWorkflow,
    DesignStudio,
    WorkflowExecutionError,
)


class MockDroneDesignStudio(DesignStudio):
    """Concrete mock studio implementing DesignStudio."""

    @property
    def studio_name(self) -> str:
        return "MockDroneDesignStudio"

    def execute_design(self, context: DesignContext) -> DesignResult:
        workflow = DesignWorkflow()

        def step_propulsion(ctx: DesignContext) -> tuple[DesignContext, list[DesignArtifact]]:
            ctx.design_data["motor"] = "T-Motor 2207"
            art = DesignArtifact(
                artifact_id="ART-1",
                name="Propulsion Sizing",
                artifact_type="MotorSelection",
                content={"motor": "T-Motor 2207"}
            )
            return ctx, [art]

        workflow.add_step(DesignStage.DRONE_DESIGN, step_propulsion)
        return workflow.execute_workflow(context)


def test_design_session_and_artifacts():
    """Verify DesignSession lifecycle and DesignArtifact model."""
    req = RequirementModel(
        mission_type=MissionType.AGRICULTURE,
        payload_weight_kg=2.0,
        target_flight_time_min=30.0,
        target_range_km=15.0,
        cruise_speed_kmh=50.0
    )
    context = ContextBuilder.create_context(req)

    session = DesignSession(session_id="SESS-001", design_context=context)

    assert session.session_id == "SESS-001"
    assert session.status == DesignStatus.CREATED

    initial_updated = session.updated_at
    session.touch()
    assert session.updated_at >= initial_updated

    artifact = DesignArtifact(
        artifact_id="ART-100",
        name="Wing Geometry",
        artifact_type="WingGeometry",
        content={"span_m": 2.5, "area_m2": 0.8}
    )
    assert artifact.name == "Wing Geometry"


def test_design_stage_manager():
    """Verify DesignStageManager tracks completions, skips, and failures."""
    mgr = DesignStageManager()

    mgr.advance_stage(DesignStage.MISSION_ANALYSIS)
    mgr.mark_completed(DesignStage.MISSION_ANALYSIS)

    mgr.mark_skipped(DesignStage.VEHICLE_RECOMMENDATION)
    mgr.mark_failed(DesignStage.DRONE_DESIGN)

    assert DesignStage.MISSION_ANALYSIS in mgr.completed_stages
    assert DesignStage.VEHICLE_RECOMMENDATION in mgr.skipped_stages
    assert DesignStage.DRONE_DESIGN in mgr.failed_stages


def test_design_workflow_successful_execution():
    """Verify DesignWorkflow executes steps sequentially, collecting artifacts and setting COMPLETED status."""
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=1.0,
        target_flight_time_min=20.0,
        target_range_km=10.0,
        cruise_speed_kmh=40.0
    )
    context = ContextBuilder.create_context(req)

    workflow = DesignWorkflow()

    def step1(ctx: DesignContext) -> tuple[DesignContext, list[DesignArtifact]]:
        ctx.design_data["step1_done"] = True
        art = DesignArtifact("A1", "Step1 Output", "Report", "Content1")
        return ctx, [art]

    def step2(ctx: DesignContext) -> tuple[DesignContext, list[DesignArtifact]]:
        ctx.design_data["step2_done"] = True
        art = DesignArtifact("A2", "Step2 Output", "Report", "Content2")
        return ctx, [art]

    workflow.add_step(DesignStage.MISSION_ANALYSIS, step1)
    workflow.add_step(DesignStage.DESIGN_ROUTING, step2)

    result = workflow.execute_workflow(context)

    assert result.success
    assert len(result.artifacts) == 2
    assert result.final_design_context.design_data["step1_done"]
    assert result.final_design_context.design_data["step2_done"]
    assert result.final_design_context.current_stage == DesignStage.COMPLETED


def test_design_workflow_failure_handling():
    """Verify DesignWorkflow handles step exception gracefully, capturing error message and setting FAILED status."""
    req = RequirementModel(
        mission_type=MissionType.DELIVERY,
        payload_weight_kg=5.0,
        target_flight_time_min=40.0,
        target_range_km=30.0,
        cruise_speed_kmh=60.0
    )
    context = ContextBuilder.create_context(req)

    workflow = DesignWorkflow()

    def failing_step(ctx: DesignContext) -> tuple[DesignContext, list[DesignArtifact]]:
        raise ValueError("Propulsion motor calculation failed due to invalid KV rating.")

    workflow.add_step(DesignStage.DRONE_DESIGN, failing_step)

    result = workflow.execute_workflow(context)

    assert not result.success
    assert len(result.errors) == 1
    assert "failed: Propulsion motor calculation failed" in result.errors[0]
    assert result.final_design_context.current_status == DesignStatus.FAILED


def test_mock_design_studio_execution():
    """Verify mock DesignStudio subclass executes design workflow and returns valid DesignResult."""
    req = RequirementModel(
        mission_type=MissionType.AGRICULTURE,
        payload_weight_kg=2.0,
        target_flight_time_min=30.0,
        target_range_km=15.0,
        cruise_speed_kmh=50.0
    )
    context = ContextBuilder.create_context(req)

    studio = MockDroneDesignStudio()
    assert studio.studio_name == "MockDroneDesignStudio"

    res = studio.execute_design(context)

    assert res.success
    assert len(res.artifacts) == 1
    assert res.final_design_context.design_data["motor"] == "T-Motor 2207"
