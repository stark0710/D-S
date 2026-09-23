"""
ArtifactFactory Subsystem

Purpose:
    Defines the `ArtifactFactory` class responsible for creating immutable `EngineeringArtifact` instances.

Role in Architecture:
    `ArtifactFactory` implements the Factory Pattern for engineering artifact creation, automatically assigning unique identifiers,
    capturing ISO 8601 timestamps, attaching metadata, and building immutable `EngineeringArtifact` objects.
"""

from uuid import uuid4
from datetime import datetime, timezone
from typing import Any
from backend.design.studio.artifacts.artifact import EngineeringArtifact
from backend.design.studio.artifacts.artifact_category import ArtifactCategory
from backend.design.studio.artifacts.artifact_version import ArtifactVersion
from backend.design.studio.artifacts.artifact_metadata import ArtifactMetadata


class ArtifactFactory:
    """
    Factory for creating immutable EngineeringArtifact instances.

    Design Principles:
        - Factory Pattern: Encapsulates artifact creation logic.
        - Immutability: Ensures created artifacts are frozen and immutable.
    """

    def create_artifact(
        self,
        name: str,
        category: ArtifactCategory,
        data: dict[str, Any],
        author: str = "Torq Wings Platform",
        version: ArtifactVersion | None = None,
        metadata: ArtifactMetadata | None = None,
        artifact_id: str | None = None
    ) -> EngineeringArtifact:
        """
        Creates an immutable EngineeringArtifact instance.

        Args:
            name (str): Human-readable artifact name.
            category (ArtifactCategory): Category classification.
            data (dict[str, Any]): Data payload content dictionary.
            author (str): Author or service name.
            version (ArtifactVersion | None): Optional version override.
            metadata (ArtifactMetadata | None): Optional metadata override.
            artifact_id (str | None): Optional explicit artifact ID.

        Returns:
            EngineeringArtifact: Created immutable engineering artifact object.
        """
        art_id = artifact_id if artifact_id else f"ART-{uuid4().hex[:8].upper()}"
        ver = version if version else ArtifactVersion(1, 0, 0)
        meta = metadata if metadata else ArtifactMetadata()
        created_at = datetime.now(timezone.utc).isoformat()

        return EngineeringArtifact(
            artifact_id=art_id,
            name=name,
            category=category,
            version=ver,
            created_at=created_at,
            author=author,
            data=data,
            metadata=meta
        )
