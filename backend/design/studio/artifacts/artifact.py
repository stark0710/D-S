"""
EngineeringArtifact Subsystem

Purpose:
    Defines the `EngineeringArtifact` domain model representing an immutable engineering output produced during aircraft design.

Role in Architecture:
    `EngineeringArtifact` provides the canonical immutable representation of engineering outputs (Motor Selection, Wing Geometry,
    CAD Models, Reports) created during Torq Wings aircraft design workflows.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from backend.design.studio.artifacts.artifact_category import ArtifactCategory
from backend.design.studio.artifacts.artifact_version import ArtifactVersion
from backend.design.studio.artifacts.artifact_metadata import ArtifactMetadata


def _current_timestamp() -> str:
    """Helper returning current UTC ISO 8601 timestamp string."""
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True, frozen=True)
class EngineeringArtifact:
    """
    Immutable engineering artifact record.

    Attributes:
        artifact_id (str): Unique artifact identifier string.
        name (str): Human-readable artifact name (e.g. 'Propulsion System Specification').
        category (ArtifactCategory): Artifact Category classification.
        version (ArtifactVersion): Version model (Major, Minor, Patch).
        created_at (str): ISO 8601 creation timestamp string.
        author (str): Creating author or service identifier.
        data (dict[str, Any]): Data payload content dictionary.
        metadata (ArtifactMetadata): Associated artifact metadata.
    """

    artifact_id: str
    name: str
    category: ArtifactCategory
    version: ArtifactVersion = field(default_factory=ArtifactVersion)
    created_at: str = field(default_factory=_current_timestamp)
    author: str = "Torq Wings Platform"
    data: dict[str, Any] = field(default_factory=dict)
    metadata: ArtifactMetadata = field(default_factory=ArtifactMetadata)
