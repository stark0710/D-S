"""
Unit tests for GraphNode domain data structure.
"""

import pytest
from backend.models.knowledge_entity import KnowledgeEntity
from backend.models.engineering_parameter import EngineeringParameter
from backend.knowledge.graph.graph_edge import GraphEdge
from backend.knowledge.graph.graph_node import GraphNode


def test_graph_node_instantiation_and_helpers():
    """Verify GraphNode wraps KnowledgeEntity and provides correct helper properties."""
    param = EngineeringParameter(
        id="EP-001",
        name="Payload Weight",
        description="Cargo mass",
        library="EPL-001",
        parameter_group="Mission",
        engineering_classification="Operational"
    )

    node = GraphNode(entity=param)

    assert node.id() == "EP-001"
    assert node.entity_type() == EngineeringParameter
    assert node.degree() == 0
    assert node.incoming_edges == []
    assert node.outgoing_edges == []
    assert node.labels == set()
    assert node.properties == {}


def test_edge_addition_and_degree():
    """Verify adding incoming and outgoing edges updates degree correctly."""
    param = KnowledgeEntity(id="E-001", name="Test Entity", description="Desc")
    node = GraphNode(entity=param, labels={"EngineeringParameter"})

    edge1 = GraphEdge(source_id="E-000", target_id="E-001", relationship_type="requires")
    edge2 = GraphEdge(source_id="E-001", target_id="E-002", relationship_type="depends_on")

    node.add_incoming_edge(edge1)
    node.add_outgoing_edge(edge2)

    assert len(node.incoming_edges) == 1
    assert len(node.outgoing_edges) == 1
    assert node.degree() == 2
    assert "EngineeringParameter" in node.labels


def test_graph_node_slots():
    """Verify slots prevent arbitrary attribute assignment."""
    param = KnowledgeEntity(id="E-001", name="Test", description="Desc")
    node = GraphNode(entity=param)

    with pytest.raises(AttributeError):
        node.extra_field = "Invalid"
