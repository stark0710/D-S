"""
SessionImporter Subsystem

Purpose:
    Defines the `SessionImporter` class responsible for importing session packages and restoring `SessionCheckpoint` objects.

Role in Architecture:
    `SessionImporter` parses session packages (JSON string or package dictionary) and deserializes them back into `SessionCheckpoint` instances.
"""

import json
from typing import Any
from backend.design.studio.persistence.session_checkpoint import SessionCheckpoint
from backend.design.studio.persistence.session_serializer import SessionSerializer
from backend.design.studio.persistence.session_validator import SessionValidator


class SessionImportError(ValueError):
    """Raised when importing a session package fails."""
    pass


class SessionImporter:
    """
    Importer for session packages.

    Design Principles:
        - Single Responsibility Principle: Package parsing and session checkpoint restoration.
    """

    def __init__(
        self,
        serializer: SessionSerializer | None = None,
        validator: SessionValidator | None = None
    ) -> None:
        """Initializes SessionImporter."""
        self._serializer: SessionSerializer = serializer if serializer else SessionSerializer()
        self._validator: SessionValidator = validator if validator else SessionValidator()

    def import_session_package(self, package: dict[str, Any]) -> SessionCheckpoint:
        """
        Imports a session package dictionary and restores SessionCheckpoint.

        Args:
            package (dict[str, Any]): Package data dictionary.

        Returns:
            SessionCheckpoint: Restored checkpoint.
        """
        if package.get("format") != "TorqWingsSessionPackage":
            raise SessionImportError("Invalid session package format. Expected 'TorqWingsSessionPackage'.")

        checkpoint_data = package.get("checkpoint")
        if not checkpoint_data:
            raise SessionImportError("Session package missing 'checkpoint' data.")

        checkpoint = self._serializer.deserialize_checkpoint(checkpoint_data)
        self._validator.validate_checkpoint(checkpoint)

        return checkpoint

    def import_session_json(self, json_str: str) -> SessionCheckpoint:
        """
        Imports a JSON string session package and restores SessionCheckpoint.

        Args:
            json_str (str): JSON string content.

        Returns:
            SessionCheckpoint: Restored checkpoint.
        """
        try:
            pkg = json.loads(json_str)
        except Exception as exc:
            raise SessionImportError(f"Failed to parse session JSON string: {str(exc)}") from exc

        return self.import_session_package(pkg)
