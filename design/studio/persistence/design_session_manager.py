"""
DesignSessionManager Subsystem

Purpose:
    Defines the `DesignSessionManager` class, which serves as the public entry point for managing design session lifecycles.

Role in Architecture:
    `DesignSessionManager` implements the Manager Pattern to handle session creation, opening, closing, resuming,
    archiving, deletion, checkpointing, and session recovery.
"""

from uuid import uuid4
from datetime import datetime, timezone
from typing import Any
from backend.design.common.context.design_context import DesignContext
from backend.design.common.context.design_status import DesignStatus
from backend.design.studio.design_session import DesignSession
from backend.design.studio.artifacts.artifact import EngineeringArtifact
from backend.design.studio.persistence.session_snapshot import SessionSnapshot
from backend.design.studio.persistence.session_checkpoint import SessionCheckpoint
from backend.design.studio.persistence.design_session_repository import DesignSessionRepository
from backend.design.studio.persistence.session_recovery import SessionRecovery


class DesignSessionManager:
    """
    Public manager service for design session lifecycles and checkpoints.

    Design Principles:
        - Manager Pattern: Centralized management of session creation, checkpoints, and recovery.
        - Dependency Injection: Injects `DesignSessionRepository` and `SessionRecovery` collaborators.
    """

    def __init__(
        self,
        repository: DesignSessionRepository | None = None,
        recovery: SessionRecovery | None = None
    ) -> None:
        """
        Initializes the DesignSessionManager.

        Args:
            repository (DesignSessionRepository | None): Injected repository instance.
            recovery (SessionRecovery | None): Injected recovery instance.
        """
        self._repository: DesignSessionRepository = repository if repository else DesignSessionRepository()
        self._recovery: SessionRecovery = recovery if recovery else SessionRecovery()

    def create_session(self, session_id: str, context: DesignContext) -> DesignSession:
        """
        Creates and stores a new DesignSession.

        Args:
            session_id (str): Unique session identifier string.
            context (DesignContext): Initial design context state.

        Returns:
            DesignSession: Created active design session instance.
        """
        session = DesignSession(session_id=session_id, design_context=context, status=DesignStatus.CREATED)
        self._repository.save_session(session)
        return session

    def open_session(self, session_id: str) -> DesignSession:
        """Opens and returns an existing DesignSession."""
        session = self._repository.get_session(session_id)
        session.status = DesignStatus.IN_PROGRESS
        session.touch()
        self._repository.save_session(session)
        return session

    def close_session(self, session_id: str) -> None:
        """Closes an active DesignSession."""
        session = self._repository.get_session(session_id)
        session.status = DesignStatus.COMPLETED
        session.touch()
        self._repository.save_session(session)

    def resume_session(self, session_id: str) -> DesignSession:
        """Resumes an interrupted or active DesignSession."""
        return self.open_session(session_id)

    def archive_session(self, session_id: str) -> None:
        """Archives a DesignSession."""
        session = self._repository.get_session(session_id)
        session.status = DesignStatus.COMPLETED
        session.metadata["archived"] = True
        session.touch()
        self._repository.save_session(session)

    def delete_session(self, session_id: str) -> None:
        """Deletes a session and its checkpoints from the repository."""
        self._repository.delete_session(session_id)

    def create_checkpoint(
        self,
        session_id: str,
        checkpoint_type: str = "MANUAL",
        notes: str = "",
        artifacts: list[EngineeringArtifact] | None = None
    ) -> SessionCheckpoint:
        """
        Creates a checkpoint snapshot for a design session.

        Args:
            session_id (str): Target session ID.
            checkpoint_type (str): Checkpoint type ('AUTOMATIC', 'MANUAL').
            notes (str): Human-readable notes.
            artifacts (list[EngineeringArtifact] | None): Optional artifacts list to capture in snapshot.

        Returns:
            SessionCheckpoint: Created checkpoint object.
        """
        session = self._repository.get_session(session_id)
        chk_id = f"CHK-{uuid4().hex[:8].upper()}"
        snap_id = f"SNP-{uuid4().hex[:8].upper()}"
        created_at = datetime.now(timezone.utc).isoformat()

        snapshot = SessionSnapshot(
            snapshot_id=snap_id,
            session_id=session_id,
            created_at=created_at,
            design_context=session.design_context,
            engineering_artifacts=list(artifacts) if artifacts else []
        )

        checkpoint = SessionCheckpoint(
            checkpoint_id=chk_id,
            session_id=session_id,
            snapshot=snapshot,
            created_at=created_at,
            checkpoint_type=checkpoint_type,
            notes=notes
        )

        self._repository.save_checkpoint(checkpoint)
        return checkpoint

    def restore_checkpoint(self, session_id: str, checkpoint_id: str) -> DesignSession:
        """
        Restores a session from a specific checkpoint.

        Args:
            session_id (str): Target session ID.
            checkpoint_id (str): Target checkpoint ID.

        Returns:
            DesignSession: Restored active session instance.
        """
        checkpoint = self._repository.get_checkpoint(session_id, checkpoint_id)
        restored_session = self._recovery.recover_session(session_id, checkpoint)
        self._repository.save_session(restored_session)
        return restored_session
