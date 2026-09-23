"""
KnowledgeRelationship Domain Model

Purpose:
    Defines the `KnowledgeRelationship` domain model representing explicit directed connections
    between domain entities within the Torq Wings Design Studio backend.

Role in Architecture:
    `KnowledgeRelationship` serves as the foundational edge model for the platform's Knowledge Graph.
    By representing relationships independently of domain entity classes, the domain model maintains
    decoupled, lightweight entity definitions while supporting flexible graph traversals and queries
    (e.g., MissionDomain CONTAINS MissionCategory, MissionCategory REQUIRES EngineeringParameter,
    EngineeringParameter DEPENDS_ON EngineeringParameter).
"""

from dataclasses import dataclass


@dataclass(slots=True)
class KnowledgeRelationship:
    """
    Domain model representing a directed relationship (edge) between two knowledge entities.

    Unlike domain entities, a `KnowledgeRelationship` does NOT inherit from `KnowledgeEntity`
    because a relationship is an edge connection rather than an entity identity.

    Architectural Role & Knowledge Graph Foundation:
        - Separate Representation: Decouples entity definitions from structural graph topology.
        - Id-based Referencing: Stores string identifiers (`source_id`, `target_id`) rather than
          direct object references, avoiding cyclic dependencies and memory-heavy graphs.
        - Framework Independent: Pure dataclass free of ORMs, databases, APIs, parsers, and AI logic.

    Attributes:
        source_id (str): Unique identifier of the source entity (origin node).
        source_type (str): Type classification of the source entity (e.g., 'MissionDomain').
        target_id (str): Unique identifier of the target entity (destination node).
        target_type (str): Type classification of the target entity (e.g., 'MissionCategory').
        relationship_type (str): Relationship semantics (e.g., 'CONTAINS', 'REQUIRES', 'DEPENDS_ON').
    """

    source_id: str
    source_type: str
    target_id: str
    target_type: str
    relationship_type: str
