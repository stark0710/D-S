"""
GraphIndexer Secondary Indexing Subsystem

Purpose:
    Defines the `GraphIndexer` class responsible for building and maintaining secondary read-only
    $O(1)$ lookup indexes over a `KnowledgeGraph`.

Role in Architecture:
    `GraphIndexer` optimizes graph queries and traversals for downstream engines (QueryEngine, DesignEngine,
    OptimizationEngine). It indexes graph nodes by ID, classification label, and concrete entity type, and indexes
    graph edges by relationship type. It also provides fast 1-hop neighbor lookup operations.
"""

from typing import Type, TypeVar
from collections import defaultdict
from backend.models.knowledge_entity import KnowledgeEntity
from backend.knowledge.graph.knowledge_graph import KnowledgeGraph
from backend.knowledge.graph.graph_node import GraphNode
from backend.knowledge.graph.graph_edge import GraphEdge

T = TypeVar("T", bound=KnowledgeEntity)


class GraphIndexerError(ValueError):
    """Base exception class for GraphIndexer operations."""
    pass


class GraphNodeNotFoundError(GraphIndexerError, KeyError):
    """Raised when querying a node ID that is absent from the index."""
    pass


class GraphIndexer:
    """
    Read-only secondary index container for fast O(1) KnowledgeGraph lookups.

    Maintains:
        - `_node_id_index`: dict[str, GraphNode]
        - `_label_index`: dict[str, list[GraphNode]]
        - `_entity_type_index`: dict[type, list[GraphNode]]
        - `_relationship_type_index`: dict[str, list[GraphEdge]]

    Design Principles:
        - Single Responsibility Principle (SRP): Secondary index creation and fast lookups only.
        - Dependency Injection: Injects `KnowledgeGraph` via constructor.
        - Read-Only Optimization: Does not mutate graph topology.
    """

    def __init__(self, graph: KnowledgeGraph) -> None:
        """
        Initializes the GraphIndexer with an injected KnowledgeGraph dependency and builds initial indexes.

        Args:
            graph (KnowledgeGraph): Injected graph instance to index.
        """
        self._graph: KnowledgeGraph = graph
        self._node_id_index: dict[str, GraphNode] = {}
        self._label_index: dict[str, list[GraphNode]] = defaultdict(list)
        self._entity_type_index: dict[type, list[GraphNode]] = defaultdict(list)
        self._relationship_type_index: dict[str, list[GraphEdge]] = defaultdict(list)

        self.build_indexes()

    def build_indexes(self) -> None:
        """
        Populates node ID, label, entity type, and relationship type indexes from the KnowledgeGraph.
        """
        self._node_id_index.clear()
        self._label_index.clear()
        self._entity_type_index.clear()
        self._relationship_type_index.clear()

        # Index nodes
        for node in self._graph.nodes():
            node_id = node.id()
            self._node_id_index[node_id] = node

            # Index node labels
            for label in node.labels:
                self._label_index[label].append(node)

            # Index entity type
            entity_cls = node.entity_type()
            self._entity_type_index[entity_cls].append(node)

        # Index relationship edges
        for node in self._graph.nodes():
            for edge in node.outgoing_edges:
                rel_type = edge.relationship_type
                self._relationship_type_index[rel_type].append(edge)

    def get_node_by_id(self, entity_id: str) -> GraphNode:
        """
        Retrieves a GraphNode by its entity ID in O(1) time.

        Args:
            entity_id (str): Entity identifier to look up.

        Returns:
            GraphNode: The matching graph node object.

        Raises:
            GraphNodeNotFoundError: If entity_id is missing from the index.
        """
        if entity_id not in self._node_id_index:
            raise GraphNodeNotFoundError(
                f"GraphNode with ID '{entity_id}' not found in GraphIndexer."
            )
        return self._node_id_index[entity_id]

    def get_nodes_by_label(self, label: str) -> list[GraphNode]:
        """
        Retrieves all GraphNodes tagged with the specified graph label.

        Args:
            label (str): Classification label string (e.g., 'EngineeringParameter').

        Returns:
            list[GraphNode]: List of matching graph nodes, or empty list if none exist.
        """
        return list(self._label_index.get(label, []))

    def get_nodes_by_entity_type(self, entity_type: Type[T]) -> list[GraphNode]:
        """
        Retrieves all GraphNodes wrapping entities that match or inherit from entity_type.

        Args:
            entity_type (Type[T]): Concrete or base entity class (e.g., EngineeringParameter).

        Returns:
            list[GraphNode]: List of matching graph nodes.
        """
        matching: list[GraphNode] = []
        for node in self._node_id_index.values():
            if isinstance(node.entity, entity_type):
                matching.append(node)
        return matching

    def get_edges_by_relationship(self, relationship_type: str) -> list[GraphEdge]:
        """
        Retrieves all GraphEdge instances matching the specified relationship type string.

        Args:
            relationship_type (str): Relationship classification string (e.g., 'depends_on').

        Returns:
            list[GraphEdge]: List of matching graph edges, or empty list if none exist.
        """
        return list(self._relationship_type_index.get(relationship_type, []))

    def get_neighbors(self, entity_id: str) -> list[GraphNode]:
        """
        Retrieves all directly connected (1-hop) neighbor GraphNodes for a given entity ID.

        Gathers both target nodes of outgoing edges and source nodes of incoming edges.

        Args:
            entity_id (str): Entity identifier whose neighbors to retrieve.

        Returns:
            list[GraphNode]: List of unique adjacent neighbor GraphNodes.

        Raises:
            GraphNodeNotFoundError: If entity_id does not exist.
        """
        node = self.get_node_by_id(entity_id)
        neighbor_ids: set[str] = set()

        for edge in node.outgoing_edges:
            neighbor_ids.add(edge.target_id)

        for edge in node.incoming_edges:
            neighbor_ids.add(edge.source_id)

        return [self._node_id_index[nid] for nid in neighbor_ids if nid in self._node_id_index]
