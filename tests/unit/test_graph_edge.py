"""
Unit tests for GraphEdge data structure.
"""

import pytest
from backend.knowledge.graph.graph_edge import GraphEdge


def test_graph_edge_instantiation():
    """Verify GraphEdge initializes correctly with all attributes."""
    edge = GraphEdge(
        source_id="MD-001",
        target_id="MC-001-01",
        relationship_type="contains",
        metadata={"weight": 1.0, "origin_document": "MD-001.md"}
    )

    assert edge.source_id == "MD-001"
    assert edge.target_id == "MC-001-01"
    assert edge.relationship_type == "contains"
    assert edge.metadata == {"weight": 1.0, "origin_document": "MD-001.md"}


def test_graph_edge_defaults():
    """Verify default values for metadata attribute."""
    edge = GraphEdge(
        source_id="EP-001",
        target_id="EP-002",
        relationship_type="depends_on"
    )

    assert edge.source_id == "EP-001"
    assert edge.target_id == "EP-002"
    assert edge.relationship_type == "depends_on"
    assert edge.metadata == {}


def test_graph_edge_slots():
    """Verify slots prevent arbitrary attribute assignment."""
    edge = GraphEdge(
        source_id="N1",
        target_id="N2",
        relationship_type="uses"
    )

    with pytest.raises(AttributeError):
        edge.extra_attr = "Invalid"
