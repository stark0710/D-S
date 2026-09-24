"""
SessionHistory Subsystem

Purpose:
    Defines the `SessionHistory` domain model representing full version and checkpoint evolution history for a session.

Role in Architecture:
    `SessionHistory` aggregates chronological checkpoints and snapshots for a design session.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.studio.persistence.session_snapshot import SessionSnapshot
from backend.design.studio.persistence.session_checkpoint import SessionCheckpoint


@dataclass(slots=True)
class SessionHistory:
    """
    Session evolution and checkpoint history.

    Attributes:
        session_id (str): Associated session identifier.
        checkpoints (list[SessionCheckpoint]): Chronological list of session checkpoints.
        snapshots (list[SessionSnapshot]): Chronological list of snapshots.
        metadata (dict[str, Any]): Additional history diagnostic metadata.
    """

    session_id: str
    checkpoints: list[SessionCheckpoint] = field(default_factory=list)
    snapshots: list[SessionSnapshot] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_checkpoint(self, checkpoint: SessionCheckpoint) -> None:
        """Appends a new checkpoint to history."""
        self.checkpoints.append(checkpoint)

    def add_snapshot(self, snapshot: SessionSnapshot) -> None:
        """Appends a new snapshot to history."""
        self.snapshots.append(snapshot)
