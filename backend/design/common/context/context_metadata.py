"""
ContextMetadata Subsystem

Purpose:
    Defines the `ContextMetadata` domain model representing administrative metadata attached to a `DesignContext`.

Role in Architecture:
    `ContextMetadata` tracks timestamps, session IDs, version information, and operational notes for design auditing.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone


def _current_timestamp() -> str:
    """Helper returning current UTC time in ISO 8601 string format."""
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class ContextMetadata:
    """
    Administrative metadata for a DesignContext instance.

    Attributes:
        created_at (str): ISO 8601 creation timestamp string.
        updated_at (str): ISO 8601 last-modified timestamp string.
        session_id (str): Unique user session identifier.
        version (str): System design context schema version string.
        notes (str): Optional operational or debugging notes.
    """

    created_at: str = field(default_factory=_current_timestamp)
    updated_at: str = field(default_factory=_current_timestamp)
    session_id: str = ""
    version: str = "1.0.0"
    notes: str = ""
