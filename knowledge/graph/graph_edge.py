"""
GraphEdge Domain Subsystem

Purpose:
    Defines the `GraphEdge` class representing a directed edge within the `KnowledgeGraph`.

Role in Architecture:
    `GraphEdge` serves as the internal graph edge data structure for `KnowledgeGraph`.
    While `KnowledgeRelationship` represents high-level domain semantics (e.g., MissionCategory REQUIRES EngineeringParameter),
    `GraphEdge` models graph-level directed connectivity (source_id, target_id, relationship_type, metadata)
    used by graph traversal, pathfinding, and query algorithms.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class GraphEdge:
    """
    Graph edge representation used internally by KnowledgeGraph and graph traversal engines.

    Attributes:
        source_id (str): Unique ID of the source entity node.
        target_id (str): Unique ID of the destination entity node.
        relationship_type (str): Graph relationship type (e.g., 'depends_on', 'references', 'belongs_to', 'requires', 'contains').
        metadata (dict[str, Any]): Optional edge metadata dictionary (e.g., weight, confidence, origin_document).

    Architectural Relationships:
        - `KnowledgeRelationship`: High-level domain relationship model.
        - `KnowledgeGraph`: Uses `GraphEdge` internally for adjacency lists and edge operations.
    """

    source_id: str
    target_id: str
    relationship_type: str
    metadata: dict[str, Any] = field(default_factory=dict)
