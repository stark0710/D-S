"""
RelationshipResolver Graph Enrichment Subsystem

Purpose:
    Defines the `RelationshipResolver` class, which enriches a `KnowledgeGraph` by inspecting
    `KnowledgeRelationship` definitions attached to entity domain models and instantiating
    corresponding directed `GraphEdge` objects in the graph topology.

Role in Architecture:
    `RelationshipResolver` connects graph nodes into a unified knowledge graph network.
    It takes an injected `KnowledgeGraph` (populated with nodes by `GraphBuilder`), extracts domain
    relationships, validates referential integrity (source and target nodes must exist in the graph),
    constructs `GraphEdge` objects, and updates node adjacency indexes (incoming and outgoing edges).
"""

from backend.knowledge.graph.knowledge_graph import KnowledgeGraph, InvalidRelationshipError
from backend.knowledge.graph.graph_edge import GraphEdge
from backend.models.knowledge_relationship import KnowledgeRelationship
from backend.models.mission_domain import MissionDomain
from backend.models.engineering_parameter import EngineeringParameter


class RelationshipResolverError(ValueError):
    """Base exception class for RelationshipResolver errors."""
    pass


class UnresolvedRelationshipError(RelationshipResolverError):
    """Raised when a relationship references a source or target entity ID that is absent from the graph."""
    pass


class RelationshipResolver:
    """
    Enriches a KnowledgeGraph by resolving KnowledgeRelationship definitions into directed GraphEdge connections.

    Workflow:
        1. Iterate through all `GraphNode` instances in the `KnowledgeGraph`.
        2. Read the underlying `KnowledgeEntity` from each node.
        3. Retrieve explicit `KnowledgeRelationship` objects (and implicit reference/category relationships).
        4. Validate that both `source_id` and `target_id` exist in the graph.
        5. Instantiate `GraphEdge` objects and add them to `KnowledgeGraph`.
        6. Update source node `outgoing_edges` and target node `incoming_edges`.

    Design Principles:
        - Single Responsibility Principle (SRP): Graph edge resolution only.
        - Dependency Injection: Receives `KnowledgeGraph` via constructor.
        - Clean Architecture: Operates on graph abstractions without modifying domain models or parsing files.
    """

    def __init__(self, graph: KnowledgeGraph) -> None:
        """
        Initializes the RelationshipResolver with an injected KnowledgeGraph dependency.

        Args:
            graph (KnowledgeGraph): Injected graph instance to enrich.
        """
        self._graph: KnowledgeGraph = graph

    def resolve(self) -> None:
        """
        Resolves domain relationships and connects graph nodes with GraphEdge instances.

        Raises:
            UnresolvedRelationshipError: If a relationship target or source entity does not exist in the graph.
        """
        for node in self._graph.nodes():
            entity = node.entity
            relationships: list[KnowledgeRelationship] = list(getattr(entity, "relationships", []))

            # Extract implicit domain entity relationships if explicit relationships list is empty
            if isinstance(entity, MissionDomain) and hasattr(entity, "category_ids"):
                for cid in entity.category_ids:
                    relationships.append(
                        KnowledgeRelationship(
                            source_id=entity.id,
                            source_type="MissionDomain",
                            target_id=cid,
                            target_type="MissionCategory",
                            relationship_type="contains"
                        )
                    )

            if isinstance(entity, EngineeringParameter) and hasattr(entity, "reference_ids"):
                for ref_id in entity.reference_ids:
                    # Skip reference edges if target reference entity is not loaded in node graph
                    if not self._graph.has_entity(ref_id):
                        continue
                    relationships.append(
                        KnowledgeRelationship(
                            source_id=entity.id,
                            source_type="EngineeringParameter",
                            target_id=ref_id,
                            target_type="KnowledgeReference",
                            relationship_type="references"
                        )
                    )

            for rel in relationships:
                # Referential integrity validation
                if not self._graph.has_entity(rel.source_id):
                    raise UnresolvedRelationshipError(
                        f"Relationship resolution failed: Source entity ID '{rel.source_id}' does not exist in KnowledgeGraph."
                    )

                if not self._graph.has_entity(rel.target_id):
                    raise UnresolvedRelationshipError(
                        f"Relationship resolution failed: Target entity ID '{rel.target_id}' does not exist in KnowledgeGraph."
                    )

                edge = GraphEdge(
                    source_id=rel.source_id,
                    target_id=rel.target_id,
                    relationship_type=rel.relationship_type,
                    metadata={"source_type": rel.source_type, "target_type": rel.target_type}
                )

                self._graph.add_relationship(edge)
