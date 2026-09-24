"""
KnowledgeGraph Domain Storage Subsystem

Purpose:
    Defines the `KnowledgeGraph` class, which serves as the canonical in-memory graph structure
    for storing engineering domain entities (nodes) and directed relationships (edges).

Role in Architecture:
    `KnowledgeGraph` encapsulates entity node storage and adjacency list representation of edges.
    Future components (GraphBuilder, QueryEngine, DesignEngine, OptimizationEngine) manipulate
    and query `KnowledgeGraph` to perform multi-hop traversals, rule checks, and dependency resolution.
"""

from collections import defaultdict
from backend.models.knowledge_entity import KnowledgeEntity
from backend.models.knowledge_relationship import KnowledgeRelationship
from backend.knowledge.graph.graph_edge import GraphEdge
from backend.knowledge.graph.graph_node import GraphNode


class KnowledgeGraphError(ValueError):
    """Base exception class for KnowledgeGraph operations."""
    pass


class DuplicateGraphEntityError(KnowledgeGraphError):
    """Raised when attempting to add an entity whose ID already exists in the graph."""
    pass


class InvalidRelationshipError(KnowledgeGraphError, KeyError):
    """Raised when attempting to add a relationship referencing a non-existent source or target entity ID."""
    pass


class GraphEntityNotFoundError(KnowledgeGraphError, KeyError):
    """Raised when looking up an entity ID that is not present in the graph."""
    pass


