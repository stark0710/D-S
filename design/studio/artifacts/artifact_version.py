"""
ArtifactVersion Subsystem

Purpose:
    Defines the `ArtifactVersion` domain model representing semantic versioning for engineering artifacts.

Role in Architecture:
    `ArtifactVersion` enforces version tracking (Major, Minor, Patch) and version compatibility checking across artifacts.
"""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ArtifactVersion:
    """
    Semantic versioning model for engineering artifacts.

    Attributes:
        major (int): Major version number (breaking structural schema changes).
        minor (int): Minor version number (backward-compatible feature additions).
        patch (int): Patch version number (backward-compatible bug fixes).
    """

    major: int = 1
    minor: int = 0
    patch: int = 0

    def __str__(self) -> str:
        """Returns string representation 'vMajor.Minor.Patch'."""
        return f"v{self.major}.{self.minor}.{self.patch}"

    def is_compatible_with(self, other: "ArtifactVersion") -> bool:
        """
        Checks version compatibility. Major versions must match.

        Args:
            other (ArtifactVersion): Target version to compare against.

        Returns:
            bool: True if major version matches; False otherwise.
        """
        return self.major == other.major
