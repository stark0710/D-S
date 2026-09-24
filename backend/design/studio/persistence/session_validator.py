"""
SessionValidator Subsystem

Purpose:
    Defines the `SessionValidator` class responsible for validating session snapshot and checkpoint data integrity.

Role in Architecture:
    `SessionValidator` enforces structural validation rules before snapshots or checkpoints are persisted or recovered.
"""

from backend.design.studio.persistence.session_snapshot import SessionSnapshot
from backend.design.studio.persistence.session_checkpoint import SessionCheckpoint


class SessionValidationError(ValueError):
    """Raised when session data validation checks fail."""
    pass


class SessionValidator:
    """
    Validator for SessionSnapshot and SessionCheckpoint instances.

    Design Principles:
        - Single Responsibility Principle: Session integrity, context non-nullness, and checkpoint structure validation.
    """

    def validate_snapshot(self, snapshot: SessionSnapshot) -> bool:
        """
        Validates SessionSnapshot integrity.

        Args:
            snapshot (SessionSnapshot): Target snapshot.

        Returns:
            bool: True if valid.

        Raises:
            SessionValidationError: If validation checks fail.
        """
        if not snapshot.snapshot_id or not snapshot.snapshot_id.strip():
            raise SessionValidationError("SessionSnapshot snapshot_id must not be empty.")

        if not snapshot.session_id or not snapshot.session_id.strip():
            raise SessionValidationError("SessionSnapshot session_id must not be empty.")

        if snapshot.design_context is None:
            raise SessionValidationError("SessionSnapshot design_context must not be None.")

        return True

    def validate_checkpoint(self, checkpoint: SessionCheckpoint) -> bool:
        """
        Validates SessionCheckpoint integrity.

        Args:
            checkpoint (SessionCheckpoint): Target checkpoint.

        Returns:
            bool: True if valid.

        Raises:
            SessionValidationError: If validation checks fail.
        """
        if not checkpoint.checkpoint_id or not checkpoint.checkpoint_id.strip():
            raise SessionValidationError("SessionCheckpoint checkpoint_id must not be empty.")

        if not checkpoint.session_id or not checkpoint.session_id.strip():
            raise SessionValidationError("SessionCheckpoint session_id must not be empty.")

        if checkpoint.snapshot is None:
            raise SessionValidationError("SessionCheckpoint snapshot must not be None.")

        return self.validate_snapshot(checkpoint.snapshot)