class KnowledgeGraph:
    """
    In-memory graph data structure representing engineering entities and directed relationships.

    Internal Storage Strategy:
        - Entity Lookup: `dict[str, KnowledgeEntity]` mapping unique entity ID to KnowledgeEntity.
        - Node Lookup: `dict[str, GraphNode]` mapping unique entity ID to GraphNode wrapper.
        - Relationship List: `list[KnowledgeRelationship]` containing all graph edges.
        - Adjacency List: `dict[str, list[KnowledgeRelationship]]` mapping source_id to outgoing edges.

    Responsibilities:
        - Store entity nodes and enforce unique node ID constraints.
        - Store relationship edges and enforce referential integrity (source & target nodes must exist).
        - Maintain outgoing adjacency lists for fast $O(1)$ edge traversal.
        - Maintain `GraphNode` incoming and outgoing edge connectivity.
    """

    def __init__(self) -> None:
        """Initializes an empty KnowledgeGraph."""
        self._entities: dict[str, KnowledgeEntity] = {}
        self._nodes: dict[str, GraphNode] = {}
        self._relationships: list[KnowledgeRelationship] = []
        self._adjacency_list: dict[str, list[KnowledgeRelationship]] = defaultdict(list)

    def add_entity(self, entity: KnowledgeEntity) -> None:
        """
        Adds a KnowledgeEntity node to the graph.

        Args:
            entity (KnowledgeEntity): The entity node to add.

        Raises:
            DuplicateGraphEntityError: If an entity with the same ID already exists in the graph.
        """
        if entity.id in self._entities:
            existing = self._entities[entity.id]
            raise DuplicateGraphEntityError(
                f"Cannot add duplicate entity to graph: ID '{entity.id}' is already registered for '{existing.name}'."
            )

        self._entities[entity.id] = entity
        self._nodes[entity.id] = GraphNode(
            entity=entity,
            labels={type(entity).__name__}
        )

    def add_relationship(self, relationship: KnowledgeRelationship | GraphEdge) -> None:
        """
        Adds a directed relationship edge to the graph.

        Referential Integrity:
            Both `relationship.source_id` and `relationship.target_id` must exist in the graph.

        Args:
            relationship (KnowledgeRelationship | GraphEdge): The directed relationship edge to add.

        Raises:
            InvalidRelationshipError: If either source_id or target_id is not present in the graph nodes.
        """
        source_id = relationship.source_id
        target_id = relationship.target_id

        if source_id not in self._entities:
            raise InvalidRelationshipError(
                f"Relationship error: Source entity ID '{source_id}' does not exist in the graph."
            )

        if target_id not in self._entities:
            raise InvalidRelationshipError(
                f"Relationship error: Target entity ID '{target_id}' does not exist in the graph."
            )

        # Convert to KnowledgeRelationship if GraphEdge was passed for storage compatibility
        if isinstance(relationship, GraphEdge):
            rel_model = KnowledgeRelationship(
                source_id=source_id,
                source_type=self._entities[source_id].__class__.__name__,
                target_id=target_id,
                target_type=self._entities[target_id].__class__.__name__,
                relationship_type=relationship.relationship_type
            )
            graph_edge = relationship
        else:
            rel_model = relationship
            graph_edge = GraphEdge(
                source_id=source_id,
                target_id=target_id,
                relationship_type=relationship.relationship_type
            )

        self._relationships.append(rel_model)
        self._adjacency_list[source_id].append(rel_model)

        # Update GraphNode incoming and outgoing edge lists
        if source_id in self._nodes:
            self._nodes[source_id].add_outgoing_edge(graph_edge)
        if target_id in self._nodes:
            self._nodes[target_id].add_incoming_edge(graph_edge)

    def get_entity(self, entity_id: str) -> KnowledgeEntity:
        """
        Retrieves an entity node by its unique string ID.

        Args:
            entity_id (str): The entity identifier to look up.

        Returns:
            KnowledgeEntity: The matching entity object.

        Raises:
            GraphEntityNotFoundError: If no entity with entity_id exists in the graph.
        """
        if entity_id not in self._entities:
            raise GraphEntityNotFoundError(
                f"Entity with ID '{entity_id}' not found in KnowledgeGraph."
            )
        return self._entities[entity_id]

    def get_node(self, entity_id: str) -> GraphNode:
        """
        Retrieves the GraphNode wrapper for an entity ID.

        Args:
            entity_id (str): Entity identifier to look up.

        Returns:
            GraphNode: The matching graph node object.

        Raises:
            GraphEntityNotFoundError: If no node with entity_id exists in the graph.
        """
        if entity_id not in self._nodes:
            raise GraphEntityNotFoundError(
                f"GraphNode with ID '{entity_id}' not found in KnowledgeGraph."
            )
        return self._nodes[entity_id]

    def has_entity(self, entity_id: str) -> bool:
        """
        Checks whether an entity node exists in the graph.

        Args:
            entity_id (str): Entity identifier to check.

        Returns:
            bool: True if entity exists; False otherwise.
        """
        return entity_id in self._entities

    def get_relationships(self, entity_id: str) -> list[KnowledgeRelationship]:
        """
        Retrieves all outgoing relationships originating from the specified source entity ID.

        Args:
            entity_id (str): Source entity identifier.

        Returns:
            list[KnowledgeRelationship]: List of outgoing directed edges, or empty list if none.
        """
        return list(self._adjacency_list.get(entity_id, []))

    def entity_count(self) -> int:
        """
        Returns total number of entity nodes in the graph.

        Returns:
            int: Node count.
        """
        return len(self._entities)

    def relationship_count(self) -> int:
        """
        Returns total number of relationship edges in the graph.

        Returns:
            int: Edge count.
        """
        return len(self._relationships)

    def entities(self) -> list[KnowledgeEntity]:
        """
        Returns list of all stored entity nodes.

        Returns:
            list[KnowledgeEntity]: List of all graph nodes.
        """
        return list(self._entities.values())

    def nodes(self) -> list[GraphNode]:
        """
        Returns list of all GraphNode wrappers stored in the graph.

        Returns:
            list[GraphNode]: List of all graph nodes.
        """
        return list(self._nodes.values())

    def relationships(self) -> list[KnowledgeRelationship]:
        """
        Returns list of all stored relationship edges.

        Returns:
            list[KnowledgeRelationship]: List of all graph edges.
        """
        return list(self._relationships)
