"""
ArtifactRepository Subsystem

Purpose:
    Defines the `ArtifactRepository` class responsible for storing, retrieving, and querying `EngineeringArtifact` instances.

Role in Architecture:
    `ArtifactRepository` implements the Repository Pattern for engineering artifacts.
    It provides lookup by ID, category filtering, custom query evaluation, and version tracking.
"""

from typing import Callable
from backend.design.studio.artifacts.artifact import EngineeringArtifact
from backend.design.studio.artifacts.artifact_category import ArtifactCategory


class ArtifactNotFoundError(KeyError):
    """Raised when looking up an artifact ID that is absent from the repository."""
    pass


class ArtifactRepository:
    """
    In-memory repository for storing and querying EngineeringArtifact instances.

    Design Principles:
        - Repository Pattern: Encapsulates artifact storage and query mechanics.
    """

    def __init__(self) -> None:
        """Initializes the ArtifactRepository."""
        self._store: dict[str, EngineeringArtifact] = {}

    def save_artifact(self, artifact: EngineeringArtifact) -> None:
        """
        Stores an EngineeringArtifact in the repository.

        Args:
            artifact (EngineeringArtifact): Immutable artifact object.
        """
        self._store[artifact.artifact_id] = artifact

    def get_artifact(self, artifact_id: str) -> EngineeringArtifact:
        """
        Retrieves an artifact by ID.

        Args:
            artifact_id (str): Unique artifact identifier.

        Returns:
            EngineeringArtifact: Stored artifact instance.

        Raises:
            ArtifactNotFoundError: If artifact_id is not present.
        """
        if artifact_id not in self._store:
            raise ArtifactNotFoundError(f"EngineeringArtifact with ID '{artifact_id}' not found in repository.")
        return self._store[artifact_id]

    def list_artifacts(self, category: ArtifactCategory | None = None) -> list[EngineeringArtifact]:
        """
        Lists stored artifacts, optionally filtered by category.

        Args:
            category (ArtifactCategory | None): Optional category filter.

        Returns:
            list[EngineeringArtifact]: List of matching stored artifacts.
        """
        if category is None:
            return list(self._store.values())
        return [a for a in self._store.values() if a.category == category]

    def query_artifacts(
        self,
        filter_fn: Callable[[EngineeringArtifact], bool]
    ) -> list[EngineeringArtifact]:
        """
        Queries stored artifacts matching a custom predicate function.

        Args:
            filter_fn (Callable): Predicate function returning True for matching artifacts.

        Returns:
            list[EngineeringArtifact]: Matching stored artifacts list.
        """
        return [a for a in self._store.values() if filter_fn(a)]
