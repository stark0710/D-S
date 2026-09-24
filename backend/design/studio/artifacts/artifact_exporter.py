"""
ArtifactExporter Subsystem

Purpose:
    Defines the `ArtifactExporter` class responsible for exporting engineering artifacts into serialized formats (JSON, YAML).

Role in Architecture:
    `ArtifactExporter` provides serialization mechanisms to convert immutable `EngineeringArtifact` objects into JSON or YAML strings.
"""

import json
from typing import Any
from backend.design.studio.artifacts.artifact import EngineeringArtifact


class ArtifactExporter:
    """
    Exporter for serializing EngineeringArtifact instances.

    Design Principles:
        - Single Responsibility Principle: Serialization into external formats (JSON, YAML) only.
    """

    def to_dict(self, artifact: EngineeringArtifact) -> dict[str, Any]:
        """Converts an EngineeringArtifact into a serializable dictionary."""
        return {
            "artifact_id": artifact.artifact_id,
            "name": artifact.name,
            "category": artifact.category.value,
            "version": str(artifact.version),
            "created_at": artifact.created_at,
            "author": artifact.author,
            "data": artifact.data,
            "metadata": {
                "project_name": artifact.metadata.project_name,
                "studio_name": artifact.metadata.studio_name,
                "stage_name": artifact.metadata.stage_name,
                "tags": list(artifact.metadata.tags),
                "extra": artifact.metadata.extra,
            },
        }

    def export_json(self, artifact: EngineeringArtifact, indent: int = 2) -> str:
        """
        Exports artifact as JSON string.

        Args:
            artifact (EngineeringArtifact): Target artifact object.
            indent (int): Indentation spaces.

        Returns:
            str: JSON string.
        """
        d = self.to_dict(artifact)
        return json.dumps(d, indent=indent, default=str)

    def export_yaml(self, artifact: EngineeringArtifact) -> str:
        """
        Exports artifact as YAML string representation.

        Args:
            artifact (EngineeringArtifact): Target artifact object.

        Returns:
            str: Simple YAML string.
        """
        d = self.to_dict(artifact)
        lines = []
        for key, val in d.items():
            if isinstance(val, dict):
                lines.append(f"{key}:")
                for k2, v2 in val.items():
                    lines.append(f"  {k2}: {v2}")
            else:
                lines.append(f"{key}: {val}")
        return "\n".join(lines)
