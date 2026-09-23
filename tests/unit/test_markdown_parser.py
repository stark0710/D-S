"""
Unit tests for MarkdownParser.
"""

from pathlib import Path
import pytest
from backend.knowledge.parser.parser import Parser
from backend.knowledge.parser.markdown_parser import MarkdownParser, UnsupportedDocumentTypeError
from backend.models.repository_document import RepositoryDocument
from backend.models.knowledge_entity import KnowledgeEntity
from backend.models.engineering_parameter import EngineeringParameter
from backend.models.mission_domain import MissionDomain
from backend.models.mission_category import MissionCategory


def test_markdown_parser_inheritance():
    """Verify MarkdownParser inherits from Parser abstract base class."""
    parser = MarkdownParser()
    assert isinstance(parser, Parser)


def test_parse_engineering_parameter_dispatch():
    """Verify dispatching engineering_parameter document type."""
    doc = RepositoryDocument(
        path=Path("/repo/EP-001.md"),
        relative_path=Path("EP-001.md"),
        file_name="EP-001.md",
        document_type="engineering_parameter"
    )
    parser = MarkdownParser()
    entity = parser.parse(doc)

    assert isinstance(entity, EngineeringParameter)
    assert isinstance(entity, KnowledgeEntity)
    assert entity.id == "EP-001"


def test_parse_mission_domain_dispatch():
    """Verify dispatching mission_domain document type."""
    doc = RepositoryDocument(
        path=Path("/repo/MD-001.md"),
        relative_path=Path("MD-001.md"),
        file_name="MD-001.md",
        document_type="mission_domain"
    )
    parser = MarkdownParser()
    entity = parser.parse(doc)

    assert isinstance(entity, MissionDomain)
    assert entity.id == "MD-001"


def test_parse_mission_category_dispatch():
    """Verify dispatching mission_category document type."""
    doc = RepositoryDocument(
        path=Path("/repo/MC-001.md"),
        relative_path=Path("MC-001.md"),
        file_name="MC-001.md",
        document_type="mission_category"
    )
    parser = MarkdownParser()
    entity = parser.parse(doc)

    assert isinstance(entity, MissionCategory)
    assert entity.id == "MC-001"


def test_parse_readme_dispatch():
    """Verify dispatching readme document type."""
    doc = RepositoryDocument(
        path=Path("/repo/README.md"),
        relative_path=Path("README.md"),
        file_name="README.md",
        document_type="readme"
    )
    parser = MarkdownParser()
    entity = parser.parse(doc)

    assert isinstance(entity, KnowledgeEntity)
    assert entity.id == "README"


def test_parse_unsupported_document_type_raises():
    """Verify unsupported document_type raises UnsupportedDocumentTypeError."""
    doc = RepositoryDocument(
        path=Path("/repo/invalid.xyz"),
        relative_path=Path("invalid.xyz"),
        file_name="invalid.xyz",
        document_type="unknown"
    )
    parser = MarkdownParser()

    with pytest.raises(UnsupportedDocumentTypeError):
        parser.parse(doc)
