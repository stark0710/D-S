"""
Unit tests for ParsedDocument domain model.
"""

from pathlib import Path
import pytest
from backend.models.repository_document import RepositoryDocument
from backend.models.parsed_document import ParsedDocument


def test_parsed_document_instantiation():
    """Verify ParsedDocument initializes correctly with fields."""
    repo_doc = RepositoryDocument(
        path=Path("/repo/EP-001.md"),
        relative_path=Path("EP-001.md"),
        file_name="EP-001.md",
        document_type="engineering_parameter"
    )

    metadata = {"id": "EP-001", "name": "Wing Span"}
    sections = []
    raw_md = "# Wing Span\nContent..."

    parsed_doc = ParsedDocument(
        repository_document=repo_doc,
        metadata=metadata,
        sections=sections,
        raw_markdown=raw_md
    )

    assert parsed_doc.repository_document == repo_doc
    assert parsed_doc.metadata == metadata
    assert parsed_doc.sections == sections
    assert parsed_doc.raw_markdown == raw_md


def test_parsed_document_defaults():
    """Verify default values for metadata, sections, and raw_markdown."""
    repo_doc = RepositoryDocument(
        path=Path("/repo/MD-001.md"),
        relative_path=Path("MD-001.md"),
        file_name="MD-001.md",
        document_type="mission_domain"
    )

    parsed_doc = ParsedDocument(repository_document=repo_doc)

    assert parsed_doc.metadata == {}
    assert parsed_doc.sections == []
    assert parsed_doc.raw_markdown == ""


def test_parsed_document_slots():
    """Verify slots prevent arbitrary attribute assignment."""
    repo_doc = RepositoryDocument(
        path=Path("/repo/test.md"),
        relative_path=Path("test.md"),
        file_name="test.md",
        document_type="test"
    )
    parsed_doc = ParsedDocument(repository_document=repo_doc)

    with pytest.raises(AttributeError):
        parsed_doc.extra_field = "Invalid"
