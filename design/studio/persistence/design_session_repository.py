"""
DesignSessionRepository Subsystem

Purpose:
    Defines the `DesignSessionRepository` class responsible for storing and retrieving design sessions, checkpoints, and history.

Role in Architecture:
    `DesignSessionRepository` implements the Repository Pattern for design sessions.
    It encapsulates storage mechanics for active design sessions and version checkpoints.
"""

from backend.design.studio.design_session import DesignSession
from backend.design.studio.persistence.session_checkpoint import SessionCheckpoint
from backend.design.studio.persistence.session_history import SessionHistory
from backend.design.studio.design_exception import SessionNotFoundError


class DesignSessionRepository:
    """
    In-memory repository for active design sessions and checkpoints.

    Design Principles:
        - Repository Pattern: Encapsulates session storage and query operations.
    """

    def __init__(self) -> None:
        """Initializes the DesignSessionRepository."""
        self._sessions: dict[str, DesignSession] = {}
        self._checkpoints: dict[str, dict[str, SessionCheckpoint]] = {}
        self._histories: dict[str, SessionHistory] = {}

    def save_session(self, session: DesignSession) -> None:
        """Stores a DesignSession."""
        self._sessions[session.session_id] = session
        if session.session_id not in self._checkpoints:
            self._checkpoints[session.session_id] = {}
        if session.session_id not in self._histories:
            self._histories[session.session_id] = SessionHistory(session_id=session.session_id)

    def get_session(self, session_id: str) -> DesignSession:
        """Retrieves a DesignSession by session_id."""
        if session_id not in self._sessions:
            raise SessionNotFoundError(f"DesignSession '{session_id}' not found in repository.")
        return self._sessions[session_id]

    def save_checkpoint(self, checkpoint: SessionCheckpoint) -> None:
        """Stores a SessionCheckpoint."""
        s_id = checkpoint.session_id
        if s_id not in self._checkpoints:
            self._checkpoints[s_id] = {}
        self._checkpoints[s_id][checkpoint.checkpoint_id] = checkpoint

        if s_id in self._histories:
            self._histories[s_id].add_checkpoint(checkpoint)

    def get_checkpoint(self, session_id: str, checkpoint_id: str) -> SessionCheckpoint:
        """Retrieves a SessionCheckpoint by session_id and checkpoint_id."""
        if session_id not in self._checkpoints or checkpoint_id not in self._checkpoints[session_id]:
            raise KeyError(f"SessionCheckpoint '{checkpoint_id}' for session '{session_id}' not found.")
        return self._checkpoints[session_id][checkpoint_id]

    def list_checkpoints(self, session_id: str) -> list[SessionCheckpoint]:
        """Lists all checkpoints for session_id."""
        if session_id not in self._checkpoints:
            return []
        return list(self._checkpoints[session_id].values())

    def get_history(self, session_id: str) -> SessionHistory:
        """Retrieves SessionHistory for session_id."""
        if session_id not in self._histories:
            return SessionHistory(session_id=session_id)
        return self._histories[session_id]

    def delete_session(self, session_id: str) -> None:
        """Deletes a session and its checkpoints from the repository."""
        self._sessions.pop(session_id, None)
        self._checkpoints.pop(session_id, None)
        self._histories.pop(session_id, None)
