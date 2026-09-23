"""
ArtifactRegistry Subsystem

Purpose:
    Defines the `ArtifactRegistry` class responsible for registering and managing engineering artifact types and handlers.

Role in Architecture:
    `ArtifactRegistry` provides the plugin registry for engineering artifact category registration and lookup.
"""

from backend.design.studio.artifacts.artifact_category import ArtifactCategory


class ArtifactRegistry:
    """
    Registry for managing engineering artifact categories and handlers.

    Design Principles:
        - Registry Pattern: Centralized registration and lookup.
        - Open/Closed Principle: Extensible plugin architecture for custom artifact classifications.
    """

    def __init__(self) -> None:
        """Initializes the ArtifactRegistry with default categories."""
        self._categories: dict[ArtifactCategory, str] = {
            cat: f"Standard engineering artifact classification for {cat.value}"
            for cat in ArtifactCategory
        }

    def register_category(self, category: ArtifactCategory, description: str) -> None:
        """Registers or updates description for an ArtifactCategory."""
        self._categories[category] = description

    def get_category_info(self, category: ArtifactCategory) -> str:
        """Retrieves description for a registered ArtifactCategory."""
        if category not in self._categories:
            raise KeyError(f"ArtifactCategory '{category.value}' is not registered.")
        return self._categories[category]

    def registered_categories(self) -> list[ArtifactCategory]:
        """Returns a list of all registered ArtifactCategory values."""
        return list(self._categories.keys())
