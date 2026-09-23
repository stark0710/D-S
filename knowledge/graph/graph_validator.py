"""
GraphValidator Structural Integrity Subsystem

Purpose:
    Defines the `GraphValidator` class responsible for performing structural validation and diagnostic reporting
    on a fully constructed `KnowledgeGraph`.

Role in Architecture:
    `GraphValidator` verifies graph integrity before the `KnowledgeGraph` is exposed to downstream engine services
    (QueryEngine, DesignEngine, OptimizationEngine). It evaluates referential integrity, adjacency list consistency,
    node wrapping, edge uniqueness, and calculates graph statistics. It performs verification only and does not mutate or repair the graph.
"""

from typing import Any
from backend.models.knowledge_entity import KnowledgeEntity
from backend.knowledge.graph.knowledge_graph import KnowledgeGraph
from backend.knowledge.graph.graph_validation_result import GraphValidationResult


class GraphValidator:
    """
    Structural validator and metric calculator for KnowledgeGraph instances.

    Validation Rules Enforced:
        Rule 1: Every edge source_id must exist in graph nodes.
        Rule 2: Every edge target_id must exist in graph nodes.
        Rule 3: Every outgoing edge must appear in the source GraphNode.outgoing_edges.
        Rule 4: Every incoming edge must appear in the destination GraphNode.incoming_edges.
        Rule 5: KnowledgeGraph adjacency list must match stored edges.
        Rule 6: Duplicate entity IDs are not allowed.
        Rule 7: Duplicate graph edges are flagged as warnings/errors.
        Rule 8: Every node must wrap a valid KnowledgeEntity instance.

    Design Principles:
        - Single Responsibility Principle (SRP): Read-only structural validation and metrics only.
        - Dependency Injection: Injects `KnowledgeGraph` via constructor.
        - Clean Architecture: Decoupled from graph construction, parsing, and reasoning logic.
    """

    def __init__(self, graph: KnowledgeGraph) -> None:
        """
        Initializes the GraphValidator with an injected KnowledgeGraph dependency.

        Args:
            graph (KnowledgeGraph): Injected graph instance to validate.
        """
        self._graph: KnowledgeGraph = graph

    def validate(self) -> GraphValidationResult:
        """
        Performs structural verification on the KnowledgeGraph and calculates graph topology metrics.

        Returns:
            GraphValidationResult: Complete validation diagnostic report containing status, errors, warnings, and statistics.
        """
        errors: list[str] = []
        warnings: list[str] = []
        stats: dict[str, Any] = {}

        nodes = self._graph.nodes()
        relationships = self._graph.relationships()
        node_ids = {node.id() for node in nodes}

        # Rule 6 & Rule 8: Node and wrapped KnowledgeEntity validation
        seen_ids: set[str] = set()
        for node in nodes:
            entity = node.entity
            if not isinstance(entity, KnowledgeEntity):
                errors.append(f"Rule 8 Violation: Node '{node.id()}' wraps an invalid non-KnowledgeEntity object.")

            if not entity.id or not str(entity.id).strip():
                errors.append(f"Rule 8 Violation: Node wraps an entity with an empty or missing ID.")

            if entity.id in seen_ids:
                errors.append(f"Rule 6 Violation: Duplicate entity ID '{entity.id}' detected in graph nodes.")
            seen_ids.add(entity.id)

        # Rule 1, 2, & 7: Edge and referential integrity validation
        seen_edges: set[tuple[str, str, str]] = set()
        for rel in relationships:
            # Rule 1: Source exists
            if rel.source_id not in node_ids:
                errors.append(
                    f"Rule 1 Violation: Edge from '{rel.source_id}' to '{rel.target_id}' references missing source_id '{rel.source_id}'."
                )

            # Rule 2: Target exists
            if rel.target_id not in node_ids:
                errors.append(
                    f"Rule 2 Violation: Edge from '{rel.source_id}' to '{rel.target_id}' references missing target_id '{rel.target_id}'."
                )

            # Rule 7: Duplicate edges
            edge_key = (rel.source_id, rel.target_id, rel.relationship_type)
            if edge_key in seen_edges:
                warnings.append(
                    f"Rule 7 Warning: Duplicate edge detected from '{rel.source_id}' to '{rel.target_id}' with type '{rel.relationship_type}'."
                )
            seen_edges.add(edge_key)

        # Rule 3, 4, & 5: Node edge lists and adjacency list consistency
        for node in nodes:
            node_id = node.id()

            # Rule 3: Outgoing edges on source node match relationships originating from source
            expected_outgoing = [r for r in relationships if r.source_id == node_id]
            actual_outgoing_targets = {e.target_id for e in node.outgoing_edges}
            expected_outgoing_targets = {r.target_id for r in expected_outgoing}

            if actual_outgoing_targets != expected_outgoing_targets:
                errors.append(
                    f"Rule 3 Violation: Outgoing edge mismatch on node '{node_id}'. Expected targets {expected_outgoing_targets}, found {actual_outgoing_targets}."
                )

            # Rule 4: Incoming edges on target node match relationships terminating at target
            expected_incoming = [r for r in relationships if r.target_id == node_id]
            actual_incoming_sources = {e.source_id for e in node.incoming_edges}
            expected_incoming_sources = {r.source_id for r in expected_incoming}

            if actual_incoming_sources != expected_incoming_sources:
                errors.append(
                    f"Rule 4 Violation: Incoming edge mismatch on node '{node_id}'. Expected sources {expected_incoming_sources}, found {actual_incoming_sources}."
                )

            # Rule 5: Adjacency list match
            adj_rels = self._graph.get_relationships(node_id)
            if len(adj_rels) != len(expected_outgoing):
                errors.append(
                    f"Rule 5 Violation: Adjacency list mismatch on node '{node_id}'. Graph adjacency count is {len(adj_rels)}, expected {len(expected_outgoing)}."
                )

        # Calculate graph topological statistics
        total_nodes = len(nodes)
        total_edges = len(relationships)
        degrees = [node.degree() for node in nodes] if total_nodes > 0 else []

        isolated_count = sum(1 for d in degrees if d == 0)
        avg_degree = sum(degrees) / total_nodes if total_nodes > 0 else 0.0
        max_degree = max(degrees) if degrees else 0
        min_degree = min(degrees) if degrees else 0

        stats["entity_count"] = total_nodes
        stats["edge_count"] = total_edges
        stats["isolated_nodes"] = isolated_count
        stats["average_degree"] = round(avg_degree, 2)
        stats["maximum_degree"] = max_degree
        stats["minimum_degree"] = min_degree

        is_valid = len(errors) == 0

        return GraphValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            statistics=stats
        )
