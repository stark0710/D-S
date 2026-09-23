"""
Unit tests for Universal Design Persistence and Session Recovery Framework.
"""

import pytest
import json
from backend.design.common.requirements import MissionType, RequirementModel
from backend.design.common.context import ContextBuilder
from backend.design.common.context.design_status import DesignStatus
from backend.design.studio.artifacts import ArtifactCategory, ArtifactFactory
from backend.design.studio.persistence import (
    SessionSnapshot,
    SessionCheckpoint,
    SessionHistory,
    SessionSerializer,
    SessionValidator,
    SessionValidationError,
    DesignSessionRepository,
    SessionRecovery,
    SessionExporter,
    SessionImporter,
    SessionImportError,
    DesignSessionManager,
)


def test_session_serializer_and_validator():
    """Verify SessionSerializer and SessionValidator roundtrip serialization and validation."""
    req = RequirementModel(
        mission_type=MissionType.AGRICULTURE,
        payload_weight_kg=2.0,
        target_flight_time_min=30.0,
        target_range_km=15.0,
        cruise_speed_kmh=50.0
    )
    context = ContextBuilder.create_context(req)
    context.design_data["motor"] = "T-Motor MN501S"

    art_factory = ArtifactFactory()
    artifact = art_factory.create_artifact("Propulsion Spec", ArtifactCategory.MOTOR_SELECTION, {"kv": 300})

    snapshot = SessionSnapshot(
        snapshot_id="SNP-001",
        session_id="SESS-100",
        design_context=context,
        engineering_artifacts=[artifact]
    )

    checkpoint = SessionCheckpoint(
        checkpoint_id="CHK-001",
        session_id="SESS-100",
        snapshot=snapshot,
        notes="Pre-optimization checkpoint"
    )

    validator = SessionValidator()
    assert validator.validate_checkpoint(checkpoint)

    serializer = SessionSerializer()
    serialized = serializer.serialize_checkpoint(checkpoint)

    deserialized_chk = serializer.deserialize_checkpoint(serialized)

    assert deserialized_chk.checkpoint_id == "CHK-001"
    assert deserialized_chk.session_id == "SESS-100"
    assert deserialized_chk.snapshot.design_context.design_data["motor"] == "T-Motor MN501S"
    assert len(deserialized_chk.snapshot.engineering_artifacts) == 1


def test_session_exporter_and_importer():
    """Verify SessionExporter and SessionImporter JSON package export and import."""
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=1.0,
        target_flight_time_min=20.0,
        target_range_km=10.0,
        cruise_speed_kmh=40.0
    )
    context = ContextBuilder.create_context(req)

    snapshot = SessionSnapshot("SNP-002", "SESS-200", context)
    checkpoint = SessionCheckpoint("CHK-002", "SESS-200", snapshot, notes="Test Checkpoint")

    exporter = SessionExporter()
    json_str = exporter.export_session_json(checkpoint)

    importer = SessionImporter()
    imported_chk = importer.import_session_json(json_str)

    assert imported_chk.checkpoint_id == "CHK-002"
    assert imported_chk.session_id == "SESS-200"


def test_design_session_manager_and_recovery():
    """Verify DesignSessionManager full lifecycle: create, checkpoint, restore, archive."""
    req = RequirementModel(
        mission_type=MissionType.DELIVERY,
        payload_weight_kg=3.0,
        target_flight_time_min=35.0,
        target_range_km=25.0,
        cruise_speed_kmh=60.0
    )
    context = ContextBuilder.create_context(req)

    manager = DesignSessionManager()

    # 1. Create Session
    session = manager.create_session("SESS-300", context)
    assert session.session_id == "SESS-300"
    assert session.status == DesignStatus.CREATED

    # 2. Update context and create checkpoint
    session.design_context.design_data["status"] = "Propulsion Sized"
    checkpoint = manager.create_checkpoint("SESS-300", notes="Propulsion Complete")
    assert checkpoint.checkpoint_id.startswith("CHK-")

    # 3. Simulate interruption and restore checkpoint
    restored_session = manager.restore_checkpoint("SESS-300", checkpoint.checkpoint_id)
    assert restored_session.session_id == "SESS-300"
    assert restored_session.status == DesignStatus.IN_PROGRESS
    assert restored_session.design_context.design_data["status"] == "Propulsion Sized"

    # 4. Archive and Delete Session
    manager.archive_session("SESS-300")
    assert manager._repository.get_session("SESS-300").metadata.get("archived") is True

    manager.delete_session("SESS-300")
    with pytest.raises(Exception):
        manager._repository.get_session("SESS-300")
