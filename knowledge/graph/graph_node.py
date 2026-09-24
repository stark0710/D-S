"""
GraphNode Domain Subsystem

Purpose:
    Defines the `GraphNode` class representing a node wrapper around a `KnowledgeEntity` within the `KnowledgeGraph`.

Role in Architecture:
    `GraphNode` serves as the internal graph node data structure for `KnowledgeGraph`.
    While `KnowledgeEntity` represents domain engineering models (e.g. EngineeringParameter, MissionDomain),
    `GraphNode` wraps the entity and stores graph-specific metadata (incoming_edges, outgoing_edges,
    labels, and dynamic graph properties) used by traversal, pathfinding, and query algorithms.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.models.knowledge_entity import KnowledgeEntity
from backend.knowledge.graph.graph_edge import GraphEdge


@dataclass(slots=True, eq=False)
class GraphNode:
    """
    Graph node representation used internally by KnowledgeGraph and graph traversal engines.

    Field Definitions:
        entity (KnowledgeEntity): The underlying domain entity object wrapped by this node.
        incoming_edges (list[GraphEdge]): Edges terminating at this node.
        outgoing_edges (list[GraphEdge]): Edges originating from this node.
        labels (set[str]): Graph classification labels (e.g., 'EngineeringParameter', 'Aerodynamics').
        properties (dict[str, Any]): Graph traversal metadata (e.g., 'visited', 'depth', 'score').

    Architectural Relationships:
        - `KnowledgeEntity`: Domain engineering object wrapped inside `entity`.
        - `GraphEdge`: Incoming and outgoing edge references.
        - `KnowledgeGraph`: Manages collection of `GraphNode` instances.
    """

    entity: KnowledgeEntity
    incoming_edges: list[GraphEdge] = field(default_factory=list)
    outgoing_edges: list[GraphEdge] = field(default_factory=list)
    labels: set[str] = field(default_factory=set)
    properties: dict[str, Any] = field(default_factory=dict)

    def id(self) -> str:
        """
        Returns the unique identifier of the wrapped entity.

        Returns:
            str: Entity ID.
        """
        return self.entity.id

    def entity_type(self) -> type:
        """
        Returns the concrete class type of the wrapped entity.

        Returns:
            type: Concrete KnowledgeEntity class type (e.g., EngineeringParameter).
        """
        return type(self.entity)

    def degree(self) -> int:
        """
        Calculates the total degree (incoming + outgoing edges) of this graph node.

        Returns:
            int: Combined edge count.
        """
        return len(self.incoming_edges) + len(self.outgoing_edges)

    def add_incoming_edge(self, edge: GraphEdge) -> None:
        """
        Appends an incoming GraphEdge to this node's incoming edges list.

        Args:
            edge (GraphEdge): Incoming edge terminating at this node.
        """
        self.incoming_edges.append(edge)

    def add_outgoing_edge(self, edge: GraphEdge) -> None:
        """
        Appends an outgoing GraphEdge to this node's outgoing edges list.

        Args:
            edge (GraphEdge): Outgoing edge originating from this node.
        """
        self.outgoing_edges.append(edge)

    def __hash__(self) -> int:
        """Returns hash based on entity ID."""
        return hash(self.entity.id)

    def __eq__(self, other: object) -> bool:
        """Checks equality based on entity ID."""
        if not isinstance(other, GraphNode):
            return False
        return self.entity.id == other.entity.id
