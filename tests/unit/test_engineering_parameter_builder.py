"""
Unit tests for EngineeringParameterBuilder.
"""

from pathlib import Path
import pytest
from backend.knowledge.builders.entity_builder import EntityBuilder
from backend.knowledge.builders.engineering_parameter_builder import (
    EngineeringParameterBuilder,
    MissingRequiredMetadataError,
)
from backend.models.repository_document import RepositoryDocument
from backend.models.parsed_document import ParsedDocument
from backend.models.engineering_parameter import EngineeringParameter


def test_engineering_parameter_builder_inheritance():
    """Verify EngineeringParameterBuilder inherits from EntityBuilder."""
    builder = EngineeringParameterBuilder()
    assert isinstance(builder, EntityBuilder)


def test_build_engineering_parameter_success():
    """Verify successful building of EngineeringParameter from metadata."""
    repo_doc = RepositoryDocument(
        path=Path("/repo/EP-001-001.md"),
        relative_path=Path("EP-001-001.md"),
        file_name="EP-001-001.md",
        document_type="engineering_parameter"
    )

    metadata = {
        "id": "EP-001-001",
        "name": "Payload Weight",
        "description": "Mass of cargo.",
        "library": "EPL-001",
        "parameter_group": "Requirements",
        "engineering_classification": "Operational",
        "unit": "kg",
        "data_type": "Float",
        "default_value": "5.0",
        "allowed_values": [1.0, 5.0, 10.0],
        "reference_ids": ["REF-001"]
    }

    parsed_doc = ParsedDocument(repository_document=repo_doc, metadata=metadata)
    builder = EngineeringParameterBuilder()
    param = builder.build(parsed_doc)

    assert isinstance(param, EngineeringParameter)
    assert param.id == "EP-001-001"
    assert param.name == "Payload Weight"
    assert param.description == "Mass of cargo."
    assert param.library == "EPL-001"
    assert param.parameter_group == "Requirements"
    assert param.engineering_classification == "Operational"
    assert param.unit == "kg"
    assert param.data_type == "Float"
    assert param.default_value == "5.0"
    assert param.allowed_values == ["1.0", "5.0", "10.0"]
    assert param.reference_ids == ["REF-001"]


def test_build_engineering_parameter_defaults():
    """Verify optional fields fallback to model defaults if omitted."""
    repo_doc = RepositoryDocument(
        path=Path("/repo/EP-001-002.md"),
        relative_path=Path("EP-001-002.md"),
        file_name="EP-001-002.md",
        document_type="engineering_parameter"
    )

    metadata = {
        "id": "EP-001-002",
        "name": "Cruise Speed"
    }

    parsed_doc = ParsedDocument(repository_document=repo_doc, metadata=metadata)
    builder = EngineeringParameterBuilder()
    param = builder.build(parsed_doc)

    assert param.id == "EP-001-002"
    assert param.name == "Cruise Speed"
    assert param.unit is None
    assert param.data_type is None
    assert param.allowed_values == []
    assert param.reference_ids == []


def test_missing_id_raises_exception():
    """Verify MissingRequiredMetadataError is raised if id cannot be determined."""
    repo_doc = RepositoryDocument(
        path=Path("/repo/invalid.md"),
        relative_path=Path("invalid.md"),
        file_name="",
        document_type="engineering_parameter"
    )
    parsed_doc = ParsedDocument(repository_document=repo_doc, metadata={"name": "No ID Param"})
    builder = EngineeringParameterBuilder()

    with pytest.raises(MissingRequiredMetadataError):
        builder.build(parsed_doc)


def test_missing_name_raises_exception():
    """Verify MissingRequiredMetadataError is raised if name cannot be determined."""
    repo_doc = RepositoryDocument(
        path=Path("/repo/invalid.md"),
        relative_path=Path("invalid.md"),
        file_name="",
        document_type="engineering_parameter"
    )
    parsed_doc = ParsedDocument(repository_document=repo_doc, metadata={"id": "EP-001"})
    builder = EngineeringParameterBuilder()

    with pytest.raises(MissingRequiredMetadataError):
        builder.build(parsed_doc)
