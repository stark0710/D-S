"""
GraphBuilder Construction Subsystem

Purpose:
    Defines the `GraphBuilder` class responsible for populating a `KnowledgeGraph` from an in-memory `KnowledgeRepository`.

Role in Architecture:
    `GraphBuilder` acts as the initial graph construction stage in Phase 3 (Knowledge Graph Foundation).
    It receives an injected `KnowledgeRepository`, iterates over all loaded `KnowledgeEntity` objects,
    wraps each entity in a `GraphNode` with classification labels, and builds the initial node topology
    of the `KnowledgeGraph`. Edge construction will be added in subsequent sprints.
"""

from backend.knowledge.knowledge_repository import KnowledgeRepository
from backend.knowledge.graph.knowledge_graph import KnowledgeGraph, DuplicateGraphEntityError
from backend.models.knowledge_entity import KnowledgeEntity


class GraphBuilderError(ValueError):
    """Base exception class for GraphBuilder errors."""
    pass


class EmptyRepositoryError(GraphBuilderError):
    """Raised when attempting to build a KnowledgeGraph from an empty KnowledgeRepository."""
    pass


class GraphBuilder:
    """
    Builder responsible for constructing a KnowledgeGraph node topology from a KnowledgeRepository.

    Workflow:
        1. Verify `KnowledgeRepository` contains loaded entities.
        2. Create an empty `KnowledgeGraph` instance.
        3. Retrieve all `KnowledgeEntity` objects from the repository.
        4. Wrap each entity in a `GraphNode` and add it to `KnowledgeGraph`.
        5. Return the populated `KnowledgeGraph`.

    Design Principles:
        - Dependency Injection: Receives `KnowledgeRepository` via constructor.
        - Single Responsibility Principle (SRP): Node graph construction only.
        - Clean Architecture: Decouples graph construction from parsing and file reading.
    """

    def __init__(self, repository: KnowledgeRepository) -> None:
        """
        Initializes the GraphBuilder with an injected KnowledgeRepository dependency.

        Args:
            repository (KnowledgeRepository): Injected repository containing domain entities.
        """
        self._repository: KnowledgeRepository = repository

    def build(self) -> KnowledgeGraph:
        """
        Constructs and populates a KnowledgeGraph with entity nodes from the repository.

        Returns:
            KnowledgeGraph: A populated KnowledgeGraph containing entity nodes.

        Raises:
            EmptyRepositoryError: If the injected KnowledgeRepository contains zero entities.
            DuplicateGraphEntityError: If duplicate entity IDs are encountered during graph insertion.
        """
        if self._repository.count() == 0:
            raise EmptyRepositoryError(
                "Cannot build KnowledgeGraph: Injected KnowledgeRepository contains zero entities."
            )

        graph = KnowledgeGraph()

        for entity in self._repository.get_all():
            graph.add_entity(entity)

        return graph
