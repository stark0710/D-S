"""
KnowledgeRepository Subsystem

Purpose:
    Defines the `KnowledgeRepository` class, which serves as the canonical in-memory storage,
    indexing, and lookup engine for all loaded `KnowledgeEntity` objects.

Role in Architecture:
    `KnowledgeRepository` acts as the single source of truth for engineering knowledge models
    loaded by the `KnowledgeEngine`. Future subsystems (Knowledge Graph, Query Engine, Rule Engine,
    Aircraft Design Engine, AI Assistant) query `KnowledgeRepository` to retrieve entities by ID or type.
"""

from typing import Type, TypeVar
from backend.models.knowledge_entity import KnowledgeEntity

T = TypeVar("T", bound=KnowledgeEntity)


class KnowledgeRepositoryError(ValueError):
    """Base exception class for KnowledgeRepository operations."""
    pass


class DuplicateEntityIDError(KnowledgeRepositoryError):
    """Raised when multiple entities with the same ID are added to the repository."""
    pass


class EntityNotFoundError(KnowledgeRepositoryError, KeyError):
    """Raised when looking up an entity ID that does not exist in the repository."""
    pass


class KnowledgeRepository:
    """
    In-memory canonical storage layer and index for KnowledgeEntity objects.

    Maintains internal indexes for $O(1)$ lookup by entity ID and type classification.

    Responsibilities:
        - Maintain an immutable catalog of instantiated `KnowledgeEntity` objects.
        - Enforce unique entity ID constraints upon initialization.
        - Provide $O(1)$ entity lookup by string ID.
        - Provide type-filtered entity lookups.
        - Expose repository metrics and stored entity types.

    Limitations:
        - In-Memory Storage: Does not persist entity state to external databases or disk.
        - Unresolved Edges: Does not construct graph edges or resolve foreign references.
    """

    def __init__(self, entities: list[KnowledgeEntity] | None = None) -> None:
        """
        Initializes the KnowledgeRepository and populates internal indexes.

        Args:
            entities (list[KnowledgeEntity] | None): Initial list of loaded engineering entities.

        Raises:
            DuplicateEntityIDError: If duplicate entity IDs are detected.
        """
        self._entities: list[KnowledgeEntity] = list(entities) if entities else []
        self._by_id: dict[str, KnowledgeEntity] = {}
        self._by_type: dict[type, list[KnowledgeEntity]] = {}

        self._build_indexes()

    def _build_indexes(self) -> None:
        """Populates ID and type lookup dictionaries while detecting duplicate IDs."""
        self._by_id.clear()
        self._by_type.clear()

        for entity in self._entities:
            # Enforce unique ID constraint
            if entity.id in self._by_id:
                existing = self._by_id[entity.id]
                raise DuplicateEntityIDError(
                    f"Duplicate entity ID detected: '{entity.id}' is shared by '{existing.name}' and '{entity.name}'."
                )

            self._by_id[entity.id] = entity

            # Index by exact class type and parent types
            entity_cls = type(entity)
            if entity_cls not in self._by_type:
                self._by_type[entity_cls] = []
            self._by_type[entity_cls].append(entity)

    def get_all(self) -> list[KnowledgeEntity]:
        """
        Returns all stored KnowledgeEntity instances.

        Returns:
            list[KnowledgeEntity]: List of all entities in the repository.
        """
        return list(self._entities)

    def get_by_id(self, entity_id: str) -> KnowledgeEntity:
        """
        Retrieves a single KnowledgeEntity by its unique string ID.

        Args:
            entity_id (str): The entity identifier to look up.

        Returns:
            KnowledgeEntity: The matching entity object.

        Raises:
            EntityNotFoundError: If no entity with entity_id exists.
        """
        if entity_id not in self._by_id:
            raise EntityNotFoundError(
                f"Entity with ID '{entity_id}' not found in KnowledgeRepository."
            )
        return self._by_id[entity_id]

    def has_entity(self, entity_id: str) -> bool:
        """
        Checks whether an entity with the specified ID exists in the repository.

        Args:
            entity_id (str): The entity identifier to check.

        Returns:
            bool: True if the entity exists; False otherwise.
        """
        return entity_id in self._by_id

    def get_by_type(self, entity_type: Type[T]) -> list[T]:
        """
        Retrieves all entities that match or inherit from the requested entity class type.

        Args:
            entity_type (Type[T]): The entity subclass (e.g., EngineeringParameter, MissionDomain).

        Returns:
            list[T]: List of matching entity instances, or empty list if none exist.
        """
        matching: list[T] = []
        for entity in self._entities:
            if isinstance(entity, entity_type):
                matching.append(entity)  # type: ignore
        return matching

    def count(self) -> int:
        """
        Returns the total count of stored entities.

        Returns:
            int: Number of entities in the repository.
        """
        return len(self._entities)

    def entity_types(self) -> list[type]:
        """
        Returns a list of all distinct entity classes currently stored in the repository.

        Returns:
            list[type]: List of entity classes.
        """
        return list(self._by_type.keys())
