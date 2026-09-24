"""
SessionCheckpoint Subsystem

Purpose:
    Defines the `SessionCheckpoint` domain model representing an explicit checkpoint record.

Role in Architecture:
    `SessionCheckpoint` encapsulates checkpoint ID, session ID, ISO 8601 creation timestamp,
    checkpoint classification ('AUTOMATIC', 'MANUAL'), underlying `SessionSnapshot`, notes, and metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from backend.design.studio.persistence.session_snapshot import SessionSnapshot


def _current_timestamp() -> str:
    """Helper returning current UTC ISO 8601 timestamp string."""
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class SessionCheckpoint:
    """
    Checkpoint record for a design session.

    Attributes:
        checkpoint_id (str): Unique checkpoint identifier string.
        session_id (str): Associated session identifier.
        snapshot (SessionSnapshot): Underlying point-in-time snapshot.
        created_at (str): ISO 8601 timestamp string.
        checkpoint_type (str): Classification type ('AUTOMATIC', 'MANUAL').
        notes (str): Human-readable explanatory notes.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    checkpoint_id: str
    session_id: str
    snapshot: SessionSnapshot
    created_at: str = field(default_factory=_current_timestamp)
    checkpoint_type: str = "MANUAL"
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
