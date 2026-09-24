"""
GraphConstructionPipeline Orchestration Subsystem

Purpose:
    Defines the `GraphConstructionPipeline` class, which orchestrates the complete sequential graph construction process
    for the Engineering Knowledge Graph.

Role in Architecture:
    `GraphConstructionPipeline` serves as the single primary orchestration point for building a `KnowledgeGraph`.
    It coordinates the execution order of `GraphBuilder` (node creation stage) and `RelationshipResolver`
    (edge connection stage). Future stages (e.g., CrossReferenceResolver, GraphValidator) will be added to this pipeline.
"""

from typing import Callable, Type
from backend.knowledge.graph.knowledge_graph import KnowledgeGraph
from backend.knowledge.graph.graph_builder import GraphBuilder
from backend.knowledge.graph.relationship_resolver import RelationshipResolver


class GraphConstructionPipeline:
    """
    Orchestrates the multi-stage construction of a connected KnowledgeGraph.

    Workflow:
        1. Invoke `builder.build()` to instantiate and populate initial graph nodes.
        2. Instantiate `RelationshipResolver` using the constructed `KnowledgeGraph`.
        3. Invoke `resolver.resolve()` to resolve and connect graph edges.
        4. Return the fully connected `KnowledgeGraph`.

    Design Principles:
        - Single Responsibility Principle (SRP): Graph construction orchestration only.
        - Dependency Injection: `GraphBuilder` and `RelationshipResolver` factory are injected.
        - Open/Closed Principle (OCP): Future graph processing stages can be inserted without API breaks.
    """

    def __init__(
        self,
        builder: GraphBuilder,
        resolver_factory: Type[RelationshipResolver] | Callable[[KnowledgeGraph], RelationshipResolver] = RelationshipResolver,
    ) -> None:
        """
        Initializes the GraphConstructionPipeline with injected collaborator dependencies.

        Args:
            builder (GraphBuilder): Injected node builder.
            resolver_factory (Type[RelationshipResolver] | Callable[[KnowledgeGraph], RelationshipResolver]):
                Injected factory or class used to instantiate RelationshipResolver for a KnowledgeGraph.
        """
        self._builder: GraphBuilder = builder
        self._resolver_factory = resolver_factory

    def construct(self) -> KnowledgeGraph:
        """
        Executes the graph construction pipeline and returns a connected KnowledgeGraph.

        Returns:
            KnowledgeGraph: The completed and connected KnowledgeGraph instance.

        Raises:
            EmptyRepositoryError: If the repository contains zero entities.
            DuplicateGraphEntityError: If duplicate nodes exist.
            UnresolvedRelationshipError: If a relationship target or source entity is missing.
        """
        # Step 1: Build initial node graph topology
        graph = self._builder.build()

        # Step 2: Resolve and connect directed relationship edges
        resolver = self._resolver_factory(graph)
        resolver.resolve()

        # Step 3: Return completed KnowledgeGraph
        return graph
