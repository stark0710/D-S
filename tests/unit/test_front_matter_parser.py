"""
Unit tests for FrontMatterParser.
"""

import pytest
from backend.knowledge.parser.front_matter_parser import (
    FrontMatterParser,
    UnclosedFrontMatterError,
    MalformedYAMLError,
)


def test_valid_front_matter_parsing():
    """Verify FrontMatterParser extracts YAML front matter correctly."""
    markdown_content = """---
id: EP-001-001
name: Wing Span
unit: m
data_type: float
allowed_values:
  - 1.5
  - 2.0
---

# Wing Span

Body content...
"""
    parser = FrontMatterParser()
    metadata = parser.parse(markdown_content)

    assert metadata == {
        "id": "EP-001-001",
        "name": "Wing Span",
        "unit": "m",
        "data_type": "float",
        "allowed_values": [1.5, 2.0],
    }


def test_no_front_matter():
    """Verify empty dictionary returned when no front matter is present."""
    markdown_content = """# Document Title

This is a markdown document with no front matter.
"""
    parser = FrontMatterParser()
    metadata = parser.parse(markdown_content)

    assert metadata == {}


def test_empty_front_matter_block():
    """Verify empty dictionary returned when front matter is empty."""
    markdown_content = """---
---

# Document Title
"""
    parser = FrontMatterParser()
    metadata = parser.parse(markdown_content)

    assert metadata == {}


def test_unclosed_front_matter_error():
    """Verify UnclosedFrontMatterError is raised when closing '---' is missing."""
    markdown_content = """---
id: EP-001
name: Test Parameter

# Unclosed Heading
Body text
"""
    parser = FrontMatterParser()

    with pytest.raises(UnclosedFrontMatterError):
        parser.parse(markdown_content)


def test_malformed_yaml_error():
    """Verify MalformedYAMLError is raised for syntax errors in YAML."""
    markdown_content = """---
id: EP-001
name: : Invalid YAML Syntax [
---

# Heading
"""
    parser = FrontMatterParser()

    with pytest.raises(MalformedYAMLError):
        parser.parse(markdown_content)


def test_non_dict_yaml_front_matter_error():
    """Verify MalformedYAMLError is raised if front matter parses to non-dict (e.g. list)."""
    markdown_content = """---
- item1
- item2
---

# Heading
"""
    parser = FrontMatterParser()

    with pytest.raises(MalformedYAMLError):
        parser.parse(markdown_content)
