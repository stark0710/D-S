"""
SessionExporter Subsystem

Purpose:
    Defines the `SessionExporter` class responsible for exporting design sessions into JSON format or ZIP package representations.

Role in Architecture:
    `SessionExporter` converts `SessionCheckpoint` objects into serializable JSON or package dictionaries.
"""

import json
from typing import Any
from backend.design.studio.persistence.session_checkpoint import SessionCheckpoint
from backend.design.studio.persistence.session_serializer import SessionSerializer


class SessionExporter:
    """
    Exporter for design session checkpoints.

    Design Principles:
        - Single Responsibility Principle: Serialization into JSON strings or export packages.
    """

    def __init__(self, serializer: SessionSerializer | None = None) -> None:
        """Initializes SessionExporter."""
        self._serializer: SessionSerializer = serializer if serializer else SessionSerializer()

    def export_session_package(self, checkpoint: SessionCheckpoint) -> dict[str, Any]:
        """Exports a SessionCheckpoint into a session package dictionary."""
        checkpoint_data = self._serializer.serialize_checkpoint(checkpoint)
        return {
            "format": "TorqWingsSessionPackage",
            "version": "1.0.0",
            "checkpoint": checkpoint_data,
        }

    def export_session_json(self, checkpoint: SessionCheckpoint, indent: int = 2) -> str:
        """Exports a SessionCheckpoint into a formatted JSON string."""
        pkg = self.export_session_package(checkpoint)
        return json.dumps(pkg, indent=indent, default=str)
