"""
Unit tests for Design Context Framework.
"""

import pytest
from backend.design.common.requirements import MissionType, RequirementModel
from backend.design.common.context import (
    DesignStage,
    DesignStatus,
    ContextMetadata,
    ContextSnapshot,
    DesignContext,
    ContextBuilder,
)


def test_design_context_enums():
    """Verify DesignStage and DesignStatus enum values."""
    assert DesignStage.REQUIREMENT_COLLECTION == "REQUIREMENT_COLLECTION"
    assert DesignStage.MISSION_ANALYSIS == "MISSION_ANALYSIS"
    assert DesignStage.DRONE_DESIGN == "DRONE_DESIGN"
    assert DesignStatus.CREATED == "CREATED"
    assert DesignStatus.IN_PROGRESS == "IN_PROGRESS"
    assert DesignStatus.COMPLETED == "COMPLETED"


def test_context_builder_and_context_creation():
    """Verify ContextBuilder builds valid DesignContext with initial snapshot and metadata."""
    req = RequirementModel(
        mission_type=MissionType.AGRICULTURE,
        payload_weight_kg=2.5,
        target_flight_time_min=45.0,
        target_range_km=40.0,
        cruise_speed_kmh=60.0
    )

    context = ContextBuilder.create_context(req, session_id="SESS-1234", notes="Test session")

    assert isinstance(context, DesignContext)
    assert context.requirement_model == req
    assert context.current_stage == DesignStage.REQUIREMENT_COLLECTION
    assert context.current_status == DesignStatus.CREATED
    assert context.metadata.session_id == "SESS-1234"
    assert context.metadata.notes == "Test session"
    assert len(context.snapshots) == 1
    assert context.snapshots[0].stage == DesignStage.REQUIREMENT_COLLECTION
    assert context.snapshots[0].summary == "DesignContext initialized from RequirementModel."


def test_context_stage_transitions_and_snapshots():
    """Verify stage transitions, status updates, and snapshot history tracking."""
    req = RequirementModel(
        mission_type=MissionType.DELIVERY,
        payload_weight_kg=5.0,
        target_flight_time_min=30.0,
        target_range_km=25.0,
        cruise_speed_kmh=80.0
    )

    context = ContextBuilder.create_context(req)
    initial_updated_at = context.metadata.updated_at

    # Transition to Requirement Validation stage
    context.update_stage(
        stage=DesignStage.REQUIREMENT_VALIDATION,
        status=DesignStatus.IN_PROGRESS,
        snapshot_summary="Validation initiated."
    )

    assert context.current_stage == DesignStage.REQUIREMENT_VALIDATION
    assert context.current_status == DesignStatus.IN_PROGRESS
    assert len(context.snapshots) == 2
    assert context.snapshots[1].stage == DesignStage.REQUIREMENT_VALIDATION
    assert context.snapshots[1].summary == "Validation initiated."

    # Manual snapshot addition
    context.add_snapshot("Custom milestone reached.")
    assert len(context.snapshots) == 3
    assert context.snapshots[2].summary == "Custom milestone reached."


def test_design_context_slots():
    """Verify @dataclass(slots=True) prevents dynamic arbitrary field assignments."""
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=1.0,
        target_flight_time_min=20.0,
        target_range_km=10.0,
        cruise_speed_kmh=50.0
    )
    context = ContextBuilder.create_context(req)

    with pytest.raises(AttributeError):
        context.arbitrary_field = "invalid"  # type: ignore
