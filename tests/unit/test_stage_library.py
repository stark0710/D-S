"""
Unit tests for Universal Aircraft Design Stage Library.
"""

import pytest
from backend.design.common.requirements import MissionType, RequirementModel
from backend.design.common.context import ContextBuilder, DesignContext
from backend.design.studio.stages import (
    StageCategory,
    StageContext,
    StageResult,
    DesignStage,
    StageValidator,
    StageValidationError,
    StageRegistry,
    StageFactory,
    DuplicateStageRegistrationError,
)


class MockStageA(DesignStage):
    """Mock stage A with no dependencies."""

    @property
    def stage_name(self) -> str:
        return "StageA"

    @property
    def category(self) -> StageCategory:
        return StageCategory.MISSION_ANALYSIS

    @property
    def required_inputs(self) -> list[str]:
        return []

    @property
    def required_dependencies(self) -> list[str]:
        return []

    def execute(self, stage_context: StageContext) -> tuple[DesignContext, StageResult]:
        ctx = stage_context.design_context
        ctx.design_data["stage_a_done"] = True
        res = StageResult(stage_name=self.stage_name, success=True, outputs={"done": True})
        return ctx, res


class MockStageB(DesignStage):
    """Mock stage B requiring StageA as a dependency."""

    @property
    def stage_name(self) -> str:
        return "StageB"

    @property
    def category(self) -> StageCategory:
        return StageCategory.COMPONENT_SELECTION

    @property
    def required_inputs(self) -> list[str]:
        return ["stage_a_done"]

    @property
    def required_dependencies(self) -> list[str]:
        return ["StageA"]

    def execute(self, stage_context: StageContext) -> tuple[DesignContext, StageResult]:
        ctx = stage_context.design_context
        ctx.design_data["stage_b_done"] = True
        res = StageResult(stage_name=self.stage_name, success=True, outputs={"done": True})
        return ctx, res


class MockCircularStage1(DesignStage):
    """Mock circular stage 1 requiring Stage 2."""

    @property
    def stage_name(self) -> str:
        return "Circ1"

    @property
    def category(self) -> StageCategory:
        return StageCategory.CONFIGURATION

    @property
    def required_inputs(self) -> list[str]:
        return []

    @property
    def required_dependencies(self) -> list[str]:
        return ["Circ2"]

    def execute(self, stage_context: StageContext) -> tuple[DesignContext, StageResult]:
        return stage_context.design_context, StageResult("Circ1", True)


class MockCircularStage2(DesignStage):
    """Mock circular stage 2 requiring Stage 1."""

    @property
    def stage_name(self) -> str:
        return "Circ2"

    @property
    def category(self) -> StageCategory:
        return StageCategory.CONFIGURATION

    @property
    def required_inputs(self) -> list[str]:
        return []

    @property
    def required_dependencies(self) -> list[str]:
        return ["Circ1"]

    def execute(self, stage_context: StageContext) -> tuple[DesignContext, StageResult]:
        return stage_context.design_context, StageResult("Circ2", True)


def test_stage_registry_and_factory():
    """Verify StageRegistry registers stage classes and StageFactory creates instances."""
    registry = StageRegistry()
    registry.register_stage(MockStageA)
    registry.register_stage(MockStageB)

    assert len(registry.registered_stages()) == 2

    factory = StageFactory(registry=registry)
    stage_a = factory.create_stage("StageA")

    assert isinstance(stage_a, MockStageA)
    assert stage_a.stage_name == "StageA"
    assert stage_a.category == StageCategory.MISSION_ANALYSIS


def test_duplicate_stage_registration_raises_error():
    """Verify DuplicateStageRegistrationError is raised when registering duplicate stage name."""
    registry = StageRegistry()
    registry.register_stage(MockStageA)

    with pytest.raises(DuplicateStageRegistrationError):
        registry.register_stage(MockStageA)


def test_stage_validator_valid_sequence():
    """Verify StageValidator validates correct stage ordering."""
    validator = StageValidator()
    stages = [MockStageA(), MockStageB()]

    assert validator.validate_stage_sequence(stages)


def test_stage_validator_invalid_sequence_order():
    """Verify StageValidator raises StageValidationError when dependencies are out of order."""
    validator = StageValidator()

    # StageB before StageA
    stages_bad = [MockStageB(), MockStageA()]

    with pytest.raises(StageValidationError):
        validator.validate_stage_sequence(stages_bad)


def test_stage_validator_circular_dependency():
    """Verify StageValidator detects circular dependencies and raises StageValidationError."""
    validator = StageValidator()
    circ_stages = [MockCircularStage1(), MockCircularStage2()]

    with pytest.raises(StageValidationError):
        validator.validate_stage_sequence(circ_stages)


def test_stage_execution():
    """Verify DesignStage execution updates context and produces StageResult."""
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=1.0,
        target_flight_time_min=20.0,
        target_range_km=10.0,
        cruise_speed_kmh=40.0
    )
    context = ContextBuilder.create_context(req)

    stage_ctx = StageContext(design_context=context, current_stage="StageA")
    stage_a = MockStageA()

    updated_ctx, res = stage_a.execute(stage_ctx)

    assert res.success
    assert updated_ctx.design_data["stage_a_done"]
    assert res.outputs["done"]
