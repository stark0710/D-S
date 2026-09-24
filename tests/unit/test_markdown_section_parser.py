"""
Unit tests for MarkdownSectionParser.
"""

from pathlib import Path
import pytest
from backend.knowledge.parser.markdown_section_parser import MarkdownSectionParser
from backend.models.markdown_section import MarkdownSection


def test_basic_heading_parsing_and_hierarchy():
    """Verify parsing of ATX headings and parent-child hierarchy building."""
    markdown_content = """---
id: EP-001
---

# Aircraft

Aircraft overview content.

## Wing

Wing description.

### Airfoil

NACA 2412 specs.

## Tail

Tail description.
"""
    parser = MarkdownSectionParser()
    sections = parser.parse(markdown_content)

    assert len(sections) == 4

    # Map by title for easy assertions
    sec_map = {s.title: s for s in sections}

    aircraft = sec_map["Aircraft"]
    wing = sec_map["Wing"]
    airfoil = sec_map["Airfoil"]
    tail = sec_map["Tail"]

    # Assert Aircraft section
    assert aircraft.heading_level == 1
    assert aircraft.parent_title is None
    assert aircraft.content == "Aircraft overview content."
    assert aircraft.children == [wing, tail]

    # Assert Wing section
    assert wing.heading_level == 2
    assert wing.parent_title == "Aircraft"
    assert wing.content == "Wing description."
    assert wing.children == [airfoil]

    # Assert Airfoil section
    assert airfoil.heading_level == 3
    assert airfoil.parent_title == "Wing"
    assert airfoil.content == "NACA 2412 specs."
    assert airfoil.children == []

    # Assert Tail section
    assert tail.heading_level == 2
    assert tail.parent_title == "Aircraft"
    assert tail.content == "Tail description."
    assert tail.children == []


def test_document_without_headings():
    """Verify synthetic heading_level=0 section for documents without headings."""
    markdown_content = "Just plain body text without any ATX headings."
    parser = MarkdownSectionParser()
    sections = parser.parse(markdown_content)

    assert len(sections) == 1
    sec = sections[0]
    assert sec.heading_level == 0
    assert sec.title == "Document"
    assert sec.content == "Just plain body text without any ATX headings."
    assert sec.parent_title is None
    assert sec.children == []


def test_empty_markdown():
    """Verify handling of empty markdown text."""
    parser = MarkdownSectionParser()
    sections = parser.parse("")

    assert len(sections) == 1
    assert sections[0].heading_level == 0
    assert sections[0].title == "Document"
    assert sections[0].content == ""


def test_consecutive_headings():
    """Verify section with no body content between headings."""
    markdown_content = """# Main Title
## Subtitle
Some content here.
"""
    parser = MarkdownSectionParser()
    sections = parser.parse(markdown_content)

    assert len(sections) == 2
    main_sec = sections[0]
    sub_sec = sections[1]

    assert main_sec.title == "Main Title"
    assert main_sec.content == ""
    assert main_sec.children == [sub_sec]

    assert sub_sec.title == "Subtitle"
    assert sub_sec.content == "Some content here."
