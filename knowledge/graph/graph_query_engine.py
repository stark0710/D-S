"""
GraphQueryEngine Public Query Subsystem

Purpose:
    Defines the `GraphQueryEngine` class, which serves as the unified, read-only public query API
    for accessing the Engineering Knowledge Graph.

Role in Architecture:
    `GraphQueryEngine` acts as the single public entry point for all higher-level platform services
    (Design Engine, Optimization Engine, Rule Engine, Requirement Engine, and AI Assistant).
    It composes `GraphIndexer` for fast $O(1)$ direct lookups and `GraphTraversalService` for $O(V + E)$
    traversal, reachability, and path existence queries.
"""

from typing import Type, TypeVar
from backend.models.knowledge_entity import KnowledgeEntity
from backend.knowledge.graph.graph_indexer import GraphIndexer, GraphNodeNotFoundError
from backend.knowledge.graph.graph_traversal_service import GraphTraversalService, TraversalNodeNotFoundError
from backend.knowledge.graph.graph_node import GraphNode

T = TypeVar("T", bound=KnowledgeEntity)


class GraphQueryEngineError(ValueError):
    """Base exception class for GraphQueryEngine errors."""
    pass


class QueryEntityNotFoundError(GraphQueryEngineError, KeyError):
    """Raised when querying an entity ID that does not exist in the graph."""
    pass


class GraphQueryEngine:
    """
    Unified public query engine for the Engineering Knowledge Graph.

    Query Strategy:
        - Direct & Type Lookups: Uses `GraphIndexer` for O(1) performance.
        - Traversals & Paths: Uses `GraphTraversalService` for O(V + E) reachability and path checks.

    Design Principles:
        - Single Responsibility Principle (SRP): Public graph query interface only.
        - Dependency Injection: Injects `GraphIndexer` and `GraphTraversalService` collaborators.
        - Read-Only Boundary: Exposes entities and nodes without modifying graph structure.
    """

    def __init__(self, indexer: GraphIndexer, traversal_service: GraphTraversalService) -> None:
        """
        Initializes the GraphQueryEngine with injected GraphIndexer and GraphTraversalService dependencies.

        Args:
            indexer (GraphIndexer): Injected secondary graph index instance.
            traversal_service (GraphTraversalService): Injected graph traversal service instance.
        """
        self._indexer: GraphIndexer = indexer
        self._traversal_service: GraphTraversalService = traversal_service

    def get_node(self, entity_id: str) -> GraphNode:
        """
        Retrieves the GraphNode wrapper for an entity ID.

        Complexity:
            O(1) time.

        Args:
            entity_id (str): Entity identifier.

        Returns:
            GraphNode: Graph node wrapper.

        Raises:
            QueryEntityNotFoundError: If entity_id is missing from the graph.
        """
        try:
            return self._indexer.get_node_by_id(entity_id)
        except GraphNodeNotFoundError as err:
            raise QueryEntityNotFoundError(
                f"Graph query failed: Entity ID '{entity_id}' not found in KnowledgeGraph."
            ) from err

    def get_entity(self, entity_id: str) -> KnowledgeEntity:
        """
        Retrieves a strongly typed KnowledgeEntity by its unique ID.

        Complexity:
            O(1) time.

        Args:
            entity_id (str): Entity identifier.

        Returns:
            KnowledgeEntity: Underlying domain entity model.

        Raises:
            QueryEntityNotFoundError: If entity_id is missing from the graph.
        """
        node = self.get_node(entity_id)
        return node.entity

    def get_entities_by_type(self, entity_type: Type[T]) -> list[T]:
        """
        Retrieves all KnowledgeEntity instances matching or inheriting from entity_type.

        Complexity:
            O(1) lookup over entity type index.

        Args:
            entity_type (Type[T]): Concrete entity class (e.g., EngineeringParameter, MissionDomain).

        Returns:
            list[T]: Matching entity domain instances.
        """
        nodes = self._indexer.get_nodes_by_entity_type(entity_type)
        return [node.entity for node in nodes]  # type: ignore

    def get_neighbors(self, entity_id: str) -> list[KnowledgeEntity]:
        """
        Retrieves all directly connected (1-hop) neighbor KnowledgeEntity objects.

        Complexity:
            O(1) average time.

        Args:
            entity_id (str): Entity identifier.

        Returns:
            list[KnowledgeEntity]: List of adjacent entity objects.

        Raises:
            QueryEntityNotFoundError: If entity_id is missing from the graph.
        """
        try:
            neighbor_nodes = self._traversal_service.neighbors(entity_id)
            return [node.entity for node in neighbor_nodes]
        except TraversalNodeNotFoundError as err:
            raise QueryEntityNotFoundError(
                f"Neighbor query failed: Entity ID '{entity_id}' not found in KnowledgeGraph."
            ) from err

    def find_related(
        self,
        entity_id: str,
        relationship_type: str | None = None
    ) -> list[KnowledgeEntity]:
        """
        Finds all KnowledgeEntity objects connected to entity_id via direct edges, optionally filtered by relationship_type.

        Complexity:
            O(k) where k is node degree.

        Args:
            entity_id (str): Entity identifier.
            relationship_type (str | None): Optional relationship type string to filter (e.g., 'depends_on').

        Returns:
            list[KnowledgeEntity]: List of related entity objects.

        Raises:
            QueryEntityNotFoundError: If entity_id is missing from the graph.
        """
        node = self.get_node(entity_id)
        related_ids: set[str] = set()

        for edge in node.outgoing_edges:
            if relationship_type is None or edge.relationship_type.lower() == relationship_type.lower():
                related_ids.add(edge.target_id)

        for edge in node.incoming_edges:
            if relationship_type is None or edge.relationship_type.lower() == relationship_type.lower():
                related_ids.add(edge.source_id)

        related_entities: list[KnowledgeEntity] = []
        for rid in related_ids:
            try:
                related_node = self._indexer.get_node_by_id(rid)
                related_entities.append(related_node.entity)
            except GraphNodeNotFoundError:
                continue

        return related_entities

    def path_exists(self, source_id: str, target_id: str) -> bool:
        """
        Determines whether any directed path exists between source_id and target_id.

        Complexity:
            O(V + E) time.

        Args:
            source_id (str): Origin entity identifier.
            target_id (str): Destination entity identifier.

        Returns:
            bool: True if a directed path exists; False otherwise.

        Raises:
            QueryEntityNotFoundError: If source_id or target_id is missing from the graph.
        """
        try:
            return self._traversal_service.path_exists(source_id, target_id)
        except TraversalNodeNotFoundError as err:
            raise QueryEntityNotFoundError(
                f"Path query failed: {err}"
            ) from err

    def reachable_entities(self, entity_id: str) -> list[KnowledgeEntity]:
        """
        Retrieves all KnowledgeEntity objects reachable from entity_id via directed paths.

        Complexity:
            O(V + E) time.

        Args:
            entity_id (str): Starting entity identifier.

        Returns:
            list[KnowledgeEntity]: List of all reachable entity objects.

        Raises:
            QueryEntityNotFoundError: If entity_id is missing from the graph.
        """
        try:
            reachable_nodes = self._traversal_service.reachable_nodes(entity_id)
            return [node.entity for node in reachable_nodes]
        except TraversalNodeNotFoundError as err:
            raise QueryEntityNotFoundError(
                f"Reachable entities query failed: Entity ID '{entity_id}' not found in KnowledgeGraph."
            ) from err
