"""
DesignSession Subsystem

Purpose:
    Defines the `DesignSession` domain model representing an active aircraft design session.

Role in Architecture:
    `DesignSession` tracks session ID, current `DesignContext`, ISO 8601 creation/updated timestamps, status, and metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from backend.design.common.context.design_context import DesignContext
from backend.design.common.context.design_status import DesignStatus


def _current_timestamp() -> str:
    """Helper returning current UTC ISO 8601 timestamp string."""
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class DesignSession:
    """
    Active aircraft design session model.

    Attributes:
        session_id (str): Unique user session identifier.
        design_context (DesignContext): In-memory DesignContext state.
        created_at (str): ISO 8601 creation timestamp string.
        updated_at (str): ISO 8601 last-modified timestamp string.
        status (DesignStatus): Current design status (CREATED, IN_PROGRESS, COMPLETED, FAILED).
        metadata (dict[str, Any]): Additional session metadata.
    """

    session_id: str
    design_context: DesignContext
    created_at: str = field(default_factory=_current_timestamp)
    updated_at: str = field(default_factory=_current_timestamp)
    status: DesignStatus = DesignStatus.CREATED
    metadata: dict[str, Any] = field(default_factory=dict)

    def touch(self) -> None:
        """Updates last modified timestamp to current UTC time."""
        self.updated_at = datetime.now(timezone.utc).isoformat()
