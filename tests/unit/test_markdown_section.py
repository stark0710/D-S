"""
Unit tests for MarkdownSection domain model.
"""

import pytest
from backend.models.markdown_section import MarkdownSection


def test_markdown_section_instantiation():
    """Verify MarkdownSection initializes correctly with all fields."""
    child = MarkdownSection(
        heading_level=2,
        title="Span",
        content="Wing span is 12 meters.",
        parent_title="Wing Geometry"
    )

    parent = MarkdownSection(
        heading_level=1,
        title="Wing Geometry",
        content="Overview of wing geometry.",
        parent_title=None,
        children=[child]
    )

    assert parent.heading_level == 1
    assert parent.title == "Wing Geometry"
    assert parent.content == "Overview of wing geometry."
    assert parent.parent_title is None
    assert len(parent.children) == 1

    assert child.heading_level == 2
    assert child.title == "Span"
    assert child.parent_title == "Wing Geometry"
    assert child.children == []


def test_markdown_section_defaults():
    """Verify default values for parent_title and children."""
    section = MarkdownSection(
        heading_level=1,
        title="Purpose",
        content="Document purpose description."
    )

    assert section.parent_title is None
    assert section.children == []


def test_markdown_section_slots():
    """Verify slots prevent arbitrary attribute assignment."""
    section = MarkdownSection(
        heading_level=1,
        title="Test",
        content="Test content"
    )

    with pytest.raises(AttributeError):
        section.extra_attribute = "Invalid"
