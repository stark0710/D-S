"""
ComponentRepository Subsystem

Purpose:
    Defines the `ComponentRepository` class implementing the Repository Pattern for component lookup.

Role in Architecture:
    `ComponentRepository` acts as the data access layer for component databases.
    It provides category queries and attribute filtering without containing engineering or sizing logic.
"""

from collections import defaultdict
from typing import Any
from backend.design.components.component_category import ComponentCategory


class ComponentRepository:
    """
    Repository for querying hardware component databases.

    Design Principles:
        - Repository Pattern: Hides underlying database implementation details.
        - Single Responsibility Principle: Data retrieval and filtering only.
    """

    def __init__(
        self,
        database: dict[ComponentCategory, list[dict[str, Any]]] | None = None
    ) -> None:
        """
        Initializes the ComponentRepository.

        Args:
            database (dict[ComponentCategory, list[dict[str, Any]]] | None): Optional initial component database dictionary.
        """
        self._db: dict[ComponentCategory, list[dict[str, Any]]] = defaultdict(list)
        if database:
            for cat, items in database.items():
                self._db[cat].extend(items)

    def register_component(self, category: ComponentCategory, component_data: dict[str, Any]) -> None:
        """
        Registers a new component record into the repository.

        Args:
            category (ComponentCategory): Target component category.
            component_data (dict[str, Any]): Component attribute dictionary.
        """
        self._db[category].append(component_data)

    def get_components_by_category(
        self,
        category: ComponentCategory,
        filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Retrieves all components for the specified category matching optional filter criteria.

        Args:
            category (ComponentCategory): Target component category.
            filters (dict[str, Any] | None): Optional key-value filter dictionary.

        Returns:
            list[dict[str, Any]]: List of matching component attribute dictionaries.
        """
        raw_items = self._db.get(category, [])
        if not filters:
            return list(raw_items)

        matching_items: list[dict[str, Any]] = []
        for item in raw_items:
            matches = True
            for k, v in filters.items():
                if item.get(k) != v:
                    matches = False
                    break
            if matches:
                matching_items.append(item)

        return matching_items

    def count(self, category: ComponentCategory | None = None) -> int:
        """Returns total component count, optionally filtered by category."""
        if category:
            return len(self._db.get(category, []))
        return sum(len(items) for items in self._db.values())
