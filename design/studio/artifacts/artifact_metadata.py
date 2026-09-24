"""
ArtifactMetadata Subsystem

Purpose:
    Defines the `ArtifactMetadata` domain model representing metadata attached to engineering artifacts.

Role in Architecture:
    `ArtifactMetadata` captures project name, design studio name, workflow stage name, tags tuple, and additional properties.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class ArtifactMetadata:
    """
    Metadata model for engineering artifacts.

    Attributes:
        project_name (str): Associated project name string.
        studio_name (str): Creating design studio name (e.g. 'DroneDesignStudio').
        stage_name (str): Creating workflow stage name.
        tags (tuple[str, ...]): Tuple of search/filter tags.
        extra (dict[str, Any]): Additional diagnostic metadata dictionary.
    """

    project_name: str = "Torq Wings Design Studio"
    studio_name: str = ""
    stage_name: str = ""
    tags: tuple[str, ...] = ()
    extra: dict[str, Any] = field(default_factory=dict)
