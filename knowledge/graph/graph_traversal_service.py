"""
GraphTraversalService Graph Algorithms Subsystem

Purpose:
    Defines the `GraphTraversalService` class responsible for providing reusable, deterministic,
    read-only graph traversal algorithms over a `KnowledgeGraph` using a `GraphIndexer`.

Role in Architecture:
    `GraphTraversalService` serves as the core graph algorithm engine for Phase 3 (Knowledge Graph Foundation).
    It provides Breadth-First Search (BFS), Depth-First Search (DFS), 1-hop neighborhood lookup,
    full reachability analysis, and path existence detection for higher-level query engines, design engines,
    and AI assistants.
"""

from collections import deque
from backend.knowledge.graph.knowledge_graph import KnowledgeGraph
from backend.knowledge.graph.graph_indexer import GraphIndexer, GraphNodeNotFoundError
from backend.knowledge.graph.graph_node import GraphNode


class TraversalServiceError(ValueError):
    """Base exception class for GraphTraversalService errors."""
    pass


class TraversalNodeNotFoundError(TraversalServiceError, KeyError):
    """Raised when traversal operations reference an entity ID that is missing from the graph index."""
    pass


class GraphTraversalService:
    """
    Reusable, read-only graph algorithm service.

    Supported Algorithms:
        - `breadth_first_search(start_id)`: Iterative queue-based BFS traversal in O(V + E) time.
        - `depth_first_search(start_id)`: Iterative stack-based DFS traversal in O(V + E) time.
        - `neighbors(entity_id)`: 1-hop adjacent neighbor discovery in O(1) average time via GraphIndexer.
        - `reachable_nodes(start_id)`: Set of all nodes reachable from start_id in O(V + E) time.
        - `path_exists(source_id, target_id)`: Determines whether a directed path exists in O(V + E) time.

    Design Principles:
        - Single Responsibility Principle (SRP): Graph traversal algorithms only.
        - Dependency Injection: Injects `KnowledgeGraph` and `GraphIndexer` collaborators.
        - Read-Only & Deterministic: Does not mutate graph topology or score/modify nodes.
    """

    def __init__(self, graph: KnowledgeGraph, indexer: GraphIndexer) -> None:
        """
        Initializes the GraphTraversalService with injected KnowledgeGraph and GraphIndexer dependencies.

        Args:
            graph (KnowledgeGraph): Injected graph instance.
            indexer (GraphIndexer): Injected secondary index instance for fast lookups.
        """
        self._graph: KnowledgeGraph = graph
        self._indexer: GraphIndexer = indexer

    def breadth_first_search(self, start_id: str) -> list[GraphNode]:
        """
        Performs an iterative Breadth-First Search (BFS) starting from the specified entity ID.

        Complexity:
            Time: O(V + E), Space: O(V)

        Args:
            start_id (str): Starting entity identifier for BFS.

        Returns:
            list[GraphNode]: Nodes in BFS traversal order.

        Raises:
            TraversalNodeNotFoundError: If start_id is missing from the index.
        """
        try:
            start_node = self._indexer.get_node_by_id(start_id)
        except GraphNodeNotFoundError as err:
            raise TraversalNodeNotFoundError(
                f"BFS traversal failed: Start entity ID '{start_id}' not found in graph index."
            ) from err

        visited: set[str] = {start_id}
        traversal_order: list[GraphNode] = []
        queue: deque[GraphNode] = deque([start_node])

        while queue:
            current_node = queue.popleft()
            traversal_order.append(current_node)

            for edge in current_node.outgoing_edges:
                target_id = edge.target_id
                if target_id not in visited and self._graph.has_entity(target_id):
                    visited.add(target_id)
                    queue.append(self._indexer.get_node_by_id(target_id))

        return traversal_order

    def depth_first_search(self, start_id: str) -> list[GraphNode]:
        """
        Performs an iterative Depth-First Search (DFS) starting from the specified entity ID.

        Complexity:
            Time: O(V + E), Space: O(V)

        Args:
            start_id (str): Starting entity identifier for DFS.

        Returns:
            list[GraphNode]: Nodes in DFS traversal order.

        Raises:
            TraversalNodeNotFoundError: If start_id is missing from the index.
        """
        try:
            start_node = self._indexer.get_node_by_id(start_id)
        except GraphNodeNotFoundError as err:
            raise TraversalNodeNotFoundError(
                f"DFS traversal failed: Start entity ID '{start_id}' not found in graph index."
            ) from err

        visited: set[str] = set()
        traversal_order: list[GraphNode] = []
        stack: list[GraphNode] = [start_node]

        while stack:
            current_node = stack.pop()
            node_id = current_node.id()

            if node_id not in visited:
                visited.add(node_id)
                traversal_order.append(current_node)

                # Push outgoing edges in reverse order so leftmost edges are visited first
                for edge in reversed(current_node.outgoing_edges):
                    target_id = edge.target_id
                    if target_id not in visited and self._graph.has_entity(target_id):
                        stack.append(self._indexer.get_node_by_id(target_id))

        return traversal_order

    def neighbors(self, entity_id: str) -> list[GraphNode]:
        """
        Retrieves directly adjacent (1-hop) neighbor GraphNodes using GraphIndexer.

        Complexity:
            Time: O(1) average, Space: O(k) where k is degree.

        Args:
            entity_id (str): Entity identifier.

        Returns:
            list[GraphNode]: List of adjacent neighbor graph nodes.

        Raises:
            TraversalNodeNotFoundError: If entity_id is missing from the index.
        """
        try:
            return self._indexer.get_neighbors(entity_id)
        except GraphNodeNotFoundError as err:
            raise TraversalNodeNotFoundError(
                f"Neighbor lookup failed: Entity ID '{entity_id}' not found in graph index."
            ) from err

    def reachable_nodes(self, start_id: str) -> set[GraphNode]:
        """
        Discovers all nodes reachable from the starting entity ID using BFS traversal.

        Complexity:
            Time: O(V + E), Space: O(V)

        Args:
            start_id (str): Starting entity identifier.

        Returns:
            set[GraphNode]: Set of all reachable graph nodes (including start_node).

        Raises:
            TraversalNodeNotFoundError: If start_id is missing from the index.
        """
        traversal_order = self.breadth_first_search(start_id)
        return set(traversal_order)

    def path_exists(self, source_id: str, target_id: str) -> bool:
        """
        Determines whether any directed path exists from source_id to target_id.

        Complexity:
            Time: O(V + E), Space: O(V)

        Args:
            source_id (str): Origin entity identifier.
            target_id (str): Destination entity identifier.

        Returns:
            bool: True if a directed path exists; False otherwise.

        Raises:
            TraversalNodeNotFoundError: If source_id or target_id is missing from the index.
        """
        if not self._graph.has_entity(source_id):
            raise TraversalNodeNotFoundError(
                f"Path check failed: Source entity ID '{source_id}' not found in graph index."
            )

        if not self._graph.has_entity(target_id):
            raise TraversalNodeNotFoundError(
                f"Path check failed: Target entity ID '{target_id}' not found in graph index."
            )

        if source_id == target_id:
            return True

        visited: set[str] = {source_id}
        queue: deque[str] = deque([source_id])

        while queue:
            current_id = queue.popleft()
            current_node = self._indexer.get_node_by_id(current_id)

            for edge in current_node.outgoing_edges:
                next_id = edge.target_id
                if next_id == target_id:
                    return True
                if next_id not in visited and self._graph.has_entity(next_id):
                    visited.add(next_id)
                    queue.append(next_id)

        return False
