"""
ArtifactValidator Subsystem

Purpose:
    Defines the `ArtifactValidator` class responsible for validating engineering artifact schemas, required fields, and version compatibility.

Role in Architecture:
    `ArtifactValidator` enforces structural validation rules before artifacts are saved or exported.
"""

from backend.design.studio.artifacts.artifact import EngineeringArtifact


class ArtifactValidationError(ValueError):
    """Raised when artifact validation checks fail."""
    pass


class ArtifactValidator:
    """
    Validator for EngineeringArtifact instances.

    Design Principles:
        - Single Responsibility Principle: Artifact structure, field, and version validation only.
    """

    def validate(self, artifact: EngineeringArtifact) -> bool:
        """
        Validates artifact structure, required fields, and metadata.

        Args:
            artifact (EngineeringArtifact): Target artifact object.

        Returns:
            bool: True if valid.

        Raises:
            ArtifactValidationError: If validation checks fail.
        """
        if not artifact.artifact_id or not artifact.artifact_id.strip():
            raise ArtifactValidationError("EngineeringArtifact artifact_id must not be empty.")

        if not artifact.name or not artifact.name.strip():
            raise ArtifactValidationError("EngineeringArtifact name must not be empty.")

        if not artifact.category:
            raise ArtifactValidationError("EngineeringArtifact category must be specified.")

        if artifact.version is None:
            raise ArtifactValidationError("EngineeringArtifact version must not be None.")

        if artifact.data is None:
            raise ArtifactValidationError("EngineeringArtifact data payload must not be None.")

        return True
