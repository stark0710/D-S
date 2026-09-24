"""
ContextSnapshot Subsystem

Purpose:
    Defines the `ContextSnapshot` domain model representing an immutable historical milestone record.

Role in Architecture:
    `ContextSnapshot` records the stage, status, timestamp, and summary description whenever a major design
    milestone is completed (e.g., Requirement Validation Complete, Mission Analysis Complete).
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from backend.design.common.context.design_stage import DesignStage
from backend.design.common.context.design_status import DesignStatus


def _current_timestamp() -> str:
    """Helper returning current UTC time in ISO 8601 string format."""
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class ContextSnapshot:
    """
    Immutable historical milestone record for a DesignContext.

    Attributes:
        stage (DesignStage): Design workflow stage at snapshot creation.
        status (DesignStatus): Design status at snapshot creation.
        timestamp (str): ISO 8601 creation timestamp string.
        summary (str): Brief summary description of milestone accomplishments.
    """

    stage: DesignStage
    status: DesignStatus
    summary: str
    timestamp: str = field(default_factory=_current_timestamp)
