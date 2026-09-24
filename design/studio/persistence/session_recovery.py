"""
SessionRecovery Subsystem

Purpose:
    Defines the `SessionRecovery` class responsible for recovering interrupted design sessions from checkpoints.

Role in Architecture:
    `SessionRecovery` validates checkpoint integrity, restores `DesignContext` and `EngineeringArtifact` collections,
    and returns a restored `DesignSession`.
"""

from backend.design.common.context.design_status import DesignStatus
from backend.design.studio.design_session import DesignSession
from backend.design.studio.persistence.session_checkpoint import SessionCheckpoint
from backend.design.studio.persistence.session_validator import SessionValidator


class SessionRecovery:
    """
    Recovery manager for restoring interrupted design sessions.

    Design Principles:
        - Single Responsibility Principle: Interrupted session recovery and data restoration only.
    """

    def __init__(self, validator: SessionValidator | None = None) -> None:
        """Initializes SessionRecovery."""
        self._validator: SessionValidator = validator if validator else SessionValidator()

    def recover_session(
        self,
        session_id: str,
        checkpoint: SessionCheckpoint
    ) -> DesignSession:
        """
        Recovers a design session from a checkpoint.

        Args:
            session_id (str): Target session ID.
            checkpoint (SessionCheckpoint): Checkpoint snapshot to restore from.

        Returns:
            DesignSession: Restored active design session instance.
        """
        self._validator.validate_checkpoint(checkpoint)

        restored_context = checkpoint.snapshot.design_context
        restored_context.metadata.notes = f"Recovered session from checkpoint '{checkpoint.checkpoint_id}'."

        session = DesignSession(
            session_id=session_id,
            design_context=restored_context,
            status=DesignStatus.IN_PROGRESS,
            metadata={
                "recovered_from_checkpoint_id": checkpoint.checkpoint_id,
                "recovered_at": checkpoint.created_at,
                "artifact_count": len(checkpoint.snapshot.engineering_artifacts),
            }
        )

        return session
