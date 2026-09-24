"""
Unit tests for Universal Aircraft Design Workflow Engine.
"""

import pytest
from backend.design.common.requirements import MissionType, RequirementModel
from backend.design.common.context import ContextBuilder, DesignContext
from backend.design.studio.workflow import (
    WorkflowStage,
    WorkflowStageResult,
    WorkflowExecutor,
    WorkflowRegistry,
    WorkflowPipeline,
    WorkflowEngine,
    StageExecutionError,
    StageNotFoundError,
    RetryableWorkflowError,
)


class MockPropulsionStage(WorkflowStage):
    """Mock propulsion stage."""

    @property
    def stage_name(self) -> str:
        return "PropulsionSizingStage"

    def execute(self, context: DesignContext) -> tuple[DesignContext, WorkflowStageResult]:
        context.design_data["motor"] = "T-Motor MN501S"
        res = WorkflowStageResult(
            stage_name=self.stage_name,
            success=True,
            artifacts=["PropulsionSpecification"]
        )
        return context, res


class MockFrameStage(WorkflowStage):
    """Mock frame stage."""

    @property
    def stage_name(self) -> str:
        return "FrameSizingStage"

    def execute(self, context: DesignContext) -> tuple[DesignContext, WorkflowStageResult]:
        context.design_data["frame"] = "Carbon Fiber Hexa 650"
        res = WorkflowStageResult(
            stage_name=self.stage_name,
            success=True,
            artifacts=["FrameCADSpec"]
        )
        return context, res


class MockRetryableStage(WorkflowStage):
    """Mock stage throwing RetryableWorkflowError on first attempt."""

    def __init__(self) -> None:
        self.attempts = 0

    @property
    def stage_name(self) -> str:
        return "RetryableStage"

    def execute(self, context: DesignContext) -> tuple[DesignContext, WorkflowStageResult]:
        self.attempts += 1
        if self.attempts == 1:
            raise RetryableWorkflowError("Transient database timeout.")
        res = WorkflowStageResult(stage_name=self.stage_name, success=True)
        return context, res


def test_workflow_registry():
    """Verify WorkflowRegistry stage registration and resolution."""
    registry = WorkflowRegistry()
    p_stage = MockPropulsionStage()
    f_stage = MockFrameStage()

    registry.register_stage(p_stage)
    registry.register_stage(f_stage)

    assert len(registry.registered_stages()) == 2
    assert registry.get_stage("PropulsionSizingStage") == p_stage

    with pytest.raises(StageNotFoundError):
        registry.get_stage("MissingStage")


def test_workflow_executor_retry():
    """Verify WorkflowExecutor retries RetryableWorkflowError up to max_retries."""
    executor = WorkflowExecutor()
    r_stage = MockRetryableStage()

    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=1.0,
        target_flight_time_min=20.0,
        target_range_km=10.0,
        cruise_speed_kmh=40.0
    )
    context = ContextBuilder.create_context(req)

    updated_ctx, res = executor.execute_stage(r_stage, context, max_retries=1)

    assert res.success
    assert r_stage.attempts == 2


def test_workflow_engine_execution():
    """Verify WorkflowEngine executes stages sequentially, updating DesignContext."""
    req = RequirementModel(
        mission_type=MissionType.AGRICULTURE,
        payload_weight_kg=3.0,
        target_flight_time_min=45.0,
        target_range_km=25.0,
        cruise_speed_kmh=60.0
    )
    context = ContextBuilder.create_context(req)

    p_stage = MockPropulsionStage()
    f_stage = MockFrameStage()

    pipeline = WorkflowPipeline(stages=[p_stage, f_stage])
    engine = WorkflowEngine(pipeline=pipeline)

    updated_context, results = engine.run_workflow(context)

    assert len(results) == 2
    assert results[0].success
    assert results[1].success
    assert updated_context.design_data["motor"] == "T-Motor MN501S"
    assert updated_context.design_data["frame"] == "Carbon Fiber Hexa 650"
