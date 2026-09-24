"""
SessionSerializer Subsystem

Purpose:
    Defines the `SessionSerializer` class responsible for serializing and deserializing session snapshots and checkpoints.

Role in Architecture:
    `SessionSerializer` provides dictionary and JSON conversion for `SessionSnapshot` and `SessionCheckpoint` instances.
"""

import json
from typing import Any
from backend.design.common.requirements import RequirementModel, MissionType, OptimizationPriority
from backend.design.common.context import ContextBuilder, DesignContext, DesignStage, DesignStatus
from backend.design.studio.artifacts import EngineeringArtifact, ArtifactCategory, ArtifactVersion, ArtifactMetadata
from backend.design.studio.persistence.session_snapshot import SessionSnapshot
from backend.design.studio.persistence.session_checkpoint import SessionCheckpoint


class SessionSerializer:
    """
    Serializer for session snapshots and checkpoints.

    Design Principles:
        - Single Responsibility Principle: Serialization and deserialization only.
    """

    def serialize_snapshot(self, snapshot: SessionSnapshot) -> dict[str, Any]:
        """Serializes SessionSnapshot into a dictionary."""
        ctx = snapshot.design_context
        req = ctx.requirement_model

        artifacts_data = [
            {
                "artifact_id": a.artifact_id,
                "name": a.name,
                "category": a.category.value,
                "version": str(a.version),
                "created_at": a.created_at,
                "author": a.author,
                "data": a.data,
            }
            for a in snapshot.engineering_artifacts
        ]

        return {
            "snapshot_id": snapshot.snapshot_id,
            "session_id": snapshot.session_id,
            "created_at": snapshot.created_at,
            "design_context": {
                "requirement_model": {
                    "mission_type": req.mission_type.value,
                    "payload_weight_kg": req.payload_weight_kg,
                    "target_flight_time_min": req.target_flight_time_min,
                    "target_range_km": req.target_range_km,
                    "cruise_speed_kmh": req.cruise_speed_kmh,
                    "budget": req.budget,
                    "optimization_priority": req.optimization_priority.value,
                },
                "current_stage": ctx.current_stage.value,
                "current_status": ctx.current_status.value,
                "design_data": ctx.design_data,
            },
            "engineering_artifacts": artifacts_data,
            "metadata": snapshot.metadata,
        }

    def deserialize_snapshot(self, data: dict[str, Any]) -> SessionSnapshot:
        """Deserializes a dictionary into a SessionSnapshot."""
        ctx_data = data["design_context"]
        req_data = ctx_data["requirement_model"]

        req = RequirementModel(
            mission_type=MissionType(req_data["mission_type"]),
            payload_weight_kg=float(req_data["payload_weight_kg"]),
            target_flight_time_min=float(req_data["target_flight_time_min"]),
            target_range_km=float(req_data["target_range_km"]),
            cruise_speed_kmh=float(req_data["cruise_speed_kmh"]),
            budget=float(req_data["budget"]) if req_data.get("budget") is not None else None,
            optimization_priority=OptimizationPriority(req_data.get("optimization_priority", "BALANCED"))
        )

        ctx = ContextBuilder.create_context(req)
        ctx.update_stage(DesignStage(ctx_data["current_stage"]), DesignStatus(ctx_data["current_status"]))
        ctx.design_data = ctx_data.get("design_data", {})

        artifacts: list[EngineeringArtifact] = []
        for a_dict in data.get("engineering_artifacts", []):
            art = EngineeringArtifact(
                artifact_id=a_dict["artifact_id"],
                name=a_dict["name"],
                category=ArtifactCategory(a_dict["category"]),
                version=ArtifactVersion(1, 0, 0),
                created_at=a_dict.get("created_at", ""),
                author=a_dict.get("author", "Torq Wings Platform"),
                data=a_dict.get("data", {}),
                metadata=ArtifactMetadata()
            )
            artifacts.append(art)

        return SessionSnapshot(
            snapshot_id=data["snapshot_id"],
            session_id=data["session_id"],
            created_at=data["created_at"],
            design_context=ctx,
            engineering_artifacts=artifacts,
            metadata=data.get("metadata", {})
        )

    def serialize_checkpoint(self, checkpoint: SessionCheckpoint) -> dict[str, Any]:
        """Serializes SessionCheckpoint into a dictionary."""
        return {
            "checkpoint_id": checkpoint.checkpoint_id,
            "session_id": checkpoint.session_id,
            "created_at": checkpoint.created_at,
            "checkpoint_type": checkpoint.checkpoint_type,
            "notes": checkpoint.notes,
            "snapshot": self.serialize_snapshot(checkpoint.snapshot),
            "metadata": checkpoint.metadata,
        }

    def deserialize_checkpoint(self, data: dict[str, Any]) -> SessionCheckpoint:
        """Deserializes a dictionary into a SessionCheckpoint."""
        snapshot = self.deserialize_snapshot(data["snapshot"])
        return SessionCheckpoint(
            checkpoint_id=data["checkpoint_id"],
            session_id=data["session_id"],
            snapshot=snapshot,
            created_at=data["created_at"],
            checkpoint_type=data.get("checkpoint_type", "MANUAL"),
            notes=data.get("notes", ""),
            metadata=data.get("metadata", {})
        )
