"""
SessionSnapshot Subsystem

Purpose:
    Defines the `SessionSnapshot` domain model representing a point-in-time state capture of a design session.

Role in Architecture:
    `SessionSnapshot` encapsulates snapshot ID, session ID, ISO 8601 timestamp, `DesignContext`,
    list of `EngineeringArtifact` objects, and diagnostic metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from backend.design.common.context.design_context import DesignContext
from backend.design.studio.artifacts.artifact import EngineeringArtifact


def _current_timestamp() -> str:
    """Helper returning current UTC ISO 8601 timestamp string."""
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class SessionSnapshot:
    """
    Point-in-time snapshot of an active design session.

    Attributes:
        snapshot_id (str): Unique snapshot identifier.
        session_id (str): Associated session identifier string.
        created_at (str): ISO 8601 timestamp string.
        design_context (DesignContext): Captured DesignContext state.
        engineering_artifacts (list[EngineeringArtifact]): Captured engineering artifacts list.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    snapshot_id: str
    session_id: str
    design_context: DesignContext
    created_at: str = field(default_factory=_current_timestamp)
    engineering_artifacts: list[EngineeringArtifact] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
