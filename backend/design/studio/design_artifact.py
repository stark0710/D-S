"""
DesignArtifact Subsystem

Purpose:
    Defines the `DesignArtifact` domain model representing outputs generated during aircraft design studio execution.

Role in Architecture:
    `DesignArtifact` encapsulates structured design outputs (Wing Geometry, Motor Selection, Battery Selection,
    Performance Analysis, CAD Model, Engineering Report) created during design workflows.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _current_timestamp() -> str:
    """Helper returning current UTC ISO 8601 timestamp string."""
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class DesignArtifact:
    """
    Design studio output artifact.

    Attributes:
        artifact_id (str): Unique artifact identifier.
        name (str): Human-readable artifact name (e.g. 'Wing Geometry Specification').
        artifact_type (str): Classification type string ('WingGeometry', 'MotorSelection', 'BatterySelection', 'CADModel', 'EngineeringReport').
        content (Any): Content payload (dictionary, markdown string, binary data, or JSON object).
        created_at (str): ISO 8601 creation timestamp string.
        metadata (dict[str, Any]): Additional artifact diagnostic metadata.
    """

    artifact_id: str
    name: str
    artifact_type: str
    content: Any
    created_at: str = field(default_factory=_current_timestamp)
    metadata: dict[str, Any] = field(default_factory=dict)
